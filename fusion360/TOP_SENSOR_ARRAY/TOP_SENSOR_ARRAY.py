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


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _add_cylinder(component, z, radius_cm, height, operation, name, x=0, y=0):
    plane = component.xYConstructionPlane if z == 0 else _offset_plane(
        component, '{} mm'.format(z), name + '_PLANE'
    )
    sketch = component.sketches.add(plane)
    sketch.name = name.replace('EXTRUDE', 'SKETCH')
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(x, y, 0), radius_cm
    )
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = name
    return feature


def _build_gnss(component):
    base = _add_cylinder(
        component, 0, 1.6, '25 mm',
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        'EXTRUDE_01_GNSS_BASE'
    )
    base.bodies.item(0).name = 'GNSS_ANTENNA_BODY'
    _add_cylinder(
        component, 20, 0.8, '190 mm',
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'EXTRUDE_02_GNSS_MAST'
    )
    _add_cylinder(
        component, 205, 4.0, '45 mm',
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'EXTRUDE_03_GNSS_RADOME'
    )


def _build_whip(component, label, height_mm):
    base = _add_cylinder(
        component, 0, 1.5, '22 mm',
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        'EXTRUDE_01_{}_BASE'.format(label)
    )
    base.bodies.item(0).name = '{}_ANTENNA_BODY'.format(label)
    _add_cylinder(
        component, 18, 0.4, '{} mm'.format(height_mm),
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'EXTRUDE_02_{}_WHIP'.format(label)
    )


def _build_lightning_rod(component):
    base = _add_cylinder(
        component, 0, 1.5, '20 mm',
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        'EXTRUDE_01_LIGHTNING_BASE'
    )
    base.bodies.item(0).name = 'LIGHTNING_ROD_316SS_BODY'
    _add_cylinder(
        component, 18, 0.3, '280 mm',
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        'EXTRUDE_02_LIGHTNING_ROD'
    )


def _build_wind_sensor(component):
    mast = _add_cylinder(
        component, 0, 1.2, '215 mm',
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        'EXTRUDE_01_WIND_SENSOR_MAST'
    )
    mast.bodies.item(0).name = 'WIND_SENSOR_BODY'
    rotor_plane = _offset_plane(component, '207 mm', 'PLANE_01_ANEMOMETER_ROTOR')
    rotor_sketch = component.sketches.add(rotor_plane)
    rotor_sketch.name = 'SKETCH_02_THREE_ARM_ANEMOMETER'
    lines = rotor_sketch.sketchCurves.sketchLines
    for angle in (0, 2 * math.pi / 3, 4 * math.pi / 3):
        tangent_x = -math.sin(angle) * 0.4
        tangent_y = math.cos(angle) * 0.4
        end_x = math.cos(angle) * 8.0
        end_y = math.sin(angle) * 8.0
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-tangent_x, -tangent_y, 0),
            adsk.core.Point3D.create(end_x + tangent_x, end_y + tangent_y, 0)
        )
    circles = rotor_sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 1.5)
    for angle in (0, 2 * math.pi / 3, 4 * math.pi / 3):
        circles.addByCenterRadius(
            adsk.core.Point3D.create(
                8.0 * math.cos(angle), 8.0 * math.sin(angle), 0
            ),
            1.5
        )
    profiles = adsk.core.ObjectCollection.create()
    for i in range(rotor_sketch.profiles.count):
        profiles.add(rotor_sketch.profiles.item(i))
    extrudes = component.features.extrudeFeatures
    rotor_input = extrudes.createInput(
        profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    rotor_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('12 mm')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    rotor = extrudes.add(rotor_input)
    rotor.name = 'EXTRUDE_02_THREE_CUP_ANEMOMETER'


def _find_material(app, names):
    for library in app.materialLibraries:
        for name in names:
            material = library.materials.itemByName(name)
            if material:
                return material
    return None


def _place_child(parent, name, x, y, builder, material, part_number):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, 88.2)
    occurrence = parent.occurrences.addNewComponent(transform)
    component = occurrence.component
    component.name = name
    builder(component)
    if material:
        for body in component.bRepBodies:
            body.material = material
    component.attributes.add('PROJECT_FALCON_01', 'PartNumber', part_number)
    return component


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
        if _find_occurrence(root, 'TOP_SENSOR_ARRAY'):
            raise RuntimeError('TOP_SENSOR_ARRAY already exists; nothing was changed.')
        if not _find_occurrence(root, 'UPPER_EQUIPMENT_FRAME'):
            raise RuntimeError('UPPER_EQUIPMENT_FRAME was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'top_sensor_deck_z', '882 mm', 'mm', 'Upper frame antenna deck elevation')
        _add_parameter(parameters, 'gnss_total_height', '250 mm', 'mm', 'GNSS antenna assembly height')
        _add_parameter(parameters, 'lte_whip_height', '220 mm', 'mm', 'LTE whip length')
        _add_parameter(parameters, 'wifi_whip_height', '180 mm', 'mm', 'Wi-Fi whip length')
        _add_parameter(parameters, 'wind_sensor_height', '219 mm', 'mm', 'Anemometer height above deck')
        _add_parameter(parameters, 'lightning_rod_height', '298 mm', 'mm', 'Air-terminal height')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'TOP_SENSOR_ARRAY'
        aluminum = _find_material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        steel = _find_material(app, ('Stainless Steel 316', 'Stainless Steel', 'Steel'))

        _place_child(system_component, 'GNSS_GPS_ANTENNA', 0, 0, _build_gnss, aluminum, 'FALCON-ANT-001')
        _place_child(
            system_component, 'LTE_4G_ANTENNA', 12.0, 0,
            lambda component: _build_whip(component, 'LTE_4G', 220),
            steel, 'FALCON-ANT-002'
        )
        _place_child(
            system_component, 'WIFI_ANTENNA', -12.0, 0,
            lambda component: _build_whip(component, 'WIFI', 180),
            steel, 'FALCON-ANT-003'
        )
        _place_child(
            system_component, 'WIND_SPEED_SENSOR', 0, 12.0,
            _build_wind_sensor, aluminum, 'FALCON-WS-001'
        )
        _place_child(
            system_component, 'LIGHTNING_AIR_TERMINAL', 0, -12.0,
            _build_lightning_rod, steel, 'FALCON-LP-001'
        )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Separate GNSS, LTE, Wi-Fi, wind sensor, and lightning-protection components'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing frame and assembly untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'TOP_SENSOR_ARRAY completed.\n\n'
            'Separate editable components:\n'
            '- GNSS/GPS antenna\n- 4G/LTE antenna\n- Wi-Fi antenna\n'
            '- Three-cup wind-speed sensor\n- Lightning air terminal\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'TOP_SENSOR_ARRAY generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
