import adsk.core
import adsk.fusion
import math
import traceback


TOP_Z = 129.0
TOP_HALF = 13.0
UPPER_RING_Z = 48.0
LOWER_RING_Z = 3.0
OUTER_RADIUS = 36.5


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
                result = library.materials.itemByName(name)
            except Exception:
                result = None
            if result:
                return result
    return None


def _child(parent, name):
    occurrence = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


def _plane(component, z_mm, name):
    input_ = component.constructionPlanes.createInput()
    input_.setByOffset(component.xYConstructionPlane, _value('{} mm'.format(z_mm)))
    plane = component.constructionPlanes.add(input_)
    plane.name = name
    return plane


def _ring(component, z_mm, outer_radius, inner_radius, thickness, name, material):
    sketch = component.sketches.add(_plane(component, z_mm, 'PLANE_' + name))
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(_point(0, 0, 0), outer_radius)
    circles.addByCenterRadius(_point(0, 0, 0), inner_radius)
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    profile = min(profiles, key=lambda item: item.areaProperties().area)
    input_ = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
                            adsk.fusion.ExtentDirections.PositiveExtentDirection)
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _member(component, start, end, index, name, material, diameter):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:03d}_{}'.format(index, name)
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
    body.name = name + '_6061_T6'
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
        if _find(root, 'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2'):
            raise RuntimeError('REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2 already exists; nothing was changed.')
        for required in ('REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE',
                         'REV5_TAPERED_MARINE_MAST', 'REV5_MAIN_BUOY_FRAME_SUPPORT'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_cage_v2_primary_OD', '32 mm', 'mm', 'Continuous primary support tube OD')
        _parameter(p, 'rev5_cage_v2_top_z', '1290 mm', 'mm', 'Top mast structural connection')
        _parameter(p, 'rev5_cage_v2_outer_radius', '365 mm', 'mm', 'Tube center radius outside float')
        _parameter(p, 'rev5_cage_v2_lower_collar_OD', '760 mm', 'mm', 'Lower structural collar OD')
        _parameter(p, 'rev5_cage_v2_lower_collar_ID', '696 mm', 'mm', 'Lined lower collar ID')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene', 'Silicone Rubber'))
        upper = _child(system, 'TOP_MAST_TO_UPPER_RING_CONTINUOUS_LEGS')
        lower = _child(system, 'UPPER_RING_TO_LOWER_COLLAR_VERTICAL_LEGS')
        collar = _child(system, 'LOWER_KEEL_STRUCTURAL_COLLAR_V2')
        _ring(collar, 15, 38.0, 34.8, '30 mm', 'LOWER_SPLIT_COLLAR_6061', aluminum)
        _ring(collar, 15, 34.8, 34.5, '30 mm', 'LOWER_COLLAR_EPDM_LINER', rubber)
        index = 1

        for sx, sy, label in ((1, 1, 'NE'), (-1, 1, 'NW'),
                              (-1, -1, 'SW'), (1, -1, 'SE')):
            angle = math.atan2(sy, sx)
            ux, uy = math.cos(angle), math.sin(angle)
            top = _point(sx * TOP_HALF, sy * TOP_HALF, TOP_Z)
            shoulder = _point(OUTER_RADIUS * ux, OUTER_RADIUS * uy, UPPER_RING_Z)
            bottom = _point(OUTER_RADIUS * ux, OUTER_RADIUS * uy, LOWER_RING_Z)
            _member(upper, top, shoulder, index,
                    '{}_TOP_TO_UPPER_RING_LEG'.format(label), aluminum, 3.2)
            index += 1
            _member(lower, shoulder, bottom, index,
                    '{}_UPPER_RING_TO_BOTTOM_LEG'.format(label), aluminum, 3.2)
            index += 1

        collar.attributes.add('PROJECT_FALCON_01', 'Fabrication',
                              'Two bolted 6061-T6 halves with continuous EPDM liner')
        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-FHC-R5-002')
        system.attributes.add('PROJECT_FALCON_01', 'Correction',
                              'Primary tubes begin at top mast corners, not mast feet')
        system.attributes.add('PROJECT_FALCON_01', 'LoadPath',
                              'Top mast corners to upper frame ring to external tubes to lower collar')
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'FEA, drag, fatigue, righting, clamp and collision checks required')

        old = _find(root, 'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE')
        if old:
            old.isLightBulbOn = False
        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2 completed.\n\n'
            'Corrected: tubes begin at the TOP mast corners\n'
            'Four sloping legs continue to the upper buoy ring\n'
            'Four vertical legs continue to the lower structural collar\n'
            'V1 hidden, not deleted; no existing part moved.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2 failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
