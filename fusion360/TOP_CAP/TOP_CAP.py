import adsk.core
import adsk.fusion
import traceback


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _find_component_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _remove_known_partial_result(component):
    if component.bRepBodies.count or component.sketches.count:
        raise RuntimeError('TOP_CAP already exists; non-destructive mode made no changes.')


def _closed_polyline(sketch, points):
    lines = sketch.sketchCurves.sketchLines
    created = []
    for index in range(len(points)):
        start = points[index]
        end = points[(index + 1) % len(points)]
        created.append(lines.addByTwoPoints(start, end))
    return created


def _assign_hdpe(app, body):
    for library in app.materialLibraries:
        for name in ('High Density Polyethylene', 'High-density polyethylene', 'HDPE'):
            material = library.materials.itemByName(name)
            if material:
                body.material = material
                return True
    return False


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Open PROJECT FALCON-01 before running this script.')

        root = design.rootComponent
        float_occurrence = _find_component_occurrence(root, 'MAIN_FLOAT')
        if not float_occurrence:
            raise RuntimeError('MAIN_FLOAT component was not found in the active design.')
        float_body = float_occurrence.component.bRepBodies.itemByName('MAIN_FLOAT_HDPE_BODY')
        if not float_body:
            raise RuntimeError('MAIN_FLOAT_HDPE_BODY was not found.')

        float_top_z = float_body.boundingBox.maxPoint.z

        cap_occurrence = _find_component_occurrence(root, 'TOP_CAP')
        if not cap_occurrence:
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, float_top_z)
            cap_occurrence = root.occurrences.addNewComponent(transform)
            cap_occurrence.component.name = 'TOP_CAP'
        component = cap_occurrence.component

        _remove_known_partial_result(component)
        if component.bRepBodies.count or component.sketches.count:
            raise RuntimeError(
                'TOP_CAP contains unknown geometry. Nothing was overwritten.'
            )

        parameters = design.userParameters
        _add_parameter(parameters, 'cap_OD', '650 mm', 'mm', 'Full-width top cover outside diameter')
        parameters.itemByName('cap_OD').expression = '650 mm'
        _add_parameter(parameters, 'cap_thickness', '12 mm', 'mm', 'Top plate thickness')
        _add_parameter(parameters, 'cap_skirt_OD', '548 mm', 'mm', 'Locating skirt outside diameter')
        _add_parameter(parameters, 'cap_skirt_wall', '5 mm', 'mm', 'Locating skirt wall')
        _add_parameter(parameters, 'cap_skirt_depth', '20 mm', 'mm', 'Skirt insertion depth')
        _add_parameter(parameters, 'cap_drip_lip_wall', '5 mm', 'mm', 'Outer drip lip wall')
        _add_parameter(parameters, 'cap_drip_lip_depth', '15 mm', 'mm', 'Outer drip lip depth')
        _add_parameter(parameters, 'gasket_groove_width', '4 mm', 'mm', 'Radial O-ring groove width')
        _add_parameter(parameters, 'gasket_groove_depth', '2 mm', 'mm', 'Radial O-ring groove depth')
        _add_parameter(parameters, 'cap_edge_radius', '3 mm', 'mm', 'Cover edge radius')

        cap_radius = parameters.itemByName('cap_OD').value / 2.0
        cap_thickness = parameters.itemByName('cap_thickness').value
        skirt_outer = parameters.itemByName('cap_skirt_OD').value / 2.0
        skirt_wall = parameters.itemByName('cap_skirt_wall').value
        skirt_inner = skirt_outer - skirt_wall
        skirt_depth = parameters.itemByName('cap_skirt_depth').value
        drip_wall = parameters.itemByName('cap_drip_lip_wall').value
        drip_depth = parameters.itemByName('cap_drip_lip_depth').value
        drip_inner = cap_radius - drip_wall
        groove_width = parameters.itemByName('gasket_groove_width').value
        groove_depth = parameters.itemByName('gasket_groove_depth').value

        profile_sketch = component.sketches.add(component.xZConstructionPlane)
        profile_sketch.name = 'SKETCH_01_CAP_PROFILE'

        # Model Z maps to negative sketch Y on Fusion's XZ sketch plane.
        profile_points = [
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(skirt_inner, 0, 0),
            adsk.core.Point3D.create(skirt_inner, skirt_depth, 0),
            adsk.core.Point3D.create(skirt_outer, skirt_depth, 0),
            adsk.core.Point3D.create(skirt_outer, 0, 0),
            adsk.core.Point3D.create(drip_inner, 0, 0),
            adsk.core.Point3D.create(drip_inner, drip_depth, 0),
            adsk.core.Point3D.create(cap_radius, drip_depth, 0),
            adsk.core.Point3D.create(cap_radius, 0, 0),
            adsk.core.Point3D.create(cap_radius, -cap_thickness, 0),
            adsk.core.Point3D.create(0, -cap_thickness, 0),
        ]
        profile_lines = _closed_polyline(profile_sketch, profile_points)

        revolves = component.features.revolveFeatures
        revolve_input = revolves.createInput(
            profile_sketch.profiles.item(0),
            component.zConstructionAxis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        revolve_input.setAngleExtent(False, _value('360 deg'))
        revolve = revolves.add(revolve_input)
        revolve.name = 'REVOLVE_01_CAP_AND_SKIRT'
        body = revolve.bodies.item(0)
        body.name = 'TOP_CAP_HDPE_BODY'

        matching_edges = []
        for edge in body.edges:
            circle = adsk.core.Circle3D.cast(edge.geometry)
            if circle and abs(circle.radius - cap_radius) < 0.001:
                matching_edges.append((circle.center.z, edge))
        if len(matching_edges) < 2:
            raise RuntimeError('The outer cap edges could not be identified.')
        matching_edges.sort(key=lambda item: item[0])
        cap_edges = adsk.core.ObjectCollection.create()
        cap_edges.add(matching_edges[0][1])
        cap_edges.add(matching_edges[-1][1])
        fillets = component.features.filletFeatures
        fillet_input = fillets.createInput()
        fillet_input.edgeSetInputs.addConstantRadiusEdgeSet(
            cap_edges, _value('cap_edge_radius'), False
        )
        fillet = fillets.add(fillet_input)
        fillet.name = 'FILLET_01_CAP_EDGES'

        # Cut a circumferential radial gasket groove into the skirt exterior.
        groove_sketch = component.sketches.add(component.xZConstructionPlane)
        groove_sketch.name = 'SKETCH_02_GASKET_GROOVE'
        groove_top = skirt_depth * 0.35
        groove_bottom = groove_top + groove_width
        groove_points = [
            adsk.core.Point3D.create(skirt_outer - groove_depth, groove_top, 0),
            adsk.core.Point3D.create(skirt_outer, groove_top, 0),
            adsk.core.Point3D.create(skirt_outer, groove_bottom, 0),
            adsk.core.Point3D.create(skirt_outer - groove_depth, groove_bottom, 0),
        ]
        groove_lines = _closed_polyline(groove_sketch, groove_points)
        groove_input = revolves.createInput(
            groove_sketch.profiles.item(0),
            component.zConstructionAxis,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        groove_input.setAngleExtent(False, _value('360 deg'))
        groove = revolves.add(groove_input)
        groove.name = 'REVOLVE_02_GASKET_GROOVE'

        body = component.bRepBodies.itemByName('TOP_CAP_HDPE_BODY')
        hdpe_assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-TC-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', 'HDPE')
        component.attributes.add('PROJECT_FALCON_01', 'Seal', 'Radial elastomer O-ring')

        app.activeViewport.fit()
        note = '' if hdpe_assigned else (
            '\nHDPE metadata was applied; assign the physical HDPE material manually '
            'if it is missing from the local material library.'
        )
        ui.messageBox(
            'TOP_CAP completed as a separate removable component.\n\n'
            'OD: 650 mm\nPlate: 12 mm\nSkirt OD: 548 mm\n'
            'Skirt depth: 20 mm\nOuter drip lip: 5 x 15 mm\n'
            'Radial gasket groove: 4 x 2 mm\n\n'
            'The cap is not joined to MAIN_FLOAT and can be animated.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'TOP_CAP generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
