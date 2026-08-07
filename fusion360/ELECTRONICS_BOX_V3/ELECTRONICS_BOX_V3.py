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


def _find_occurrence(root, name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == name.upper():
            return occurrence
    return None


def _rectangle(sketch, width, depth):
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2.0, -depth / 2.0, 0),
        adsk.core.Point3D.create(width / 2.0, depth / 2.0, 0)
    )


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


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
        if _find_occurrence(root, 'ELECTRONICS_BOX_V3'):
            raise RuntimeError(
                'ELECTRONICS_BOX_V3 already exists; non-destructive mode made no changes.'
            )
        float_occurrence = _find_occurrence(root, 'MAIN_FLOAT')
        if not float_occurrence:
            raise RuntimeError('MAIN_FLOAT component was not found.')
        float_body = float_occurrence.component.bRepBodies.itemByName('MAIN_FLOAT_HDPE_BODY')
        if not float_body:
            raise RuntimeError('MAIN_FLOAT_HDPE_BODY was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'ebox_v3_width', '500 mm', 'mm', 'Enclosure width')
        _add_parameter(parameters, 'ebox_v3_depth', '340 mm', 'mm', 'Enclosure depth')
        _add_parameter(parameters, 'ebox_v3_height', '350 mm', 'mm', 'Enclosure height')
        _add_parameter(parameters, 'ebox_v3_wall', '5 mm', 'mm', 'HDPE wall thickness')
        _add_parameter(parameters, 'ebox_v3_base', '6 mm', 'mm', 'Leak floor thickness')
        _add_parameter(parameters, 'ebox_v3_fan_x', '170 mm', 'mm', 'Hot-bay fan center X')
        _add_parameter(parameters, 'ebox_v3_fan_z', '120 mm', 'mm', 'Fan height above box floor')
        _add_parameter(parameters, 'ebox_v3_fan_opening', '76 mm', 'mm', 'Air opening diameter')
        _add_parameter(parameters, 'ebox_v3_fan_pitch', '71.5 mm', 'mm', '80 mm fan pitch')
        _add_parameter(parameters, 'ebox_v3_fan_hole', '4.5 mm', 'mm', 'M4 clearance')

        width = parameters.itemByName('ebox_v3_width').value
        depth = parameters.itemByName('ebox_v3_depth').value
        wall = parameters.itemByName('ebox_v3_wall').value
        fan_x = parameters.itemByName('ebox_v3_fan_x').value
        fan_offset_z = parameters.itemByName('ebox_v3_fan_z').value
        fan_radius = parameters.itemByName('ebox_v3_fan_opening').value / 2.0
        pitch = parameters.itemByName('ebox_v3_fan_pitch').value
        mount_radius = parameters.itemByName('ebox_v3_fan_hole').value / 2.0

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = 'ELECTRONICS_BOX_V3'
        extrudes = component.features.extrudeFeatures

        base_sketch = component.sketches.add(component.xYConstructionPlane)
        base_sketch.name = 'SKETCH_01_V3_BASE'
        _rectangle(base_sketch, width, depth)
        base_input = extrudes.createInput(
            base_sketch.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        base_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ebox_v3_base')),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        base_feature = extrudes.add(base_input)
        base_feature.name = 'EXTRUDE_01_V3_BASE'
        body = base_feature.bodies.item(0)
        body.name = 'ELECTRONICS_BOX_V3_HDPE_BODY'

        wall_sketch = component.sketches.add(component.xYConstructionPlane)
        wall_sketch.name = 'SKETCH_02_V3_WALL_RING'
        _rectangle(wall_sketch, width, depth)
        _rectangle(wall_sketch, width - 2.0 * wall, depth - 2.0 * wall)
        wall_profile = _profiles_by_area(wall_sketch)[0]
        wall_input = extrudes.createInput(
            wall_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        wall_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ebox_v3_height')),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        wall_feature = extrudes.add(wall_input)
        wall_feature.name = 'EXTRUDE_02_V3_JOINED_WALLS'

        body = component.bRepBodies.itemByName('ELECTRONICS_BOX_V3_HDPE_BODY')
        local_bottom_z = body.boundingBox.minPoint.z
        local_top_z = body.boundingBox.maxPoint.z
        fan_model_z = local_bottom_z + fan_offset_z

        port_sketch = component.sketches.add(component.xZConstructionPlane)
        port_sketch.name = 'SKETCH_03_V3_OPPOSED_FAN_PORTS'
        # Fusion XZ sketch Y maps to negative model Z.
        center = adsk.core.Point3D.create(fan_x, -fan_model_z, 0)
        circles = port_sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(center, fan_radius)
        half_pitch = pitch / 2.0
        for dx in (-half_pitch, half_pitch):
            for dz in (-half_pitch, half_pitch):
                circles.addByCenterRadius(
                    adsk.core.Point3D.create(fan_x + dx, -fan_model_z + dz, 0),
                    mount_radius
                )

        port_profiles = adsk.core.ObjectCollection.create()
        for index in range(port_sketch.profiles.count):
            port_profiles.add(port_sketch.profiles.item(index))
        port_input = extrudes.createInput(
            port_profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        port_input.participantBodies = [body]
        port_input.setTwoSidesExtent(
            adsk.fusion.ThroughAllExtentDefinition.create(),
            adsk.fusion.ThroughAllExtentDefinition.create()
        )
        port_feature = extrudes.add(port_input)
        port_feature.name = 'CUT_01_V3_NATIVE_INTAKE_EXHAUST'

        # Position the finished body using its actual orientation, so the box
        # floor is always 10 mm above the main-float interior bottom.
        desired_bottom_z = float_body.boundingBox.minPoint.z + 1.0
        position = adsk.core.Matrix3D.create()
        position.translation = adsk.core.Vector3D.create(
            0, 0, desired_bottom_z - local_bottom_z
        )
        occurrence.transform2 = position

        body = component.bRepBodies.itemByName('ELECTRONICS_BOX_V3_HDPE_BODY')
        assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-EB-003')
        component.attributes.add('PROJECT_FALCON_01', 'Revision', 'V3 joined shell')
        component.attributes.add('PROJECT_FALCON_01', 'Cooling', 'Native opposed fan ports')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign HDPE manually if unavailable locally.'
        ui.messageBox(
            'ELECTRONICS_BOX_V3 completed as one joined open-top box.\n\n'
            'Native intake and exhaust ports: 76 mm\n'
            'Fan pattern: 71.5 mm with M4 clearance\n'
            'V1 and V2 were not edited or deleted.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'ELECTRONICS_BOX_V3 generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )

