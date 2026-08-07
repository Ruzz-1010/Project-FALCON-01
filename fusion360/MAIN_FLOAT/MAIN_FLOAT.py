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


def _horizontal_planar_face(body, highest=True):
    candidates = []
    for face in body.faces:
        plane = adsk.core.Plane.cast(face.geometry)
        if not plane:
            continue
        success, outward_normal = face.evaluator.getNormalAtPoint(face.pointOnFace)
        if not success or abs(outward_normal.z) < 0.999:
            continue
        candidates.append((face, outward_normal.z))
    if not candidates:
        return None
    # A BRepFace evaluator always reports the normal pointing out of the solid.
    # Therefore +Z is the top cap and -Z is the bottom cap regardless of the
    # arbitrary orientation of the underlying Plane geometry.
    desired = [item for item in candidates if item[1] > 0.999] if highest else [
        item for item in candidates if item[1] < -0.999
    ]
    if len(desired) != 1:
        raise RuntimeError(
            'Could not uniquely identify the outward-facing top/bottom face.'
        )
    return desired[0][0]


def _assign_hdpe(app, body):
    candidate_names = (
        'High Density Polyethylene',
        'High-density polyethylene',
        'HDPE',
    )
    for library in app.materialLibraries:
        materials = library.materials
        for name in candidate_names:
            material = materials.itemByName(name)
            if material:
                body.material = material
                return True
    return False


def _get_or_create_main_float_component(design):
    root = design.rootComponent

    # Reuse the internal MAIN_FLOAT component already visible in the Browser.
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == 'MAIN_FLOAT':
            return occurrence.component

    # If it does not exist, create it inside the current design—not in a new file.
    occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = 'MAIN_FLOAT'
    return occurrence.component


