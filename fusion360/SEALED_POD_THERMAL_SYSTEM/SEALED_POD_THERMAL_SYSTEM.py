import adsk.core
import adsk.fusion
import traceback


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _find(root, prefix):
    for occurrence in root.allOccurrences:
        name = occurrence.component.name.upper().replace(' ', '_')
        if name.startswith(prefix.upper()):
            return occurrence
    return None


def _parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


def _material(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _child(parent, name, x=0.0, y=0.0, z=0.0):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _rear_transform(x, y, z):
    transform = adsk.core.Matrix3D.create()
    transform.setToRotation(
        3.141592653589793,
        adsk.core.Vector3D.create(0, 0, 1),
        adsk.core.Point3D.create(0, 0, 0)
    )
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    return transform


def _rear_child(parent, name, x=0.0, y=0.0, z=0.0):
    occurrence = parent.occurrences.addNewComponent(_rear_transform(x, y, z))
    occurrence.component.name = name
    return occurrence.component


def _repair_rear_thermal_side(system):
    repaired = []
    targets = {
        'POD_SEALED_THERMAL_BRIDGE': (0, 14.9, 16.0),
        'POD_EXTERNAL_FINNED_HEAT_SINK': (0, 16.6, 16.0),
    }
    for occurrence in system.occurrences:
        name = occurrence.component.name.upper().replace(' ', '_')
        position = targets.get(name)
        if position:
            occurrence.transform2 = _rear_transform(*position)
            repaired.append(name)
    return repaired


def _hide_obsolete_inner_box(root):
    hidden = False
    names = (
        'INNER_SEALED_ELECTRONICS_BOX',
        'INNER_BOX_RAISED_FRONT_SEAL_FRAME',
        'INNER_BOX_OUTER_EPDM_GASKET',
        'INNER_BOX_INNER_EPDM_GASKET',
        'INNER_BOX_REMOVABLE_FRONT_SERVICE_DOOR',
        'INNER_BOX_EQUIPMENT_DECKS',
    )
    for name in names:
        occurrence = _find(root, name)
        if occurrence and occurrence.isLightBulbOn:
            occurrence.isLightBulbOn = False
            hidden = True
    return hidden


def _box(component, plane, x1, y1, x2, y2, thickness, name, material):
    sketch = component.sketches.add(plane)
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x1, y1, 0),
        adsk.core.Point3D.create(x2, y2, 0)
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _front_frame(component, width, height, border, thickness, name, material):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_' + name
    rectangles = sketch.sketchCurves.sketchLines
    rectangles.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2, 0, 0),
        adsk.core.Point3D.create(width / 2, height, 0)
    )
    rectangles.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2 + border, border, 0),
        adsk.core.Point3D.create(width / 2 - border, height - border, 0)
    )
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    profile = min(profiles, key=lambda item: item.areaProperties().area)
    input_ = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _fan(component, index, material):
    # Horizontal cartridge, matching the installed Screenshot-693 geometry.
    _box(component, component.xYConstructionPlane, -4.0, -4.0, 4.0, 4.0,
         '25 mm', 'INTERNAL_FAN_{:02d}_80MM_FRAME'.format(index), material)
    hub = _child(component, 'INTERNAL_FAN_{:02d}_ROTOR_HUB'.format(index), 0, 0, 0.3)
    sketch = hub.sketches.add(hub.xYConstructionPlane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), 2.2
    )
    input_ = hub.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('20 mm')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    body = hub.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = 'INTERNAL_FAN_{:02d}_ROTOR'.format(index)
    if material:
        body.material = material


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Open PROJECT FALCON-01 before running this script.')
        root = design.rootComponent
        if design.snapshots.hasPendingSnapshot:
            raise RuntimeError('Click Capture Position, save, then run again.')
        pod_occurrence = _find(root, 'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD')
        if not pod_occurrence:
            raise RuntimeError('REV5_RECTANGULAR_MARINE_ELECTRONICS_POD was not found.')
        # Prefer the installed original thermal assembly shown in Screenshot
        # 693. Reuse it instead of replacing it with the later misplaced
        # cooling-only occurrence.
        existing = (_find(root, 'SEALED_POD_THERMAL_SYSTEM') or
                    _find(root, 'REV5_RECTANGULAR_POD_COOLING_SYSTEM') or
                    _find(root, 'REV5_INNER_SEALED_BOX_COOLING'))
        if existing:
            # The buoy assembly may have been repositioned after earlier parts
            # were generated. Reuse the pod occurrence transform so this
            # system follows the completed pod without deleting/rebuilding it.
            existing.transform2 = pod_occurrence.transform2.copy()
            existing.component.name = 'SEALED_POD_THERMAL_SYSTEM'
            existing.isLightBulbOn = True
            repaired = _repair_rear_thermal_side(existing.component)
            _hide_obsolete_inner_box(root)
            obsolete_sensor = _find(root, 'POD_TEMP_HUMIDITY_SENSOR_BRACKET')
            if obsolete_sensor:
                obsolete_sensor.isLightBulbOn = False
            duplicate = _find(root, 'REV5_RECTANGULAR_POD_COOLING_SYSTEM')
            if duplicate and duplicate != existing:
                duplicate.isLightBulbOn = False
            app.activeViewport.fit()
            ui.messageBox(
                'SEALED_POD_THERMAL_SYSTEM repaired.\n\n'
                'Original Screenshot-693 thermal geometry retained.\n'
                'Horizontal upper/lower fans and airflow guides retained.\n'
                'Vertical bridge and 8-fin heat sink moved to the rear (+Y) side.\n'
                'Front maintenance-door side remains unobstructed.\n'
                'Obsolete humidity bracket and duplicate cooling occurrence hidden.\n'
                'No body or component was deleted or duplicated.\n\n'
                'Capture Position, save, then send a screenshot.',
                'PROJECT FALCON-01'
            )
            return

        p = design.userParameters
        _parameter(p, 'rev5_cooling_fan_size', '80 mm', 'mm', 'Internal recirculation fan size')
        _parameter(p, 'rev5_airflow_guide_thickness', '4 mm', 'mm', 'Internal airflow guide thickness')
        _parameter(p, 'rev5_heat_sink_width', '180 mm', 'mm', 'External heat sink width')
        _parameter(p, 'rev5_heat_sink_height', '220 mm', 'mm', 'External heat sink height')
        _parameter(p, 'rev5_heat_sink_fin_count', '8', '', 'External heat sink fin count')

        # Create directly at the completed pod occurrence transform, rather
        # than assuming that the full assembly is still at the global origin.
        occurrence = root.occurrences.addNewComponent(pod_occurrence.transform2.copy())
        system = occurrence.component
        system.name = 'SEALED_POD_THERMAL_SYSTEM'
        polymer = _material(app, ('ABS Plastic', 'Plastic', 'Nylon'))
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))

        # Screenshot-693 layout: two horizontal fan cartridges move sealed
        # air vertically between decks. The guides prevent a short airflow
        # loop and direct return air toward the rear thermal interface.
        fan1 = _child(system, 'POD_INTERNAL_FAN_LOWER', -5.0, 0, 23.0)
        _fan(fan1, 1, polymer)
        fan2 = _child(system, 'POD_INTERNAL_FAN_UPPER', 5.0, 0, 34.0)
        _fan(fan2, 2, polymer)

        baffles = _child(system, 'POD_INTERNAL_AIRFLOW_BAFFLES')
        _box(baffles, baffles.xYConstructionPlane, -13.0, -2.0, 13.0, 2.0,
             '4 mm', 'LOWER_AIR_GUIDE', polymer)
        upper_baffle = _child(baffles, 'UPPER_RETURN_AIR_GUIDE', 0, 0, 34.0)
        _box(upper_baffle, upper_baffle.xYConstructionPlane,
             -13.0, -2.0, 13.0, 2.0, '4 mm', 'UPPER_AIR_GUIDE', polymer)

        # One vertical clamped plate carries heat through the sealed rear wall.
        # It is not an air duct and does not create an ingress path.
        bridge = _rear_child(system, 'POD_SEALED_THERMAL_BRIDGE', 0, 14.9, 16.0)
        _box(bridge, bridge.xZConstructionPlane, -9.0, 0, 9.0, 22.0,
             '12 mm', 'INTERNAL_CLAMPED_THERMAL_BRIDGE', aluminum)
        bridge.attributes.add('PROJECT_FALCON_01', 'Seal',
                              'Compression gasket and thermal pad; solid conductor with no air passage')

        # Vertical rear base plus eight projecting fins. In transparent Fusion
        # views the fins appear horizontal/in the middle, but they belong to
        # this single external heat-sink assembly.
        sink = _rear_child(system, 'POD_EXTERNAL_FINNED_HEAT_SINK', 0, 16.6, 16.0)
        _box(sink, sink.xZConstructionPlane, -9.0, 0, 9.0, 22.0,
             '6 mm', 'EXTERNAL_HEAT_SINK_BASE', aluminum)
        for index, x in enumerate((-7.7, -5.5, -3.3, -1.1, 1.1, 3.3, 5.5, 7.7), 1):
            fin = _child(sink, 'HEAT_SINK_FIN_{:02d}'.format(index), x, -0.6, 0)
            _box(fin, fin.yZConstructionPlane, -2.5, 0, 0, 22.0,
                 '2 mm', 'EXTERNAL_FIN_{:02d}'.format(index), aluminum)

        system.attributes.add('PROJECT_FALCON_01', 'ControlSensor',
                              'Use existing approved MCP9808 enclosure-temperature sensor only')

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-PTS-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'Architecture',
                              'Cooling-only hardware inside the existing rectangular marine pod')
        system.attributes.add('PROJECT_FALCON_01', 'Cooling',
                              'Two horizontal internal fans; two airflow guides; vertical sealed bridge; rear 8-fin sink')
        system.attributes.add('PROJECT_FALCON_01', 'SensorScope',
                              'Existing MCP9808 only; no humidity sensor and no leak sensor')
        system.attributes.add('PROJECT_FALCON_01', 'Ingress',
                              'No outside-air intake or exhaust into either dry electronics volume')
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'Thermal soak, IP, salt fog, vibration and service-access tests required')

        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'SEALED_POD_THERMAL_SYSTEM completed.\n\n'
            'Uses the existing rectangular marine electronics pod\n'
            'No second electronics box was created\n'
            '2 x horizontal 80 mm internal recirculation fans\n'
            'Lower and upper horizontal airflow guides\n'
            'Vertical sealed thermal bridge and rear 8-fin heat sink\n'
            'Existing MCP9808 only; no humidity/leak sensor\n'
            'No outside-air intake or exhaust\n'
            'Screenshot-693 geometry restored.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('SEALED_POD_THERMAL_SYSTEM failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
