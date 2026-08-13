import adsk.core
import adsk.fusion
import traceback


BASE_Z_CM = 58.0


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


def _child(parent, name, z_cm=0):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, z_cm)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _disk(component, radius_cm, thickness, name, material=None):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), radius_cm
    )
    extrudes = component.features.extrudeFeatures
    input_ = extrudes.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(input_)
    feature.name = 'EXTRUDE_' + name
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _ring(component, outer_cm, inner_cm, height, name, material=None):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_' + name
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), outer_cm)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), inner_cm)
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    profile = min(profiles, key=lambda item: item.areaProperties().area)
    input_ = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    feature.name = 'EXTRUDE_' + name
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _rectangle(component, width_cm, depth_cm, thickness, name, material=None):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width_cm / 2, -depth_cm / 2, 0),
        adsk.core.Point3D.create(width_cm / 2, depth_cm / 2, 0)
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
        if _find_occurrence(root, 'UPPER_ALL_ELECTRONICS_POD'):
            raise RuntimeError('UPPER_ALL_ELECTRONICS_POD already exists; nothing was changed.')
        if not _find_occurrence(root, 'TWO_SIDE_SOLAR_FRAME_V3'):
            raise RuntimeError('TWO_SIDE_SOLAR_FRAME_V3 was not found. Run the two-side frame first.')

        p = design.userParameters
        _add_parameter(p, 'upper_pod_OD', '320 mm', 'mm', 'UV-stabilized HDPE pod diameter')
        _add_parameter(p, 'upper_pod_height', '400 mm', 'mm', 'Dry compartment height')
        _add_parameter(p, 'upper_pod_wall', '8 mm', 'mm', 'HDPE shell wall')
        _add_parameter(p, 'upper_pod_base_z', '580 mm', 'mm', 'Pod mounting elevation')
        _add_parameter(p, 'upper_pod_lid_thickness', '18 mm', 'mm', 'Removable service lid')
        _add_parameter(p, 'upper_pod_shield_gap', '25 mm', 'mm', 'Ventilated solar/rain gap')
        _add_parameter(p, 'upper_pod_shield_OD', '370 mm', 'mm', 'Overhanging sun/rain shield')
        _add_parameter(p, 'upper_pod_gasket_section', '6 mm', 'mm', 'Dual EPDM gasket section')

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, BASE_Z_CM)
        system_occurrence = root.occurrences.addNewComponent(transform)
        system = system_occurrence.component
        system.name = 'UPPER_ALL_ELECTRONICS_POD'
        hdpe = _material(app, ('High Density Polyethylene', 'High-density polyethylene', 'HDPE'))
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('Rubber', 'Neoprene', 'Silicone Rubber'))

        shell = _child(system, 'POD_HDPE_SHELL')
        _disk(shell, 16.0, '8 mm', 'POD_8MM_BASE', hdpe)
        _ring(shell, 16.0, 15.2, '400 mm', 'POD_8MM_WALL', hdpe)
        shell.attributes.add('PROJECT_FALCON_01', 'Protection', 'UV HDPE; 8 mm wall; raised sealing lip')

        tray = _child(system, 'POD_LEAK_TRAY', 1.2)
        _disk(tray, 14.8, '6 mm', 'LEAK_TRAY_HDPE', hdpe)
        _ring(tray, 14.8, 14.2, '25 mm', 'LEAK_TRAY_UPSTAND', hdpe)
        tray.attributes.add('PROJECT_FALCON_01', 'Sensor', 'Water leak sensor mounting at lowest point')

        battery = _child(system, 'POD_BATTERY_RESTRAINT', 4.5)
        _rectangle(battery, 24.0, 18.0, '6 mm', 'BATTERY_SUPPORT_DECK', aluminum)
        battery.attributes.add('PROJECT_FALCON_01', 'Payload', 'LiFePO4 battery plus BMS; captive strap required')

        thermal = _child(system, 'POD_THERMAL_SPREAD_PLATE', 17.0)
        _disk(thermal, 14.5, '6 mm', 'SEALED_THERMAL_SPREADER_6061', aluminum)
        thermal.attributes.add('PROJECT_FALCON_01', 'Cooling', 'Mini PC and MPPT thermal-pad interface; sealed internal circulation')

        rack = _child(system, 'POD_CONTROL_RACK', 27.0)
        _rectangle(rack, 24.0, 20.0, '5 mm', 'ESP32_MODEM_CONTROL_DECK', aluminum)
        rack.attributes.add('PROJECT_FALCON_01', 'Payload', 'ESP32, Orange Pi, LTE, GPS interface, DC-DC, fuse distribution')

        lid = _child(system, 'POD_SERVICE_LID', 40.0)
        _disk(lid, 16.8, '18 mm', 'REMOVABLE_HDPE_SERVICE_LID', hdpe)
        _ring(lid, 15.1, 14.5, '6 mm', 'EPDM_GASKET_INNER', rubber)
        _ring(lid, 15.9, 15.3, '6 mm', 'EPDM_GASKET_OUTER', rubber)
        lid.attributes.add('PROJECT_FALCON_01', 'Seal', 'Double EPDM gasket; captive 316L perimeter fasteners')

        shield = _child(system, 'POD_SUN_RAIN_SHIELD', 44.3)
        _disk(shield, 18.5, '5 mm', 'VENTILATED_OVERHANG_SHIELD', hdpe)
        shield.attributes.add('PROJECT_FALCON_01', 'Protection', '25 mm air gap; rain overhang; light UV-reflective finish')

        connector = _child(system, 'POD_DOWNWARD_CONNECTOR_PANEL', 0.8)
        _rectangle(connector, 18.0, 6.0, '8 mm', 'IP68_DOWNWARD_CONNECTOR_PLATE', hdpe)
        connector.attributes.add('PROJECT_FALCON_01', 'Interface', 'Downward IP68 bulkhead connectors and cable drip loops')

        vent = _child(system, 'POD_MEMBRANE_VENT', 38.0)
        _disk(vent, 1.2, '12 mm', 'IP67_PRESSURE_EQUALIZATION_BOSS', hdpe)
        vent.attributes.add('PROJECT_FALCON_01', 'Vent', 'Hydrophobic pressure membrane; not an open cooling intake')

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-UEP-001')
        system.attributes.add('PROJECT_FALCON_01', 'Architecture', 'All electronics and battery in removable upper service pod')
        system.attributes.add('PROJECT_FALCON_01', 'Environmental', 'IP67 design intent; UV, rain, spray, salt, heat, vibration provisions')
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'Thermal soak, spray/immersion, salt fog, vibration, flotation and righting tests required')
        system.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing components were not moved, hidden, or deleted')

        app.activeViewport.fit()
        ui.messageBox(
            'UPPER_ALL_ELECTRONICS_POD completed.\n\n'
            'Pod: 320 mm OD x 400 mm; 8 mm UV-HDPE\n'
            'Separate service lid with dual EPDM gaskets\n'
            'Ventilated sun/rain shield with 25 mm air gap\n'
            'Leak tray, battery restraint, thermal plate, and control rack\n'
            'Downward IP68 connector panel and membrane vent\n'
            'Cooling: sealed internal recirculation; no salt-air intake\n'
            'Existing assembly components were not moved or deleted.\n\n'
            'Click Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'UPPER_ALL_ELECTRONICS_POD failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
