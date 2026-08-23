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
    _box(component, component.xZConstructionPlane, -4.0, -4.0, 4.0, 4.0,
         '25 mm', 'INTERNAL_FAN_{:02d}_80MM_FRAME'.format(index), material)
    hub = _child(component, 'INTERNAL_FAN_{:02d}_ROTOR_HUB'.format(index), 0, 0.3, 0)
    sketch = hub.sketches.add(hub.xZConstructionPlane)
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
        existing = (_find(root, 'REV5_RECTANGULAR_POD_COOLING_SYSTEM') or
                    _find(root, 'REV5_INNER_SEALED_BOX_COOLING'))
        if existing:
            # The buoy assembly may have been repositioned after earlier parts
            # were generated. Reuse the pod occurrence transform so this
            # system follows the completed pod without deleting/rebuilding it.
            existing.transform2 = pod_occurrence.transform2.copy()
            existing.component.name = 'REV5_RECTANGULAR_POD_COOLING_SYSTEM'
            existing.isLightBulbOn = True
            _hide_obsolete_inner_box(root)
            old = _find(root, 'SEALED_POD_THERMAL_SYSTEM')
            if old:
                old.isLightBulbOn = False
            app.activeViewport.fit()
            ui.messageBox(
                'SEALED_POD_THERMAL_SYSTEM repaired.\n\n'
                'Cooling hardware reconnected to the current rectangular pod origin.\n'
                'The obsolete second inner box is hidden.\n'
                'No body or component was deleted or duplicated.\n\n'
                'Capture Position, save, then send a screenshot.',
                'PROJECT FALCON-01'
            )
            return

        p = design.userParameters
        _parameter(p, 'rev5_cooling_fan_size', '80 mm', 'mm', 'Internal recirculation fan size')
        _parameter(p, 'rev5_cold_plate_thickness', '6 mm', 'mm', 'Rear aluminum cold plate')
        _parameter(p, 'rev5_heat_sink_width', '180 mm', 'mm', 'External heat sink width')
        _parameter(p, 'rev5_heat_sink_height', '220 mm', 'mm', 'External heat sink height')
        _parameter(p, 'rev5_heat_sink_fin_count', '8', '', 'External heat sink fin count')

        # Create directly at the completed pod occurrence transform, rather
        # than assuming that the full assembly is still at the global origin.
        occurrence = root.occurrences.addNewComponent(pod_occurrence.transform2.copy())
        system = occurrence.component
        system.name = 'REV5_RECTANGULAR_POD_COOLING_SYSTEM'
        polymer = _material(app, ('ABS Plastic', 'Plastic', 'Nylon'))
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))

        cold = _child(system, 'INNER_BOX_REAR_COLD_PLATE', 0, 9.8, 10.0)
        _box(cold, cold.xZConstructionPlane, -9.0, 0, 9.0, 22.0,
             '6 mm', 'SEALED_INTERNAL_COLD_PLATE', aluminum)
        bridge = _child(system, 'SEALED_CLAMPED_THERMAL_BRIDGE', 0, 11.2, 10.0)
        _box(bridge, bridge.xZConstructionPlane, -9.0, 0, 9.0, 22.0,
             '12 mm', 'CLAMPED_THERMAL_BRIDGE', aluminum)
        bridge.attributes.add('PROJECT_FALCON_01', 'Seal',
                              'Compression gasket and thermal pad; solid conductor with no air passage')

        fans = _child(system, 'TWO_INTERNAL_RECIRCULATION_FANS')
        fan1 = _child(fans, 'INTERNAL_RECIRCULATION_FAN_LOWER', -7.5, 8.8, 10.0)
        _fan(fan1, 1, polymer)
        fan2 = _child(fans, 'INTERNAL_RECIRCULATION_FAN_UPPER', 7.5, 8.8, 24.0)
        _fan(fan2, 2, polymer)
        fans.attributes.add('PROJECT_FALCON_01', 'ControlSensor',
                            'Use existing approved MCP9808 enclosure-temperature sensor only')

        sink = _child(system, 'EXTERNAL_REAR_FINNED_HEAT_SINK', 0, 15.0, 10.0)
        _box(sink, sink.xZConstructionPlane, -9.0, 0, 9.0, 22.0,
             '6 mm', 'EXTERNAL_HEAT_SINK_BASE', aluminum)
        for index, x in enumerate((-7.7, -5.5, -3.3, -1.1, 1.1, 3.3, 5.5, 7.7), 1):
            fin = _child(sink, 'EXTERNAL_HEAT_SINK_FIN_{:02d}'.format(index), x, 0.6, 0)
            _box(fin, fin.yZConstructionPlane, 0, 0, 2.5, 22.0,
                 '2 mm', 'EXTERNAL_FIN_{:02d}'.format(index), aluminum)

        hood = _child(system, 'EXTERNAL_HEAT_SINK_SPLASH_HOOD', 0, 14.2, 33.2)
        _box(hood, hood.xYConstructionPlane, -11.0, -1.0, 11.0, 3.8,
             '4 mm', 'HEAT_SINK_TOP_SPLASH_HOOD', polymer)
        hood.attributes.add('PROJECT_FALCON_01', 'Airflow',
                            'Sides and bottom remain open; hood blocks direct rain/spray only')

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-ISBC-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'Architecture',
                              'Cooling-only hardware inside the existing rectangular marine pod')
        system.attributes.add('PROJECT_FALCON_01', 'Cooling',
                              'Two internal fans; cold plate; solid thermal bridge; external finned sink')
        system.attributes.add('PROJECT_FALCON_01', 'SensorScope',
                              'Existing MCP9808 only; no humidity sensor and no leak sensor')
        system.attributes.add('PROJECT_FALCON_01', 'Ingress',
                              'No outside-air intake or exhaust into either dry electronics volume')
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'Thermal soak, IP, salt fog, vibration and service-access tests required')

        old = _find(root, 'SEALED_POD_THERMAL_SYSTEM')
        if old:
            old.isLightBulbOn = False
        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'SEALED_POD_THERMAL_SYSTEM completed.\n\n'
            'Uses the existing rectangular marine electronics pod\n'
            'No second electronics box was created\n'
            '2 x 80 mm internal recirculation fans\n'
            'Cold plate, sealed bridge and rear 8-fin heat sink\n'
            'Existing MCP9808 only; no humidity/leak sensor\n'
            'No outside-air intake or exhaust\n'
            'Old thermal concept hidden, not deleted.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('SEALED_POD_THERMAL_SYSTEM failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
