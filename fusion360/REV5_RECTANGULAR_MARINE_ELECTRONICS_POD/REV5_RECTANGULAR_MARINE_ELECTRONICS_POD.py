import adsk.core
import adsk.fusion
import traceback


BASE_Z_CM = 58.0


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


def _child(parent, name, z=0.0):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _corners(width, depth, chamfer):
    x, y, c = width / 2.0, depth / 2.0, chamfer
    return ((-x + c, -y), (x - c, -y), (x, -y + c), (x, y - c),
            (x - c, y), (-x + c, y), (-x, y - c), (-x, -y + c))


def _loop(sketch, points):
    lines = sketch.sketchCurves.sketchLines
    for start, end in zip(points, points[1:] + points[:1]):
        lines.addByTwoPoints(adsk.core.Point3D.create(start[0], start[1], 0),
                            adsk.core.Point3D.create(end[0], end[1], 0))


def _octagonal_solid(component, width, depth, chamfer, height, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_' + name
    _loop(sketch, _corners(width, depth, chamfer))
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(_value(height)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection)
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _octagonal_ring(component, outer_w, outer_d, outer_c,
                    inner_w, inner_d, inner_c, height, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_' + name
    _loop(sketch, _corners(outer_w, outer_d, outer_c))
    _loop(sketch, _corners(inner_w, inner_d, inner_c))
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    profile = min(profiles, key=lambda item: item.areaProperties().area)
    input_ = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(_value(height)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection)
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _rectangle(component, width, depth, thickness, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2, -depth / 2, 0),
        adsk.core.Point3D.create(width / 2, depth / 2, 0)
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection)
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _direct_child(parent, name):
    target = name.upper()
    for occurrence in parent.occurrences:
        if occurrence.component.name.upper() == target:
            return occurrence
    return None


def _front_frame(component, width, height, border, thickness, name, material):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_' + name
    lines = sketch.sketchCurves.sketchLines
    lines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2, 0, 0),
        adsk.core.Point3D.create(width / 2, height, 0)
    )
    lines.addTwoPointRectangle(
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


def _front_panel(component, width, height, thickness, name, material):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2, 0, 0),
        adsk.core.Point3D.create(width / 2, height, 0)
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


def _cylinder(component, radius, height, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), radius
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _front_cut_exists(shell):
    extrudes = shell.features.extrudeFeatures
    return any(extrudes.item(i).name == 'CUT_FRONT_SERVICE_OPENING'
               for i in range(extrudes.count))


def _cut_front_opening(shell):
    wall = None
    for body in shell.bRepBodies:
        if body.name == 'RECT_POD_8MM_HOLLOW_WALL':
            wall = body
            break
    if not wall:
        raise RuntimeError('RECT_POD_8MM_HOLLOW_WALL was not found.')
    plane_input = shell.constructionPlanes.createInput()
    plane_input.setByOffset(shell.xZConstructionPlane, _value('-140 mm'))
    plane = shell.constructionPlanes.add(plane_input)
    plane.name = 'PLANE_FRONT_SERVICE_OPENING'
    sketch = shell.sketches.add(plane)
    sketch.name = 'SKETCH_FRONT_SERVICE_OPENING_220X320'
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-11.0, 4.0, 0),
        adsk.core.Point3D.create(11.0, 36.0, 0)
    )
    input_ = shell.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    input_.setSymmetricExtent(_value('40 mm'), True)
    input_.participantBodies = [wall]
    feature = shell.features.extrudeFeatures.add(input_)
    feature.name = 'CUT_FRONT_SERVICE_OPENING'


