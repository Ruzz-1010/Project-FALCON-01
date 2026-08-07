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


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _center_rectangle(sketch, width, height):
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2.0, -height / 2.0, 0),
        adsk.core.Point3D.create(width / 2.0, height / 2.0, 0)
    )


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _assign_aluminum(app, body):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            material = library.materials.itemByName(name)
            if material:
                body.material = material
                return True
    return False


def _radial_transform(radial_angle, local_rotation, local_inner_x,
                      hull_radius, elevation):
    angle = radial_angle + local_rotation
    transform = adsk.core.Matrix3D.create()
    transform.setToRotation(
        angle,
        adsk.core.Vector3D.create(0, 0, 1),
        adsk.core.Point3D.create(0, 0, 0)
    )
    transform.translation = adsk.core.Vector3D.create(
        hull_radius * math.cos(radial_angle) - local_inner_x * math.cos(angle),
        hull_radius * math.sin(radial_angle) - local_inner_x * math.sin(angle),
        elevation
    )
    return transform


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Open PROJECT FALCON-01 before running this script.')

        root = design.rootComponent
        if design.snapshots.hasPendingSnapshot:
            raise RuntimeError(
                'Fusion has uncaptured component positions. Nothing was changed.\n\n'
                'Click Capture Position in the toolbar, save the document, then run again.'
            )
        if _find_occurrence(root, 'STABILIZER_ARM'):
            raise RuntimeError(
                'STABILIZER_ARM already exists; non-destructive mode made no changes.'
            )
        if not _find_occurrence(root, 'MAIN_SUPPORT_FRAME'):
            raise RuntimeError('MAIN_SUPPORT_FRAME component was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'stabilizer_arm_length', '475 mm', 'mm', 'Hull to stabilizer center reach')
        _add_parameter(parameters, 'stabilizer_tube_size', '40 mm', 'mm', 'Square tube outside size')
        _add_parameter(parameters, 'stabilizer_tube_wall', '3 mm', 'mm', '6061-T6 tube wall')
        _add_parameter(parameters, 'stabilizer_mount_plate_thickness', '12 mm', 'mm', 'Horizontal mounting foot thickness')
        _add_parameter(parameters, 'stabilizer_mount_hole', '11 mm', 'mm', 'M10 clearance')
        _add_parameter(parameters, 'stabilizer_interface_radius', '430 mm', 'mm', 'Support frame outside radius')
        _add_parameter(parameters, 'stabilizer_arm_center_z', '106 mm', 'mm', 'Tube center elevation')

        tube_size = parameters.itemByName('stabilizer_tube_size').value
        tube_wall = parameters.itemByName('stabilizer_tube_wall').value
        hole_radius = parameters.itemByName('stabilizer_mount_hole').value / 2.0
        interface_radius = parameters.itemByName('stabilizer_interface_radius').value
        arm_center_z = parameters.itemByName('stabilizer_arm_center_z').value

        first_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = first_occurrence.component
        component.name = 'STABILIZER_ARM'
        extrudes = component.features.extrudeFeatures

        tube_sketch = component.sketches.add(component.yZConstructionPlane)
        tube_sketch.name = 'SKETCH_01_HOLLOW_TUBE'
        _center_rectangle(tube_sketch, tube_size, tube_size)
        _center_rectangle(
            tube_sketch, tube_size - 2.0 * tube_wall, tube_size - 2.0 * tube_wall
        )
        tube_profile = _profiles_by_area(tube_sketch)[0]
        tube_input = extrudes.createInput(
            tube_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        tube_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('stabilizer_arm_length')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        tube_feature = extrudes.add(tube_input)
        tube_feature.name = 'EXTRUDE_01_HOLLOW_ARM'
        body = tube_feature.bodies.item(0)
        body.name = 'STABILIZER_ARM_6061_BODY'

        plane_input = component.constructionPlanes.createInput()
        plane_input.setByOffset(component.xYConstructionPlane, _value('-32 mm'))
        foot_plane = component.constructionPlanes.add(plane_input)
        foot_plane.name = 'PLANE_01_MOUNTING_FOOT_BOTTOM'
        plate_sketch = component.sketches.add(foot_plane)
        plate_sketch.name = 'SKETCH_02_FRAME_MOUNTING_FOOT'
        plate_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-10.3, -4.5, 0),
            adsk.core.Point3D.create(0.8, 4.5, 0)
        )
        circles = plate_sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(-7.2, 0, 0), hole_radius)
        circles.addByCenterRadius(adsk.core.Point3D.create(-3.0, 0, 0), hole_radius)
        plate_profile = _profiles_by_area(plate_sketch)[-1]
        plate_input = extrudes.createInput(
            plate_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        plate_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                _value('stabilizer_mount_plate_thickness')
            ),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        plate_feature = extrudes.add(plate_input)
        plate_feature.name = 'EXTRUDE_02_FRAME_MOUNTING_FOOT'

        # Attach only the new arm to the +X support-frame lug.
        arm_transform = adsk.core.Matrix3D.create()
        arm_transform.translation = adsk.core.Vector3D.create(
            interface_radius, 0, arm_center_z
        )
        first_occurrence.transform2 = arm_transform
        body = component.bRepBodies.itemByName('STABILIZER_ARM_6061_BODY')
        assigned = _assign_aluminum(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-SA-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', '6061-T6 marine aluminum')
        component.attributes.add('PROJECT_FALCON_01', 'Placement', 'Attached to +X MAIN_SUPPORT_FRAME lug')
        component.attributes.add('PROJECT_FALCON_01', 'Interface', 'Two M10 vertical bolts')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign 6061-T6 manually if unavailable locally.'
        ui.messageBox(
            'One STABILIZER_ARM component completed.\n\n'
            'Tube: 40 x 40 x 3 mm\nReach: 475 mm\n'
            'Frame interface: horizontal foot; 2 x M10\n'
            'Placement: attached to the +X support-frame lug\n'
            'No existing component was moved or edited.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_ARM generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
