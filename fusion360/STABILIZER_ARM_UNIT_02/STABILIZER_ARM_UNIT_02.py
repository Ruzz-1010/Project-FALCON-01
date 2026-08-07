import adsk.core
import adsk.fusion
import math
import traceback


COMPONENT_NAME = 'STABILIZER_ARM_UNIT_02'
PART_NUMBER = 'FALCON-SAU-002'
ARM_ANGLE = math.pi / 2
ARM_X = 0
ARM_Y = 43.0
PLACEMENT = 'second (+Y) support-frame lug'


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _offset_plane(component, base_plane, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(base_plane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _add_gusset(component, plane, direction, index):
    sketch = component.sketches.add(plane)
    sketch.name = 'SKETCH_0{}_SIDE_GUSSET'.format(index + 2)
    lines = sketch.sketchCurves.sketchLines
    # Local X/Z coordinates relative to the support-frame interface.
    # Exact profile used by the approved first arm reinforcement.
    # It spans 80 mm inward and 140 mm outward from the frame interface.
    # XZ sketch-local Y runs opposite global Z in this component context.
    # Flip the local vertical signs so the result matches the approved upper arm.
    p1 = adsk.core.Point3D.create(-8.0, 2.0, 0)
    p2 = adsk.core.Point3D.create(14.0, 2.0, 0)
    p3 = adsk.core.Point3D.create(0, -2.0, 0)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p1)
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('unit_gusset_thickness')),
        direction
    )
    feature = extrudes.add(extrude_input)
    feature.name = 'EXTRUDE_0{}_SIDE_GUSSET'.format(index + 2)


def _assign_aluminum(app, body):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
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
        if design.snapshots.hasPendingSnapshot:
            raise RuntimeError(
                'Fusion has uncaptured component positions. Nothing was changed.\n\n'
                'Click Capture Position, save, then run again.'
            )
        if _find_occurrence(root, COMPONENT_NAME):
            raise RuntimeError(
                '{} already exists; nothing was changed.'.format(COMPONENT_NAME)
            )
        if not _find_occurrence(root, 'MAIN_SUPPORT_FRAME'):
            raise RuntimeError('MAIN_SUPPORT_FRAME was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'unit_arm_length', '475 mm', 'mm', 'Arm reach')
        _add_parameter(parameters, 'unit_tube_size', '40 mm', 'mm', 'Square tube outside size')
        _add_parameter(parameters, 'unit_tube_wall', '3 mm', 'mm', 'Square tube wall')
        _add_parameter(parameters, 'unit_mount_thickness', '12 mm', 'mm', 'Horizontal mounting foot')
        _add_parameter(parameters, 'unit_m10_clearance', '11 mm', 'mm', 'M10 clearance hole')
        _add_parameter(parameters, 'unit_gusset_thickness', '6 mm', 'mm', 'Twin gusset thickness')

        tube_size = parameters.itemByName('unit_tube_size').value
        tube_wall = parameters.itemByName('unit_tube_wall').value
        hole_radius = parameters.itemByName('unit_m10_clearance').value / 2.0

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = COMPONENT_NAME
        extrudes = component.features.extrudeFeatures

        tube_sketch = component.sketches.add(component.yZConstructionPlane)
        tube_sketch.name = 'SKETCH_01_HOLLOW_TUBE'
        lines = tube_sketch.sketchCurves.sketchLines
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-tube_size / 2, -tube_size / 2, 0),
            adsk.core.Point3D.create(tube_size / 2, tube_size / 2, 0)
        )
        inner = tube_size - 2 * tube_wall
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-inner / 2, -inner / 2, 0),
            adsk.core.Point3D.create(inner / 2, inner / 2, 0)
        )
        tube_input = extrudes.createInput(
            _profiles_by_area(tube_sketch)[0],
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        tube_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('unit_arm_length')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        tube_feature = extrudes.add(tube_input)
        tube_feature.name = 'EXTRUDE_01_HOLLOW_ARM'
        tube_feature.bodies.item(0).name = COMPONENT_NAME + '_6061_BODY'

        foot_plane = _offset_plane(
            component, component.xYConstructionPlane, '-32 mm',
            'PLANE_01_MOUNTING_FOOT_BOTTOM'
        )
        foot_sketch = component.sketches.add(foot_plane)
        foot_sketch.name = 'SKETCH_02_MOUNTING_FOOT'
        foot_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-10.3, -4.5, 0),
            adsk.core.Point3D.create(0.8, 4.5, 0)
        )
        circles = foot_sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(-7.2, 0, 0), hole_radius)
        circles.addByCenterRadius(adsk.core.Point3D.create(-3.0, 0, 0), hole_radius)
        foot_input = extrudes.createInput(
            _profiles_by_area(foot_sketch)[-1],
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        foot_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('unit_mount_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        foot_feature = extrudes.add(foot_input)
        foot_feature.name = 'EXTRUDE_02_MOUNTING_FOOT'

        positive_plane = _offset_plane(
            component, component.xZConstructionPlane, '20 mm',
            'PLANE_02_POSITIVE_GUSSET'
        )
        negative_plane = _offset_plane(
            component, component.xZConstructionPlane, '-20 mm',
            'PLANE_03_NEGATIVE_GUSSET'
        )
        _add_gusset(
            component, positive_plane,
            adsk.fusion.ExtentDirections.PositiveExtentDirection, 1
        )
        _add_gusset(
            component, negative_plane,
            adsk.fusion.ExtentDirections.NegativeExtentDirection, 2
        )

        transform = adsk.core.Matrix3D.create()
        transform.setToRotation(
            ARM_ANGLE,
            adsk.core.Vector3D.create(0, 0, 1),
            adsk.core.Point3D.create(0, 0, 0)
        )
        transform.translation = adsk.core.Vector3D.create(ARM_X, ARM_Y, 10.6)
        occurrence.transform2 = transform

        body = component.bRepBodies.itemByName(COMPONENT_NAME + '_6061_BODY')
        assigned = _assign_aluminum(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', PART_NUMBER)
        component.attributes.add('PROJECT_FALCON_01', 'Construction', 'Arm, foot, and twin gussets unified')
        component.attributes.add('PROJECT_FALCON_01', 'Placement', PLACEMENT)
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing components untouched')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign 6061-T6 manually if unavailable locally.'
        ui.messageBox(
            '{} completed.\n\n'.format(COMPONENT_NAME) +
            'Arm, mounting foot, and twin gussets are one component.\n'
            'Placement: {}.\n'.format(PLACEMENT) +
            'No existing component was moved or edited.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                '{} generation failed:\n\n{}'.format(COMPONENT_NAME, traceback.format_exc()),
                'PROJECT FALCON-01'
            )
