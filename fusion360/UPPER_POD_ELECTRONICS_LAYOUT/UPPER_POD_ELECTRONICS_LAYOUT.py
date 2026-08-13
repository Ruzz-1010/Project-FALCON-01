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


def _equipment(parent, name, x, y, z, width, depth, height, material, part_number, role):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    component = occurrence.component
    component.name = name
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_01_EQUIPMENT_ENVELOPE'
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2, -depth / 2, 0),
        adsk.core.Point3D.create(width / 2, depth / 2, 0)
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('{} mm'.format(height * 10))),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    feature.name = 'EXTRUDE_01_EQUIPMENT_ENVELOPE'
    body = feature.bodies.item(0)
    body.name = name + '_BODY'
    if material:
        body.material = material
    component.attributes.add('PROJECT_FALCON_01', 'PartNumber', part_number)
    component.attributes.add('PROJECT_FALCON_01', 'Role', role)
    component.attributes.add(
        'PROJECT_FALCON_01', 'Envelope',
        '{} x {} x {} mm nominal; verify purchased hardware'.format(
            int(width * 10), int(depth * 10), int(height * 10)
        )
    )


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
        if _find_occurrence(root, 'UPPER_POD_ELECTRONICS_LAYOUT'):
            raise RuntimeError('UPPER_POD_ELECTRONICS_LAYOUT already exists; nothing was changed.')
        if not _find_occurrence(root, 'UPPER_ALL_ELECTRONICS_POD'):
            raise RuntimeError('UPPER_ALL_ELECTRONICS_POD was not found.')

        p = design.userParameters
        _add_parameter(p, 'pod_battery_envelope_width', '240 mm', 'mm', 'LiFePO4 package width')
        _add_parameter(p, 'pod_battery_envelope_depth', '180 mm', 'mm', 'LiFePO4 package depth')
        _add_parameter(p, 'pod_battery_envelope_height', '105 mm', 'mm', 'LiFePO4 package height')
        _add_parameter(p, 'pod_power_level_z', '750 mm', 'mm', 'Power equipment mounting level')
        _add_parameter(p, 'pod_control_level_z', '860 mm', 'mm', 'Control equipment mounting level')
        _add_parameter(p, 'pod_service_clearance', '25 mm', 'mm', 'Minimum service and airflow clearance')

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, POD_BASE_Z_CM)
        occurrence = root.occurrences.addNewComponent(transform)
        system = occurrence.component
        system.name = 'UPPER_POD_ELECTRONICS_LAYOUT'
        dark = _material(app, ('ABS Plastic', 'Plastic', 'Nylon'))
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))

        # Level 1: heaviest items as low as possible inside the removable pod.
        _equipment(system, 'LIFEPO4_BATTERY_12V_ENVELOPE', 0, 0, 5.2,
                   24.0, 18.0, 10.5, dark, 'FALCON-BAT-ENV-001',
                   '12 V LiFePO4 battery; restrained in all axes')
        _equipment(system, 'BATTERY_BMS_ENVELOPE', 0, -11.5, 6.0,
                   12.0, 4.0, 5.0, aluminum, 'FALCON-BMS-ENV-001',
                   'Battery management system with thermal monitoring')

        # Level 2: hot and high-current power equipment on the thermal plate.
        _equipment(system, 'MPPT_CONTROLLER_ENVELOPE', -7.0, 0, 17.8,
                   11.0, 8.0, 4.5, aluminum, 'FALCON-MPPT-ENV-001',
                   'Solar charge controller on thermal interface')
        _equipment(system, 'DC_DC_CONVERTER_ENVELOPE', 6.5, 0, 17.8,
                   9.0, 7.0, 3.5, aluminum, 'FALCON-DCDC-ENV-001',
                   'Isolated regulated power conversion')
        _equipment(system, 'FUSED_POWER_DISTRIBUTION', -7.5, 8.5, 17.8,
                   9.0, 4.0, 3.0, dark, 'FALCON-PDB-ENV-001',
                   'Branch fuses and protected distribution')
        _equipment(system, 'MAIN_BATTERY_DISCONNECT', 7.5, 8.5, 17.8,
                   6.0, 4.0, 4.0, dark, 'FALCON-DISC-ENV-001',
                   'Service-isolation switch accessible after lid removal')

        # Level 3: low-current computing and communications service deck.
        _equipment(system, 'ORANGE_PI_MINI_PC_ENVELOPE', -6.5, 0, 27.5,
                   10.0, 7.0, 3.5, aluminum, 'FALCON-SBC-ENV-001',
                   'Orange Pi / Mini PC edge computing')
        _equipment(system, 'ESP32_CONTROLLER_ENVELOPE', 6.5, 0, 27.5,
                   8.0, 5.5, 2.2, dark, 'FALCON-ESP-ENV-001',
                   'ESP32 primary sensor controller')
        _equipment(system, 'LTE_4G_MODEM_ENVELOPE', -6.5, 8.5, 27.5,
                   9.0, 5.0, 2.5, dark, 'FALCON-LTE-ENV-001',
                   '4G LTE modem and antenna bulkhead interface')
        _equipment(system, 'SENSOR_DISTRIBUTION_BOARD', 6.5, 8.5, 27.5,
                   9.0, 5.0, 2.0, dark, 'FALCON-SDB-ENV-001',
                   'Sensor, GPS, wind, IMU, and leak-input distribution')

        system.attributes.add('PROJECT_FALCON_01', 'Architecture', 'Three-level removable service layout')
        system.attributes.add('PROJECT_FALCON_01', 'Level1', 'Battery and BMS')
        system.attributes.add('PROJECT_FALCON_01', 'Level2', 'MPPT, DC-DC, fused distribution, disconnect')
        system.attributes.add('PROJECT_FALCON_01', 'Level3', 'Orange Pi, ESP32, LTE, sensor distribution')
        system.attributes.add('PROJECT_FALCON_01', 'Warning', 'Packaging envelopes require purchased-part dimension verification')

        app.activeViewport.fit()
        ui.messageBox(
            'UPPER_POD_ELECTRONICS_LAYOUT completed.\n\n'
            'Level 1: LiFePO4 battery and BMS\n'
            'Level 2: MPPT, DC-DC, fuse block, main disconnect\n'
            'Level 3: Orange Pi, ESP32, LTE modem, sensor distribution\n'
            'All equipment is separate and editable.\n'
            'These are packaging envelopes; verify purchased dimensions.\n\n'
            'Click Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'UPPER_POD_ELECTRONICS_LAYOUT failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
