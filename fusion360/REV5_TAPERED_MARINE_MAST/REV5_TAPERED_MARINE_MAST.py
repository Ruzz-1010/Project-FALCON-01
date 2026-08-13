import adsk.core
import adsk.fusion
import traceback


BASE_Z = 49.0
SHOULDER_Z = 100.0
TOP_Z = 129.0
BASE_HALF = 21.0
SHOULDER_HALF = 19.0
TOP_HALF = 13.0


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


def _material(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _child(parent, name):
    occurrence = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


def _half_at(z):
    # Preserve clearance around the existing sealed pod, then taper above it.
    if z <= SHOULDER_Z:
        fraction = (z - BASE_Z) / (SHOULDER_Z - BASE_Z)
        return BASE_HALF + (SHOULDER_HALF - BASE_HALF) * fraction
    fraction = (z - SHOULDER_Z) / (TOP_Z - SHOULDER_Z)
    return SHOULDER_HALF + (TOP_HALF - SHOULDER_HALF) * fraction


def _member(component, start, end, index, name, material, diameter=3.2):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:03d}_{}'.format(index, name)
    sketch.is3D = True
    curve = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(curve, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(diameter)
    input_.isHollow = False
    feature = component.features.pipeFeatures.add(input_)
    feature.name = 'PIPE_{:03d}_{}'.format(index, name)
    body = feature.bodies.item(0)
    body.name = name + '_6061'
    if material:
        body.material = material


def _plate(component, z, half, thickness, name, material):
    input_plane = component.constructionPlanes.createInput()
    input_plane.setByOffset(component.xYConstructionPlane, _value('{} mm'.format(z * 10)))
    plane = component.constructionPlanes.add(input_plane)
    sketch = component.sketches.add(plane)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        _point(-half, -half, 0), _point(half, half, 0)
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
        if _find(root, 'REV5_TAPERED_MARINE_MAST'):
            raise RuntimeError('REV5_TAPERED_MARINE_MAST already exists; nothing was changed.')
        for required in ('REV5_MAIN_BUOY_FRAME_SUPPORT', 'UPPER_ALL_ELECTRONICS_POD',
                         'DUAL_30W_SOLAR_ARRAY'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_mast_base_width', '420 mm', 'mm', 'Square mast base width')
        _parameter(p, 'rev5_mast_shoulder_width', '380 mm', 'mm', 'Pod-clearance shoulder width')
        _parameter(p, 'rev5_mast_top_width', '260 mm', 'mm', 'Square mast top width')
        _parameter(p, 'rev5_mast_height', '800 mm', 'mm', 'Tapered structural height')
        _parameter(p, 'rev5_mast_leg_OD', '32 mm', 'mm', 'Primary 6061-T6 leg diameter')
        _parameter(p, 'rev5_mast_brace_OD', '20 mm', 'mm', 'Rail and X-brace diameter')
        _parameter(p, 'rev5_mast_base_z', '490 mm', 'mm', 'Annular support deck interface')
        _parameter(p, 'rev5_mast_top_z', '1290 mm', 'mm', 'Top sensor platform elevation')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_TAPERED_MARINE_MAST'
        aluminum = _material(app)
        index = 1

        legs = _child(system, 'REV5_MAST_FOUR_SLOPING_LEGS')
        for sx, sy, label in ((1, 1, 'NE'), (-1, 1, 'NW'),
                              (-1, -1, 'SW'), (1, -1, 'SE')):
            _member(legs, _point(sx * BASE_HALF, sy * BASE_HALF, BASE_Z),
                    _point(sx * SHOULDER_HALF, sy * SHOULDER_HALF, SHOULDER_Z), index,
                    'MAST_{}_LOWER_POD_LEG'.format(label), aluminum, 3.2)
            index += 1
            _member(legs, _point(sx * SHOULDER_HALF, sy * SHOULDER_HALF, SHOULDER_Z),
                    _point(sx * TOP_HALF, sy * TOP_HALF, TOP_Z), index,
                    'MAST_{}_UPPER_TAPER_LEG'.format(label), aluminum, 3.2)
            index += 1

        rails = _child(system, 'REV5_MAST_HORIZONTAL_RAILS')
        levels = (65.0, 81.0, 97.0, 113.0, 129.0)
        for level_index, z in enumerate(levels, 1):
            half = _half_at(z)
            points = (_point(half, half, z), _point(-half, half, z),
                      _point(-half, -half, z), _point(half, -half, z))
            for side, (start, end) in enumerate(zip(points, points[1:] + points[:1]), 1):
                _member(rails, start, end, index,
                        'LEVEL_{:02d}_SIDE_{:02d}_RAIL'.format(level_index, side),
                        aluminum, 2.0)
                index += 1

        braces = _child(system, 'REV5_MAST_FULL_X_BRACING')
        # X-brace every face across the lower and middle mast bays.
        for z1, z2, bay in ((49.0, 81.0, 1), (81.0, 113.0, 2)):
            h1, h2 = _half_at(z1), _half_at(z2)
            face_pairs = (
                ((_point(-h1, h1, z1), _point(h2, h2, z2)),
                 (_point(h1, h1, z1), _point(-h2, h2, z2)), 'N'),
                ((_point(-h1, -h1, z1), _point(h2, -h2, z2)),
                 (_point(h1, -h1, z1), _point(-h2, -h2, z2)), 'S'),
                ((_point(h1, -h1, z1), _point(h2, h2, z2)),
                 (_point(h1, h1, z1), _point(h2, -h2, z2)), 'E'),
                ((_point(-h1, -h1, z1), _point(-h2, h2, z2)),
                 (_point(-h1, h1, z1), _point(-h2, -h2, z2)), 'W')
            )
            for first, second, face in face_pairs:
                _member(braces, first[0], first[1], index,
                        'BAY_{}_{}_X_A'.format(bay, face), aluminum, 1.6); index += 1
                _member(braces, second[0], second[1], index,
                        'BAY_{}_{}_X_B'.format(bay, face), aluminum, 1.6); index += 1

        solar = _child(system, 'REV5_MAST_DUAL_SOLAR_CRADLES')
        # Two opposed East/West cradles reach the current panel center radius.
        for x, side in ((27.0, 'EAST'), (-27.0, 'WEST')):
            sign = 1 if x > 0 else -1
            for y in (-15.0, 15.0):
                _member(solar, _point(sign * _half_at(102.0), y, 102.0),
                        _point(x, y, 105.0), index,
                        '{}_LOWER_PANEL_CRADLE'.format(side), aluminum, 2.0); index += 1
                _member(solar, _point(sign * _half_at(129.0), y, 129.0),
                        _point(x, y, 129.0), index,
                        '{}_UPPER_PANEL_CRADLE'.format(side), aluminum, 2.0); index += 1

        top = _child(system, 'REV5_MAST_SENSOR_PLATFORM')
        _plate(top, 129.0, 15.0, '8 mm', 'TOP_SENSOR_PLATFORM_6061', aluminum)
        _member(top, _point(-15.0, 0, 130.0), _point(15.0, 0, 130.0), index,
                'TOP_SENSOR_CROSS_X', aluminum, 2.0); index += 1
        _member(top, _point(0, -15.0, 130.0), _point(0, 15.0, 130.0), index,
                'TOP_SENSOR_CROSS_Y', aluminum, 2.0)

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-MAST-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'Architecture', 'Four-leg tapered marine mast with full face bracing')
        system.attributes.add('PROJECT_FALCON_01', 'SolarInterface', 'Two opposed isolated panel cradles; verify purchased-panel holes')
        system.attributes.add('PROJECT_FALCON_01', 'PodClearance', 'Sealed 320 mm pod retained inside lower mast')
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'FEA, wind, fatigue, vibration and fastener checks required before fabrication')

        for name in ('REV5_POD_DUAL_SOLAR_FRAME', 'TWO_SIDE_SOLAR_FRAME_V3',
                     'DUAL_SOLAR_COMPACT_FRAME_V2', 'COMPACT_ELEVATED_UPPER_TOWER',
                     'UPPER_EQUIPMENT_FRAME'):
            old = _find(root, name)
            if old:
                old.isLightBulbOn = False
        occurrence.isLightBulbOn = True

        app.activeViewport.fit()
        ui.messageBox(
            'REV5_TAPERED_MARINE_MAST completed.\n\n'
            'Reference-inspired tapered marine mast\n'
            'Base/shoulder/top: 420 / 380 / 260 mm; height: 800 mm\n'
            'Four 32 mm two-stage legs; lower bay clears the sealed pod\n'
            'Five horizontal rail levels and full-face X-bracing\n'
            'Two opposed 30 W solar cradles\n'
            'Compact top sensor platform\n'
            'Earlier frame variants hidden, not deleted.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_TAPERED_MARINE_MAST failed:\n\n{}'.format(traceback.format_exc()), 'PROJECT FALCON-01')
