import adsk.core
import adsk.fusion
import math
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


def _rectangle(sketch, size):
    half = size / 2.0
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-half, -half, 0),
        adsk.core.Point3D.create(half, half, 0)
    )


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _assign_material(app, body):
    for library in app.materialLibraries:
        for name in ('ABS Plastic', 'ABS', 'Plastic'):
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
        if _find_occurrence(root, 'EXHAUST_FAN_MODULE'):
            raise RuntimeError(
                'EXHAUST_FAN_MODULE already exists; non-destructive mode made no changes.'
            )
        box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX_V3')
        if not box_occurrence:
            raise RuntimeError('ELECTRONICS_BOX_V3 component was not found.')
        box_body = box_occurrence.component.bRepBodies.itemByName(
            'ELECTRONICS_BOX_V3_HDPE_BODY'
        )
        if not box_body:
            raise RuntimeError('ELECTRONICS_BOX_V3_HDPE_BODY was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'exhaust_fan_size', '80 mm', 'mm', 'Nominal PWM fan size')
        _add_parameter(parameters, 'exhaust_opening', '76 mm', 'mm', 'Free-air opening diameter')
        _add_parameter(parameters, 'exhaust_mount_pitch', '71.5 mm', 'mm', 'Standard fan pitch')
        _add_parameter(parameters, 'exhaust_mount_hole', '4.5 mm', 'mm', 'M4 clearance')
        _add_parameter(parameters, 'exhaust_frame_size', '100 mm', 'mm', 'Bracket outside size')
        _add_parameter(parameters, 'exhaust_frame_thickness', '4 mm', 'mm', 'Bracket thickness')
        _add_parameter(parameters, 'exhaust_collar_depth', '45 mm', 'mm', 'Hot-air collar depth')

        opening_radius = parameters.itemByName('exhaust_opening').value / 2.0
        pitch = parameters.itemByName('exhaust_mount_pitch').value
        mount_radius = parameters.itemByName('exhaust_mount_hole').value / 2.0
        frame_size = parameters.itemByName('exhaust_frame_size').value
        half_pitch = pitch / 2.0

        local_bottom_z = box_body.boundingBox.minPoint.z
        global_fan_z = (
            box_occurrence.transform2.translation.z + local_bottom_z + 12.0
        )
        transform = adsk.core.Matrix3D.create()
        transform.setToRotation(
            -math.pi / 2.0,
            adsk.core.Vector3D.create(1, 0, 0),
            adsk.core.Point3D.create(0, 0, 0)
        )
        transform.translation = adsk.core.Vector3D.create(17.0, 17.0, global_fan_z)
        occurrence = root.occurrences.addNewComponent(transform)
        component = occurrence.component
        component.name = 'EXHAUST_FAN_MODULE'

        frame_sketch = component.sketches.add(component.xYConstructionPlane)
        frame_sketch.name = 'SKETCH_01_EXHAUST_FRAME'
        _rectangle(frame_sketch, frame_size)
        circles = frame_sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), opening_radius)
        for x in (-half_pitch, half_pitch):
            for y in (-half_pitch, half_pitch):
                circles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), mount_radius)

        frame_profile = _profiles_by_area(frame_sketch)[-1]
        extrudes = component.features.extrudeFeatures
        frame_input = extrudes.createInput(
            frame_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        frame_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                _value('exhaust_frame_thickness')
            ),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        frame_feature = extrudes.add(frame_input)
        frame_feature.name = 'EXTRUDE_01_EXHAUST_FRAME'
        body = frame_feature.bodies.item(0)
        body.name = 'EXHAUST_FAN_BRACKET_BODY'

        collar_sketch = component.sketches.add(component.xYConstructionPlane)
        collar_sketch.name = 'SKETCH_02_EXHAUST_COLLAR'
        _rectangle(collar_sketch, 9.0)
        collar_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 4.1
        )
        collar_profile = _profiles_by_area(collar_sketch)[0]
        collar_input = extrudes.createInput(
            collar_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        collar_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                _value('exhaust_collar_depth')
            ),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        collar_feature = extrudes.add(collar_input)
        collar_feature.name = 'EXTRUDE_02_EXHAUST_COLLAR'

        body = component.bRepBodies.itemByName('EXHAUST_FAN_BRACKET_BODY')
        assigned = _assign_material(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-EFM-001')
        component.attributes.add('PROJECT_FALCON_01', 'Fan', '80 x 80 x 25 mm; 12 V PWM')
        component.attributes.add('PROJECT_FALCON_01', 'Airflow', 'Hot air out of isolated electronics bay')
        component.attributes.add('PROJECT_FALCON_01', 'Protection', 'Backflow and splash baffle provision')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign ABS manually if unavailable locally.'
        ui.messageBox(
            'EXHAUST_FAN_MODULE completed as a separate component.\n\n'
            'Fan: 80 x 80 x 25 mm PWM\nOpening: 76 mm\n'
            'Mounting pitch: 71.5 mm\nHot-air collar: 45 mm\n'
            'ELECTRONICS_BOX_V3 was not modified.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'EXHAUST_FAN_MODULE generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )

