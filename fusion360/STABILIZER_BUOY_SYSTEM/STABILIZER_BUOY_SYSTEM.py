import adsk.core
import adsk.fusion
import math
import traceback


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


def _radial_transform(angle, radius_cm, elevation_cm):
    transform = adsk.core.Matrix3D.create()
    transform.setToRotation(
        angle,
        adsk.core.Vector3D.create(0, 0, 1),
        adsk.core.Point3D.create(0, 0, 0)
    )
    transform.translation = adsk.core.Vector3D.create(
        radius_cm * math.cos(angle), radius_cm * math.sin(angle), elevation_cm
    )
    return transform


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _offset_plane(component, base_plane, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(base_plane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _build_buoy(component, index):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_01_HOLLOW_BUOY_PROFILE'
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    axis = lines.addByTwoPoints(
        adsk.core.Point3D.create(0, -13.0, 0),
        adsk.core.Point3D.create(0, 13.0, 0)
    )
    axis.isConstruction = True
    outer_bottom = adsk.core.Point3D.create(0, -12.0, 0)
    outer_side = adsk.core.Point3D.create(12.0, 0, 0)
    outer_top = adsk.core.Point3D.create(0, 12.0, 0)
    inner_bottom = adsk.core.Point3D.create(0, -11.4, 0)
    inner_side = adsk.core.Point3D.create(11.4, 0, 0)
    inner_top = adsk.core.Point3D.create(0, 11.4, 0)
    arcs.addByThreePoints(outer_bottom, outer_side, outer_top)
    lines.addByTwoPoints(outer_top, inner_top)
    arcs.addByThreePoints(inner_top, inner_side, inner_bottom)
    lines.addByTwoPoints(inner_bottom, outer_bottom)
    if sketch.profiles.count != 1:
        raise RuntimeError('Unexpected profile in STABILIZER_BUOY_{:02d}.'.format(index))
    revolves = component.features.revolveFeatures
    revolve_input = revolves.createInput(
        sketch.profiles.item(0), axis,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    revolve_input.setAngleExtent(False, _value('360 deg'))
    feature = revolves.add(revolve_input)
    feature.name = 'REVOLVE_01_HOLLOW_HDPE_SHELL'
    body = feature.bodies.item(0)
    body.name = 'STABILIZER_BUOY_{:02d}_HDPE_BODY'.format(index)
    return body


def _add_ring(component, base_plane, offset, sketch_name, feature_name, body_name):
    plane = _offset_plane(component, base_plane, offset, feature_name + '_PLANE')
    sketch = component.sketches.add(plane)
    sketch.name = sketch_name
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 13.8)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 12.3)
    profile = _profiles_by_area(sketch)[0]
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('cradle_band_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = feature_name
    feature.bodies.item(0).name = body_name


def _build_cradle(component, index):
    _add_ring(
        component, component.xYConstructionPlane, '-3 mm',
        'SKETCH_01_HORIZONTAL_CLAMP_RING', 'EXTRUDE_01_HORIZONTAL_CLAMP_RING',
        'CRADLE_{:02d}_HORIZONTAL_RING'.format(index)
    )
    _add_ring(
        component, component.xZConstructionPlane, '-3 mm',
        'SKETCH_02_VERTICAL_CLAMP_RING_XZ', 'EXTRUDE_02_VERTICAL_CLAMP_RING_XZ',
        'CRADLE_{:02d}_VERTICAL_RING_XZ'.format(index)
    )
    _add_ring(
        component, component.yZConstructionPlane, '-3 mm',
        'SKETCH_03_VERTICAL_CLAMP_RING_YZ', 'EXTRUDE_03_VERTICAL_CLAMP_RING_YZ',
        'CRADLE_{:02d}_VERTICAL_RING_YZ'.format(index)
    )

    connector_plane = _offset_plane(
        component, component.xYConstructionPlane, '-6 mm',
        'PLANE_04_ARM_CONNECTOR_BOTTOM'
    )
    sketch = component.sketches.add(connector_plane)
    sketch.name = 'SKETCH_04_ARM_CONNECTOR'
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-16.0, -2.5, 0),
        adsk.core.Point3D.create(-12.3, 2.5, 0)
    )
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('cradle_connector_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = 'EXTRUDE_04_ARM_CONNECTOR'
    feature.bodies.item(0).name = 'CRADLE_{:02d}_ARM_CONNECTOR'.format(index)


def _find_material(app, names):
    for library in app.materialLibraries:
        for name in names:
            material = library.materials.itemByName(name)
            if material:
                return material
    return None


def _assign_material(component, material):
    if not material:
        return
    for body in component.bRepBodies:
        body.material = material


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
        if _find_occurrence(root, 'STABILIZER_BUOY_SYSTEM'):
            raise RuntimeError('STABILIZER_BUOY_SYSTEM already exists; nothing was changed.')
        if _find_occurrence(root, 'STABILIZER_BUOY_01'):
            raise RuntimeError(
                'Old STABILIZER_BUOY_01 exists. Nothing was changed.\n'
                'Undo only that old test buoy before running the four-buoy system.'
            )
        for required in (
            'MAIN_SUPPORT_FRAME', 'STABILIZER_ARM',
            'STABILIZER_ARM_UNIT_02', 'STABILIZER_ARM_UNIT_03',
            'STABILIZER_ARM_UNIT_04'
        ):
            if not _find_occurrence(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        parameters = design.userParameters
        _add_parameter(parameters, 'system_buoy_OD', '240 mm', 'mm', 'Each stabilizer buoy outside diameter')
        _add_parameter(parameters, 'system_buoy_wall', '6 mm', 'mm', 'Rotomolded HDPE wall')
        _add_parameter(parameters, 'system_buoy_center_radius', '1025 mm', 'mm', 'Radial position of four buoy centers')
        _add_parameter(parameters, 'system_buoy_center_z', '106 mm', 'mm', 'Buoy center elevation')
        _add_parameter(parameters, 'cradle_inside_diameter', '246 mm', 'mm', '6 mm diametral frame clearance')
        _add_parameter(parameters, 'cradle_outside_diameter', '276 mm', 'mm', 'Cradle ring outside diameter')
        _add_parameter(parameters, 'cradle_band_thickness', '6 mm', 'mm', '6061-T6 ring thickness')
        _add_parameter(parameters, 'cradle_connector_thickness', '12 mm', 'mm', 'Arm connector thickness')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'STABILIZER_BUOY_SYSTEM'

        hdpe = _find_material(
            app, ('HDPE', 'High Density Polyethylene', 'Polyethylene, High Density')
        )
        aluminum = _find_material(
            app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum')
        )

        for index, angle in enumerate((0, math.pi / 2, math.pi, 3 * math.pi / 2), 1):
            transform = _radial_transform(angle, 102.5, 10.6)

            buoy_occurrence = system_component.occurrences.addNewComponent(transform)
            buoy_component = buoy_occurrence.component
            buoy_component.name = 'STABILIZER_BUOY_{:02d}'.format(index)
            _build_buoy(buoy_component, index)
            _assign_material(buoy_component, hdpe)
            buoy_component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber', 'FALCON-SB-{:03d}'.format(index)
            )
            buoy_component.attributes.add(
                'PROJECT_FALCON_01', 'Material', 'Rotomolded marine-grade HDPE'
            )

            cradle_occurrence = system_component.occurrences.addNewComponent(transform)
            cradle_component = cradle_occurrence.component
            cradle_component.name = 'STABILIZER_BUOY_CRADLE_{:02d}'.format(index)
            _build_cradle(cradle_component, index)
            _assign_material(cradle_component, aluminum)
            cradle_component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber', 'FALCON-SBC-{:03d}'.format(index)
            )
            cradle_component.attributes.add(
                'PROJECT_FALCON_01', 'Material', '6061-T6 marine aluminum'
            )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Four editable buoy components plus four editable cradle components'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing assembly untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'STABILIZER_BUOY_SYSTEM completed.\n\n'
            '4 separate hollow HDPE buoys: 240 mm OD / 6 mm wall\n'
            '4 separate 6061-T6 three-ring cradle frames\n'
            'All eight child components remain editable and animatable.\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_BUOY_SYSTEM generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
