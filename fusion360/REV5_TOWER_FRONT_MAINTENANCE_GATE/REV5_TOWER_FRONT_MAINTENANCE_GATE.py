import adsk.core
import adsk.fusion
import traceback


FRONT_Y = -22.0
LOWER_Z = 59.0
UPPER_Z = 98.0
LOWER_HALF = 17.0
UPPER_HALF = 15.5


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


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


def _member(component, start, end, index, name, material, diameter):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_{}'.format(index, name)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(diameter)
    input_.isHollow = False
    body = component.features.pipeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _cylinder(component, radius, height, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(_point(0, 0, 0), radius)
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


def _box(component, width, depth, height, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        _point(-width / 2, -depth / 2, 0), _point(width / 2, depth / 2, 0)
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


def _hide_replaced_front_members(root):
    prefixes = (
        'BAY_1_S_X_A', 'BAY_1_S_X_B', 'BAY_2_S_X_A', 'BAY_2_S_X_B',
        'LEVEL_01_SIDE_03_RAIL', 'LEVEL_02_SIDE_03_RAIL',
        'LEVEL_03_SIDE_03_RAIL'
    )
    hidden = 0
    for occurrence in root.allOccurrences:
        for body in occurrence.component.bRepBodies:
            normalized = body.name.upper().replace(' ', '_')
            if any(normalized.startswith(prefix) for prefix in prefixes):
                body.isVisible = False
                hidden += 1
    return hidden


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
        if _find(root, 'REV5_TOWER_FRONT_MAINTENANCE_GATE'):
            raise RuntimeError('REV5_TOWER_FRONT_MAINTENANCE_GATE already exists; nothing was changed.')
        for required in ('REV5_TAPERED_MARINE_MAST',
                         'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD',
                         'REV5_INNER_SEALED_BOX_COOLING'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_gate_lower_width', '340 mm', 'mm', 'Lower gate outside width')
        _parameter(p, 'rev5_gate_upper_width', '310 mm', 'mm', 'Upper gate outside width')
        _parameter(p, 'rev5_gate_height', '390 mm', 'mm', 'Front maintenance opening height')
        _parameter(p, 'rev5_gate_frame_OD', '25 mm', 'mm', '6061-T6 perimeter tube OD')
        _parameter(p, 'rev5_gate_brace_OD', '20 mm', 'mm', 'Gate X-brace tube OD')
        _parameter(p, 'rev5_gate_hinge_pin_OD', '10 mm', 'mm', 'Removable 316L hinge pin OD')
        _parameter(p, 'rev5_gate_open_angle', '100 deg', 'deg', 'Minimum intended service opening')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_TOWER_FRONT_MAINTENANCE_GATE'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        stainless = _material(app, ('Stainless Steel 316L', 'Stainless Steel', 'Steel'))
        rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene'))

        gate = _child(system, 'MOVABLE_FRONT_GATE_PANEL')
        lower_left = _point(-LOWER_HALF, FRONT_Y, LOWER_Z)
        lower_right = _point(LOWER_HALF, FRONT_Y, LOWER_Z)
        upper_left = _point(-UPPER_HALF, FRONT_Y, UPPER_Z)
        upper_right = _point(UPPER_HALF, FRONT_Y, UPPER_Z)
        members = (
            (lower_left, lower_right, 'GATE_LOWER_RAIL', 2.5),
            (upper_left, upper_right, 'GATE_UPPER_RAIL', 2.5),
            (lower_left, upper_left, 'GATE_LEFT_HINGE_STILE', 2.5),
            (lower_right, upper_right, 'GATE_RIGHT_LATCH_STILE', 2.5),
            (lower_left, upper_right, 'GATE_X_BRACE_A', 2.0),
            (lower_right, upper_left, 'GATE_X_BRACE_B', 2.0)
        )
        for index, (start, end, name, diameter) in enumerate(members, 1):
            _member(gate, start, end, index, name, aluminum, diameter)

        hinges = _child(system, 'LEFT_REMOVABLE_HINGE_ASSEMBLY')
        for index, z in enumerate((61.0, 71.5, 84.5, 94.0), 1):
            barrel = _child(hinges, 'LEFT_HINGE_BARREL_{:02d}'.format(index),
                            -17.2, FRONT_Y - 0.2, z)
            _cylinder(barrel, 1.4, '55 mm',
                      'HINGE_BARREL_{:02d}_316L'.format(index), stainless)
        pin = _child(hinges, 'CAPTIVE_REMOVABLE_HINGE_PIN', -17.2, FRONT_Y - 0.2, 59.0)
        _cylinder(pin, 0.5, '390 mm', 'HINGE_PIN_10MM_316L', stainless)

        locks = _child(system, 'RIGHT_CAPTIVE_GATE_LOCKS')
        for index, z in enumerate((65.0, 90.0), 1):
            lock = _child(locks, 'RIGHT_COMPRESSION_LOCK_{:02d}'.format(index),
                          16.7, FRONT_Y - 1.0, z)
            _box(lock, 5.0, 3.0, '45 mm',
                 'CAPTIVE_COMPRESSION_LOCK_{:02d}_316L'.format(index), stainless)

        stops = _child(system, 'GATE_EPDM_ANTI_RATTLE_STOPS')
        for index, (x, z) in enumerate(((-15.5, 60.0), (15.5, 60.0),
                                        (-14.5, 96.0), (14.5, 96.0)), 1):
            stop = _child(stops, 'EPDM_GATE_STOP_{:02d}'.format(index), x, FRONT_Y + 0.8, z)
            _box(stop, 2.5, 1.2, '8 mm', 'EPDM_STOP_{:02d}'.format(index), rubber)

        hidden = _hide_replaced_front_members(root)
        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-TMG-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'Access',
                              'Front gate aligned with outer and inner electronics service doors')
        system.attributes.add('PROJECT_FALCON_01', 'Animation',
                              'Separate gate component; revolute axis is the left 10 mm hinge pin')
        system.attributes.add('PROJECT_FALCON_01', 'HiddenLegacyMembers', str(hidden))
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'Verify 100 deg collision envelope, hinges, locks, wind and fatigue loads')

        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'REV5_TOWER_FRONT_MAINTENANCE_GATE completed.\n\n'
            'Front tapered gate: 340/310 x 390 mm\n'
            '25 mm perimeter with 20 mm X-bracing\n'
            'Left removable hinge pin; two right captive locks\n'
            '{} obstructing front members hidden, not deleted\n'
            'Side/rear mast, solar panels and sensors untouched.\n\n'
            'Capture Position, save, then send a screenshot.'.format(hidden),
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_TOWER_FRONT_MAINTENANCE_GATE failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
