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


def _find_outward_y_face(body, negative=True):
    candidates = []
    for face in body.faces:
        if not adsk.core.Plane.cast(face.geometry):
            continue
        success, normal = face.evaluator.getNormalAtPoint(face.pointOnFace)
        if not success:
            continue
        if (negative and normal.y < -0.999) or (not negative and normal.y > 0.999):
            candidates.append(face)
    if not candidates:
        return None
    return max(candidates, key=lambda face: face.area)


def _remove_box_opening(box_component):
    cut = box_component.features.extrudeFeatures.itemByName('CUT_01_INTAKE_OPENING')
    sketch = box_component.sketches.itemByName('SKETCH_03_INTAKE_OPENING')
    if cut:
        return 'complete', sketch
    if sketch:
        return 'sketch_only', sketch
    return 'missing', None


def _remove_module_result(component):
    if component.bRepBodies.count or component.sketches.count:
        raise RuntimeError('INTAKE_FAN_MODULE already exists; non-destructive mode made no changes.')


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
        box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX_V3')
        native_v3_ports = box_occurrence is not None
        if not box_occurrence:
            box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX_V2')
        native_v2_ports = box_occurrence is not None and not native_v3_ports
        if not box_occurrence:
            box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX')
        if not box_occurrence:
            raise RuntimeError('ELECTRONICS_BOX component was not found.')
        box_component = box_occurrence.component
        body_name = 'ELECTRONICS_BOX_HDPE_BODY'
        if native_v3_ports:
            body_name = 'ELECTRONICS_BOX_V3_HDPE_BODY'
        elif native_v2_ports:
            body_name = 'ELECTRONICS_BOX_V2_HDPE_BODY'
        box_body = box_component.bRepBodies.itemByName(body_name)
        if not box_body:
            raise RuntimeError('ELECTRONICS_BOX_HDPE_BODY was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'intake_fan_size', '80 mm', 'mm', 'Nominal PWM fan size')
        _add_parameter(parameters, 'intake_opening', '76 mm', 'mm', 'Free-air opening diameter')
        _add_parameter(parameters, 'intake_mount_pitch', '71.5 mm', 'mm', 'Standard 80 mm fan pitch')
        _add_parameter(parameters, 'intake_mount_hole', '4.5 mm', 'mm', 'M4 clearance hole')
        _add_parameter(parameters, 'intake_frame_size', '100 mm', 'mm', 'Removable bracket size')
        _add_parameter(parameters, 'intake_frame_thickness', '4 mm', 'mm', 'Bracket plate thickness')
        _add_parameter(parameters, 'intake_collar_depth', '35 mm', 'mm', 'Filter and splash collar')

        opening_radius = parameters.itemByName('intake_opening').value / 2.0
        pitch = parameters.itemByName('intake_mount_pitch').value
        mount_radius = parameters.itemByName('intake_mount_hole').value / 2.0
        frame_size = parameters.itemByName('intake_frame_size').value

        opening_state, opening_sketch = (
            ('complete', None) if (native_v2_ports or native_v3_ports)
            else _remove_box_opening(box_component)
        )
        half_pitch = pitch / 2.0
        if opening_state != 'complete':
            if opening_state == 'missing':
                front_face = _find_outward_y_face(box_body, negative=True)
                if not front_face:
                    raise RuntimeError('The electronics-box intake wall could not be identified.')

                opening_sketch = box_component.sketches.add(front_face)
                opening_sketch.name = 'SKETCH_03_INTAKE_OPENING'
                center_model = adsk.core.Point3D.create(17.0, -17.0, 12.0)
                center = opening_sketch.modelToSketchSpace(center_model)
                circles = opening_sketch.sketchCurves.sketchCircles
                circles.addByCenterRadius(center, opening_radius)
                for dx in (-half_pitch, half_pitch):
                    for dy in (-half_pitch, half_pitch):
                        circles.addByCenterRadius(
                            adsk.core.Point3D.create(center.x + dx, center.y + dy, 0),
                            mount_radius
                        )

            cut_profiles = adsk.core.ObjectCollection.create()
            for index in range(opening_sketch.profiles.count):
                cut_profiles.add(opening_sketch.profiles.item(index))
            cut_input = box_component.features.extrudeFeatures.createInput(
                cut_profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            cut_input.participantBodies = [box_body]
            cut_input.setTwoSidesExtent(
                adsk.fusion.ThroughAllExtentDefinition.create(),
                adsk.fusion.ThroughAllExtentDefinition.create()
            )
            cut_feature = box_component.features.extrudeFeatures.add(cut_input)
            cut_feature.name = 'CUT_01_INTAKE_OPENING'

        module_occurrence = _find_occurrence(root, 'INTAKE_FAN_MODULE')
        if not module_occurrence:
            transform = adsk.core.Matrix3D.create()
            transform.setToRotation(
                math.pi / 2.0,
                adsk.core.Vector3D.create(1, 0, 0),
                adsk.core.Point3D.create(0, 0, 0)
            )
            box_z = box_occurrence.transform2.translation.z
            transform.translation = adsk.core.Vector3D.create(17.0, -17.0, box_z + 12.0)
            module_occurrence = root.occurrences.addNewComponent(transform)
            module_occurrence.component.name = 'INTAKE_FAN_MODULE'
        component = module_occurrence.component

        _remove_module_result(component)
        if component.bRepBodies.count or component.sketches.count:
            raise RuntimeError('INTAKE_FAN_MODULE contains unknown geometry. Nothing was overwritten.')

        frame_sketch = component.sketches.add(component.xYConstructionPlane)
        frame_sketch.name = 'SKETCH_01_INTAKE_FRAME'
        _rectangle(frame_sketch, frame_size)
        frame_circles = frame_sketch.sketchCurves.sketchCircles
        frame_circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), opening_radius)
        for x in (-half_pitch, half_pitch):
            for y in (-half_pitch, half_pitch):
                frame_circles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), mount_radius)

        frame_profile = _profiles_by_area(frame_sketch)[-1]
        extrudes = component.features.extrudeFeatures
        frame_input = extrudes.createInput(
            frame_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        frame_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('intake_frame_thickness')
        )
        frame_input.setOneSideExtent(
            frame_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        frame_feature = extrudes.add(frame_input)
        frame_feature.name = 'EXTRUDE_01_INTAKE_FRAME'
        body = frame_feature.bodies.item(0)
        body.name = 'INTAKE_FAN_BRACKET_BODY'

        collar_sketch = component.sketches.add(component.xYConstructionPlane)
        collar_sketch.name = 'SKETCH_02_INTAKE_COLLAR'
        _rectangle(collar_sketch, 9.0)
        collar_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 4.1
        )
        collar_profile = _profiles_by_area(collar_sketch)[0]
        collar_input = extrudes.createInput(
            collar_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        collar_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('intake_collar_depth')
        )
        collar_input.setOneSideExtent(
            collar_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        collar_feature = extrudes.add(collar_input)
        collar_feature.name = 'EXTRUDE_02_INTAKE_COLLAR'

        body = component.bRepBodies.itemByName('INTAKE_FAN_BRACKET_BODY')
        material_assigned = _assign_material(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-IFM-001')
        component.attributes.add('PROJECT_FALCON_01', 'Fan', '80 x 80 x 25 mm; 12 V PWM')
        component.attributes.add('PROJECT_FALCON_01', 'Airflow', 'Cool air into isolated hot-electronics bay')
        component.attributes.add('PROJECT_FALCON_01', 'Service', 'Removable filter and splash collar')

        app.activeViewport.fit()
        note = '' if material_assigned else (
            '\nABS metadata was added; assign the physical material manually if needed.'
        )
        ui.messageBox(
            'INTAKE_FAN_MODULE completed.\n\n'
            'Fan: 80 x 80 x 25 mm PWM\nOpening: 76 mm\n'
            'Mounting pitch: 71.5 mm\nCollar depth: 35 mm\n'
            'The electronics-box intake wall was cut automatically.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'INTAKE_FAN_MODULE generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
