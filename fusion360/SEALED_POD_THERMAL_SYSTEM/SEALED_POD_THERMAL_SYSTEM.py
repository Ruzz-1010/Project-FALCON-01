import adsk.core
import adsk.fusion
import traceback


POD_BASE_Z_CM = 58.0


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _find_occurrence(root, name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == name.upper():
            return occurrence
    return None


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


def _material(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                result = library.materials.itemByName(name)
            except Exception:
                result = None
            if result:
                return result
    return None


def _child(parent, name, x=0, y=0, z=0):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _box(component, plane, x1, y1, x2, y2, thickness, name, material=None):
    sketch = component.sketches.add(plane)
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x1, y1, 0), adsk.core.Point3D.create(x2, y2, 0)
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    feature.name = 'EXTRUDE_' + name
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _fan(component, index, z_cm, material=None):
    # Horizontal fan cartridge: plan-view envelope plus central rotor disc.
    frame = _box(
        component, component.xYConstructionPlane,
        -4.0, -4.0, 4.0, 4.0, '25 mm',
        'FAN_{:02d}_80MM_FRAME'.format(index), material
    )
    component.attributes.add(
        'PROJECT_FALCON_01', 'Fan{:02d}'.format(index),
        '80 mm sealed-bearing internal recirculation fan at local Z {} mm'.format(int(z_cm * 10))
    )
    return frame


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
        if _find_occurrence(root, 'SEALED_POD_THERMAL_SYSTEM'):
            raise RuntimeError('SEALED_POD_THERMAL_SYSTEM already exists; nothing was changed.')
        if not _find_occurrence(root, 'UPPER_ALL_ELECTRONICS_POD'):
            raise RuntimeError('UPPER_ALL_ELECTRONICS_POD was not found.')

        p = design.userParameters
        _add_parameter(p, 'pod_internal_fan_size', '80 mm', 'mm', 'Internal recirculation fan size')
        _add_parameter(p, 'pod_internal_fan_thickness', '25 mm', 'mm', 'Fan cartridge thickness')
        _add_parameter(p, 'pod_heat_sink_width', '180 mm', 'mm', 'External rear heat sink width')
        _add_parameter(p, 'pod_heat_sink_height', '220 mm', 'mm', 'External rear heat sink height')
        _add_parameter(p, 'pod_heat_sink_base', '6 mm', 'mm', 'Sealed aluminum heat-sink base')
        _add_parameter(p, 'pod_heat_sink_fin_count', '8', '', 'External heat-sink fin count')
        _add_parameter(p, 'pod_heat_sink_fin_depth', '25 mm', 'mm', 'External fin projection')
        # Some Fusion builds reject temperature symbols in user-parameter
        # expressions. Store the threshold as a documented Celsius number.
        _add_parameter(p, 'pod_thermal_shutdown_C', '65', '',
                       'Emergency electronics shutdown threshold in deg C')

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, POD_BASE_Z_CM)
        occurrence = root.occurrences.addNewComponent(transform)
        system = occurrence.component
        system.name = 'SEALED_POD_THERMAL_SYSTEM'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        plastic = _material(app, ('ABS Plastic', 'Plastic', 'Nylon'))

        # Keep the battery zone clear: the lower fan sits above the power deck,
        # while the upper fan provides return flow above the control deck.
        fan1 = _child(system, 'POD_INTERNAL_FAN_LOWER', -5.0, 0, 23.0)
        _fan(fan1, 1, 23.0, plastic)
        fan2 = _child(system, 'POD_INTERNAL_FAN_UPPER', 5.0, 0, 34.0)
        _fan(fan2, 2, 34.0, plastic)

        bridge = _child(system, 'POD_SEALED_THERMAL_BRIDGE', 0, -14.9, 16.0)
        _box(
            bridge, bridge.xZConstructionPlane,
            -9.0, 0, 9.0, 22.0, '12 mm',
            'INTERNAL_CLAMPED_THERMAL_BRIDGE', aluminum
        )
        bridge.attributes.add(
            'PROJECT_FALCON_01', 'Seal',
            'Thermal pad and clamped wall interface; no open air passage'
        )

        sink = _child(system, 'POD_EXTERNAL_FINNED_HEAT_SINK', 0, -16.6, 16.0)
        _box(
            sink, sink.xZConstructionPlane,
            -9.0, 0, 9.0, 22.0, '6 mm',
            'EXTERNAL_HEAT_SINK_BASE', aluminum
        )
        for index, x in enumerate((-7.7, -5.5, -3.3, -1.1, 1.1, 3.3, 5.5, 7.7), 1):
            fin = _child(sink, 'HEAT_SINK_FIN_{:02d}'.format(index), x, -0.6, 0)
            _box(
                fin, fin.yZConstructionPlane,
                -2.5, 0, 0, 22.0, '2 mm',
                'EXTERNAL_FIN_{:02d}'.format(index), aluminum
            )

        baffles = _child(system, 'POD_INTERNAL_AIRFLOW_BAFFLES')
        _box(baffles, baffles.xYConstructionPlane, -13.0, -2.0, 13.0, 2.0,
             '4 mm', 'LOWER_AIR_GUIDE', plastic)
        upper_baffle = _child(baffles, 'UPPER_RETURN_AIR_GUIDE', 0, 0, 34.0)
        _box(upper_baffle, upper_baffle.xYConstructionPlane, -13.0, -2.0, 13.0, 2.0,
             '4 mm', 'UPPER_AIR_GUIDE', plastic)

        sensor = _child(system, 'POD_TEMP_HUMIDITY_SENSOR_BRACKET', 11.0, 0, 35.0)
        _box(sensor, sensor.xYConstructionPlane, -2.0, -1.5, 2.0, 1.5,
             '3 mm', 'TEMP_HUMIDITY_SENSOR_MOUNT', plastic)
        sensor.attributes.add(
            'PROJECT_FALCON_01', 'Control',
            'Fan enable 40 degC; derate 55 degC; shutdown 65 degC; humidity alarm 75 percent RH'
        )

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-PTS-001')
        system.attributes.add('PROJECT_FALCON_01', 'Cooling', 'Closed-loop internal air recirculation')
        system.attributes.add('PROJECT_FALCON_01', 'Ingress', 'No outside-air opening into dry electronics volume')
        system.attributes.add('PROJECT_FALCON_01', 'HeatRejection', 'Clamped thermal bridge to rear external finned sink')
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'Thermal soak at solar load and sealed ingress test required')

        app.activeViewport.fit()
        ui.messageBox(
            'SEALED_POD_THERMAL_SYSTEM completed.\n\n'
            '2 x 80 mm internal recirculation fans\n'
            'Internal airflow guides and temperature/humidity bracket\n'
            'Sealed thermal bridge through pod wall interface\n'
            'Rear 180 x 220 mm heat sink with 8 external fins\n'
            'No salt-air intake into the dry compartment\n'
            'Control intent: fan 40 C, derate 55 C, shutdown 65 C\n\n'
            'Click Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'SEALED_POD_THERMAL_SYSTEM failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
