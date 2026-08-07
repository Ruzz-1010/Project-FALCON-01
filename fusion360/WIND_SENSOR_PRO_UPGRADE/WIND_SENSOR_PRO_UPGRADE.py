import adsk.core
import adsk.fusion
import math
import traceback


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _has_child(component, child_name):
    for occurrence in component.allOccurrences:
        if occurrence.component.name.upper() == child_name.upper():
            return True
    return False


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _add_cylinder(component, z_mm, x, y, radius, height, name):
    plane = component.xYConstructionPlane if z_mm == 0 else _offset_plane(
        component, '{} mm'.format(z_mm), name + '_PLANE'
    )
    sketch = component.sketches.add(plane)
    sketch.name = name.replace('EXTRUDE', 'SKETCH')
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(x, y, 0), radius
    )
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = name
    return feature.bodies.item(0)


def _add_round_bar(component, start, end, diameter_cm, index, body_name):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_BAR_CENTERLINE'.format(index)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line)
    pipes = component.features.pipeFeatures
    pipe_input = pipes.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(diameter_cm)
    pipe_input.isHollow = False
    feature = pipes.add(pipe_input)
    feature.name = 'PIPE_{:02d}_ROUND_BAR'.format(index)
    feature.bodies.item(0).name = body_name


def _build_anemometer(component):
    hub = _add_cylinder(
        component, 0, 0, 0, 1.2, '30 mm',
        'EXTRUDE_01_ANEMOMETER_HUB'
    )
    hub.name = 'ANEMOMETER_SPEED_HUB'
    for index, angle in enumerate((0, 2 * math.pi / 3, 4 * math.pi / 3), 1):
        end_x = 8.5 * math.cos(angle)
        end_y = 8.5 * math.sin(angle)
        _add_round_bar(
            component,
            adsk.core.Point3D.create(0, 0, 1.5),
            adsk.core.Point3D.create(end_x, end_y, 1.5),
            0.6, index + 1,
            'ANEMOMETER_ARM_{:02d}'.format(index)
        )
        cup_x = end_x - 1.2 * math.sin(angle)
        cup_y = end_y + 1.2 * math.cos(angle)
        cup = _add_cylinder(
            component, 0, cup_x, cup_y, 1.8, '30 mm',
            'EXTRUDE_{:02d}_WIND_CUP'.format(index + 4)
        )
        cup.name = 'ANEMOMETER_CUP_{:02d}'.format(index)
    component.attributes.add(
        'PROJECT_FALCON_01', 'Measurement',
        'Wind speed from three-cup rotor RPM'
    )


def _build_direction_vane(component):
    shaft = _add_cylinder(
        component, 0, 0, 0, 0.6, '65 mm',
        'EXTRUDE_01_DIRECTION_SHAFT'
    )
    shaft.name = 'WIND_DIRECTION_SHAFT'
    _add_round_bar(
        component,
        adsk.core.Point3D.create(-9.0, 0, 3.5),
        adsk.core.Point3D.create(9.0, 0, 3.5),
        0.6, 2, 'WIND_VANE_BOOM'
    )
    tail_sketch = component.sketches.add(component.xZConstructionPlane)
    tail_sketch.name = 'SKETCH_03_DIRECTION_TAIL'
    lines = tail_sketch.sketchCurves.sketchLines
    p1 = adsk.core.Point3D.create(-9.0, -4.0, 0)
    p2 = adsk.core.Point3D.create(-9.0, 4.0, 0)
    p3 = adsk.core.Point3D.create(-4.5, 0, 0)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p1)
    extrudes = component.features.extrudeFeatures
    tail_input = extrudes.createInput(
        tail_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    tail_input.setSymmetricExtent(_value('4 mm'), True)
    tail = extrudes.add(tail_input)
    tail.name = 'EXTRUDE_03_DIRECTION_TAIL_FIN'
    tail.bodies.item(0).name = 'WIND_DIRECTION_TAIL_FIN'
    component.attributes.add(
        'PROJECT_FALCON_01', 'Measurement',
        'Wind direction from rotating vane angle / magnetic encoder'
    )


def _find_material(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            material = library.materials.itemByName(name)
            if material:
                return material
    return None


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
        sensor_occurrence = _find_occurrence(root, 'WIND_SPEED_SENSOR')
        if not sensor_occurrence:
            raise RuntimeError('WIND_SPEED_SENSOR was not found. Run TOP_SENSOR_ARRAY first.')
        sensor_component = sensor_occurrence.component
        if _has_child(sensor_component, 'ANEMOMETER_SPEED_ROTOR'):
            raise RuntimeError('Professional wind-sensor upgrade already exists; nothing was changed.')

        aluminum = _find_material(app)
        anemometer_transform = adsk.core.Matrix3D.create()
        anemometer_transform.translation = adsk.core.Vector3D.create(0, 0, 24.0)
        anemometer_occurrence = sensor_component.occurrences.addNewComponent(
            anemometer_transform
        )
        anemometer = anemometer_occurrence.component
        anemometer.name = 'ANEMOMETER_SPEED_ROTOR'
        _build_anemometer(anemometer)

        vane_transform = adsk.core.Matrix3D.create()
        vane_transform.translation = adsk.core.Vector3D.create(0, 0, 16.0)
        vane_occurrence = sensor_component.occurrences.addNewComponent(vane_transform)
        vane = vane_occurrence.component
        vane.name = 'WIND_DIRECTION_VANE'
        _build_direction_vane(vane)

        if aluminum:
            for child in (anemometer, vane):
                for body in child.bRepBodies:
                    body.material = aluminum
        anemometer.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-WS-002')
        vane.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-WD-001')
        sensor_component.attributes.add(
            'PROJECT_FALCON_01', 'Upgrade',
            'Independent wind-speed rotor plus wind-direction vane'
        )
        sensor_component.name = 'WIND_SPEED_DIRECTION_SENSOR'
        app.activeViewport.fit()
        ui.messageBox(
            'WIND_SPEED_DIRECTION_SENSOR completed.\n\n'
            'ANEMOMETER_SPEED_ROTOR: measures wind strength/speed from RPM\n'
            'WIND_DIRECTION_VANE: measures wind direction from vane angle\n'
            'Both are separate editable child components.\n'
            'No other component was moved, edited, or deleted.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'WIND_SENSOR_PRO_UPGRADE failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