def _add_front_service_access(root, system, hdpe, rubber, stainless):
    if _find(root, 'RECT_POD_FRONT_SERVICE_DOOR'):
        return False
    shell_occurrence = _direct_child(system, 'RECT_POD_HDPE_ENCLOSURE')
    if not shell_occurrence:
        raise RuntimeError('RECT_POD_HDPE_ENCLOSURE was not found.')
    shell = shell_occurrence.component
    if not _front_cut_exists(shell):
        _cut_front_opening(shell)

    lip = _child(system, 'RECT_POD_FRONT_RAISED_SEALING_LIP', 0, -14.1, 4.0)
    _front_frame(lip, 25.0, 35.0, 1.5, '6 mm',
                 'FRONT_RAISED_SEALING_LIP', hdpe)
    outer_gasket = _child(system, 'RECT_POD_FRONT_EPDM_GASKET_OUTER', 0, -14.75, 4.0)
    _front_frame(outer_gasket, 23.8, 33.8, 0.5, '5 mm',
                 'FRONT_EPDM_GASKET_OUTER', rubber)
    inner_gasket = _child(system, 'RECT_POD_FRONT_EPDM_GASKET_INNER', 0, -15.3, 4.0)
    _front_frame(inner_gasket, 22.6, 32.6, 0.5, '5 mm',
                 'FRONT_EPDM_GASKET_INNER', rubber)
    door = _child(system, 'RECT_POD_FRONT_SERVICE_DOOR', 0, -15.9, 3.0)
    _front_panel(door, 25.0, 34.0, '10 mm',
                 'REMOVABLE_FRONT_SERVICE_DOOR_HDPE', hdpe)
    door.attributes.add('PROJECT_FALCON_01', 'Seal',
                        'Raised lip with dual continuous EPDM gasket paths')
    door.attributes.add('PROJECT_FALCON_01', 'Opening',
                        'Left hinge; opens outward; minimum intended service angle 100 deg')

    hinges = _child(system, 'RECT_POD_FRONT_DOOR_LEFT_HINGES')
    for index, z in enumerate((7.0, 17.0, 27.0, 35.0), 1):
        hinge = _child(hinges, 'FRONT_DOOR_HINGE_{:02d}'.format(index),
                       -13.0, -16.0, z)
        _cylinder(hinge, 1.2, '45 mm',
                  'FRONT_DOOR_HINGE_BARREL_{:02d}_316L'.format(index), stainless)
    pin = _child(hinges, 'FRONT_DOOR_REMOVABLE_HINGE_PIN', -13.0, -16.0, 5.0)
    _cylinder(pin, 0.45, '340 mm', 'FRONT_DOOR_HINGE_PIN_9MM_316L', stainless)

    latches = _child(system, 'RECT_POD_FRONT_DOOR_RIGHT_COMPRESSION_LATCHES')
    for index, z in enumerate((10.0, 29.0), 1):
        latch = _child(latches, 'FRONT_DOOR_COMPRESSION_LATCH_{:02d}'.format(index),
                       12.5, -16.8, z)
        _rectangle(latch, 4.0, 2.5, '45 mm',
                   'FRONT_DOOR_LATCH_{:02d}_316L'.format(index), stainless)
    return True


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
        existing = _find(root, 'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD')
        if existing:
            hdpe = _material(app, ('High Density Polyethylene', 'High-density polyethylene', 'HDPE'))
            rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene', 'Silicone Rubber'))
            stainless = _material(app, ('Stainless Steel 316L', 'Stainless Steel', 'Steel'))
            added = _add_front_service_access(root, existing.component,
                                              hdpe, rubber, stainless)
            app.activeViewport.fit()
            ui.messageBox(
                ('Front service access completed.\n\n'
                 '220 x 320 mm shell opening\n'
                 'Raised lip and dual EPDM gasket paths\n'
                 'Left hinges and two right compression latches\n'
                 'Existing pod retained; no duplicate component created.\n\n'
                 'Capture Position, save, then send a screenshot.')
                if added else
                'Front service door already exists; nothing was changed.',
                'PROJECT FALCON-01'
            )
            return
        for required in ('UPPER_ALL_ELECTRONICS_POD', 'REV5_TAPERED_MARINE_MAST'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_rect_pod_width', '300 mm', 'mm', 'Outside cabinet width')
        _parameter(p, 'rev5_rect_pod_depth', '280 mm', 'mm', 'Outside cabinet depth')
        _parameter(p, 'rev5_rect_pod_height', '400 mm', 'mm', 'Sealed cabinet height')
        _parameter(p, 'rev5_rect_pod_corner', '35 mm', 'mm', 'Marine corner chamfer')
        _parameter(p, 'rev5_rect_pod_wall', '8 mm', 'mm', 'UV-HDPE wall thickness')
        _parameter(p, 'rev5_rect_pod_lid', '18 mm', 'mm', 'Removable service lid thickness')
        _parameter(p, 'rev5_rect_pod_base_z', '580 mm', 'mm', 'Existing pod mounting elevation')

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, BASE_Z_CM)
        occurrence = root.occurrences.addNewComponent(transform)
        system = occurrence.component
        system.name = 'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD'
        hdpe = _material(app, ('High Density Polyethylene', 'High-density polyethylene', 'HDPE'))
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene', 'Silicone Rubber'))
        stainless = _material(app, ('Stainless Steel 316L', 'Stainless Steel', 'Steel'))

        shell = _child(system, 'RECT_POD_HDPE_ENCLOSURE')
        _octagonal_solid(shell, 30.0, 28.0, 3.5, '8 mm', 'RECT_POD_8MM_BASE', hdpe)
        _octagonal_ring(shell, 30.0, 28.0, 3.5, 28.4, 26.4, 2.7,
                        '400 mm', 'RECT_POD_8MM_HOLLOW_WALL', hdpe)

        leak = _child(system, 'RECT_POD_LEAK_TRAY', 1.2)
        _octagonal_solid(leak, 27.6, 25.6, 2.5, '6 mm', 'INTERNAL_LEAK_TRAY', hdpe)
        _octagonal_ring(leak, 27.6, 25.6, 2.5, 26.4, 24.4, 2.0,
                        '22 mm', 'LEAK_TRAY_UPSTAND', hdpe)

        lower = _child(system, 'RECT_POD_LOWER_POWER_DECK', 4.5)
        _rectangle(lower, 25.0, 20.0, '6 mm', 'BATTERY_MINIPC_MPPT_DECK', aluminum)
        upper = _child(system, 'RECT_POD_UPPER_CONTROL_DECK', 27.0)
        _rectangle(upper, 25.0, 21.0, '5 mm', 'ESP32_MODEM_SENSOR_DECK', aluminum)

        lid = _child(system, 'RECT_POD_REMOVABLE_SERVICE_LID', 40.0)
        _octagonal_solid(lid, 31.6, 29.6, 4.0, '18 mm', 'TOP_SERVICE_LID_HDPE', hdpe)
        _octagonal_ring(lid, 29.2, 27.2, 3.1, 28.0, 26.0, 2.5,
                        '6 mm', 'EPDM_GASKET_OUTER', rubber)
        _octagonal_ring(lid, 27.6, 25.6, 2.4, 26.4, 24.4, 1.8,
                        '6 mm', 'EPDM_GASKET_INNER', rubber)

        hood = _child(system, 'RECT_POD_VENTILATED_RAIN_HOOD', 44.3)
        _octagonal_solid(hood, 33.0, 31.0, 4.5, '5 mm', 'SUN_RAIN_OVERHANG_HDPE', hdpe)

        thermal = _child(system, 'RECT_POD_REAR_THERMAL_INTERFACE', 15.0)
        _rectangle(thermal, 18.0, 0.6, '220 mm', 'SEALED_REAR_HEAT_SPREAD_INTERFACE', aluminum)

        connector = _child(system, 'RECT_POD_DOWNWARD_CABLE_INTERFACE', 0.8)
        _rectangle(connector, 18.0, 6.0, '8 mm', 'IP68_DOWNWARD_GLAND_PLATE', hdpe)
        vent = _child(system, 'RECT_POD_MEMBRANE_VENT_BOSS', 37.0)
        _octagonal_solid(vent, 2.4, 2.4, 0.5, '12 mm', 'IP67_MEMBRANE_VENT_BOSS', hdpe)

        lower.attributes.add('PROJECT_FALCON_01', 'Payload', 'Battery, Mini PC, MPPT and hot power electronics')
        upper.attributes.add('PROJECT_FALCON_01', 'Payload', 'ESP32, modem, sensor interfaces and distribution')
        lid.attributes.add('PROJECT_FALCON_01', 'Seal', 'Dual EPDM paths; captive 316L compression fasteners')
        thermal.attributes.add('PROJECT_FALCON_01', 'Cooling', 'Sealed conduction bridge to external finned heat sink')
        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-RMEP-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'Protection', 'UV-HDPE, dual seal, rain hood, downward glands, membrane vent')
        system.attributes.add(
            'PROJECT_FALCON_01', 'Maintenance',
            'Front service door with removable modular decks; top lid retained for major service'
        )
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'IP test, thermal soak, salt fog, vibration, EMC and structural verification required')
        _add_front_service_access(root, system, hdpe, rubber, stainless)

        for old_name in ('UPPER_ALL_ELECTRONICS_POD', 'UPPER_POD_ELECTRONICS_LAYOUT',
                         'SEALED_POD_THERMAL_SYSTEM', 'POD_MARINE_PROTECTION_HARDWARE'):
            old = _find(root, old_name)
            if old:
                old.isLightBulbOn = False
        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD completed.\n\n'
            '300 x 280 x 400 mm chamfered marine cabinet\n'
            '8 mm UV-HDPE hollow shell and removable top lid\n'
            'Dual EPDM seals and ventilated rain/sun hood\n'
            'Separate leak, power, control, thermal and cable components\n'
            'Old round-pod system hidden, not deleted; no existing part moved.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_RECTANGULAR_MARINE_ELECTRONICS_POD failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