def _remove_known_partial_result(component):
    if component.bRepBodies.count or component.sketches.count:
        raise RuntimeError('MAIN_FLOAT already exists; non-destructive mode made no changes.')


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError(
                'Open the PROJECT FALCON-01 Fusion design before running this script.'
            )

        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        component = _get_or_create_main_float_component(design)
        _remove_known_partial_result(component)
        if component.bRepBodies.count or component.sketches.count:
            raise RuntimeError(
                'MAIN_FLOAT already contains geometry. Nothing was changed. '
                'Use an empty MAIN_FLOAT component and run the script again.'
            )

        parameters = design.userParameters
        _add_parameter(parameters, 'float_OD', '650 mm', 'mm', 'Outside diameter')
        _add_parameter(parameters, 'float_height', '380 mm', 'mm', 'Overall height')
        _add_parameter(parameters, 'wall_thickness', '5 mm', 'mm', 'Nominal HDPE wall')
        _add_parameter(parameters, 'profile_radius', '45 mm', 'mm', 'Marine-profile edge radius')

        sketch = component.sketches.add(component.xYConstructionPlane)
        sketch.name = 'SKETCH_01_FLOAT_FOOTPRINT'
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 32.5
        )
        diameter_dimension = sketch.sketchDimensions.addDiameterDimension(
            circle, adsk.core.Point3D.create(36, 0, 0), True
        )
        diameter_dimension.parameter.expression = 'float_OD'

        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.fusion.DistanceExtentDefinition.create(_value('float_height'))
        extrude_input.setOneSideExtent(
            distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        extrude = extrudes.add(extrude_input)
        extrude.name = 'EXTRUDE_01_OVERALL_HEIGHT'
        body = extrude.bodies.item(0)
        body.name = 'MAIN_FLOAT_HDPE_BODY'

        circular_edges = adsk.core.ObjectCollection.create()
        for edge in body.edges:
            if adsk.core.Circle3D.cast(edge.geometry):
                circular_edges.add(edge)
        if circular_edges.count != 2:
            raise RuntimeError(
                'Expected two circular rim edges before the marine-profile fillet.'
            )

        fillets = component.features.filletFeatures
        fillet_input = fillets.createInput()
        fillet_input.isRollingBallCorner = True
        fillet_input.edgeSetInputs.addConstantRadiusEdgeSet(
            circular_edges, _value('profile_radius'), False
        )
        fillet = fillets.add(fillet_input)
        fillet.name = 'FILLET_01_MARINE_PROFILE'

        # Create a deterministic open-top cavity instead of relying on Shell's
        # face-removal interpretation. Fusion API point lengths are centimeters.
        od = parameters.itemByName('float_OD').value
        height = parameters.itemByName('float_height').value
        wall = parameters.itemByName('wall_thickness').value
        radius = parameters.itemByName('profile_radius').value
        outer_radius = od / 2.0
        inner_radius = outer_radius - wall
        opening_radius = outer_radius - radius - wall

        body = component.bRepBodies.itemByName('MAIN_FLOAT_HDPE_BODY')
        body_box = body.boundingBox
        bottom_z = body_box.minPoint.z
        top_z = body_box.maxPoint.z
        cavity_bottom_z = bottom_z + wall
        shoulder_z = top_z - radius

        # On Fusion's XZ sketch plane, sketch Y maps to negative model Z.
        cavity_bottom_y = -cavity_bottom_z
        shoulder_y = -shoulder_z
        top_y = -top_z

        cavity_sketch = component.sketches.add(component.xZConstructionPlane)
        cavity_sketch.name = 'SKETCH_02_INNER_CAVITY'
        lines = cavity_sketch.sketchCurves.sketchLines
        arcs = cavity_sketch.sketchCurves.sketchArcs

        axis_line = lines.addByTwoPoints(
            adsk.core.Point3D.create(0, cavity_bottom_y, 0),
            adsk.core.Point3D.create(0, top_y, 0)
        )
        inner_arc = arcs.addByCenterStartSweep(
            adsk.core.Point3D.create(opening_radius, shoulder_y, 0),
            adsk.core.Point3D.create(inner_radius, shoulder_y, 0),
            -1.5707963267948966
        )
        lines.addByTwoPoints(axis_line.endSketchPoint, inner_arc.endSketchPoint)
        lines.addByTwoPoints(
            inner_arc.startSketchPoint,
            adsk.core.Point3D.create(inner_radius, cavity_bottom_y, 0)
        )
        lines.addByTwoPoints(
            adsk.core.Point3D.create(inner_radius, cavity_bottom_y, 0),
            axis_line.startSketchPoint
        )
        cavity_profile = cavity_sketch.profiles.item(0)
        revolves = component.features.revolveFeatures
        revolve_input = revolves.createInput(
            cavity_profile,
            axis_line,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        revolve_input.setAngleExtent(False, _value('360 deg'))
        revolve = revolves.add(revolve_input)
        revolve.name = 'REVOLVE_01_INNER_CAVITY'

        body = component.bRepBodies.itemByName('MAIN_FLOAT_HDPE_BODY')
        hdpe_assigned = _assign_hdpe(app, body)
        design.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-MF-001')
        design.attributes.add('PROJECT_FALCON_01', 'Material', 'HDPE')
        design.attributes.add('PROJECT_FALCON_01', 'Description',
                              'Parametric marine observation buoy main float')

        app.activeViewport.fit()
        material_note = '' if hdpe_assigned else (
            '\n\nHDPE metadata was added, but your local Fusion material library '
            'does not contain a matching HDPE name. Physical material can be '
            'assigned after the geometry check.'
        )
        ui.messageBox(
            'MAIN_FLOAT completed.\n\n'
            'OD: 650 mm\nHeight: 380 mm\nWall: 5 mm\n'
            'Profile radius: 45 mm\nTop: open\nBottom: closed\n'
            'Cavity: controlled revolve\n\n'
            'The model was created inside the current active design.\n'
            'Save PROJECT FALCON-01 after inspection.' + material_note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'MAIN_FLOAT generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
