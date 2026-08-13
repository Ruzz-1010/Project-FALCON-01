import adsk.core
import adsk.fusion
import math
import traceback


LOWER_Z = 4.5
UPPER_Z = 38.5
LOWER_RADIUS = 36.5
UPPER_RADIUS = 33.6


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


def _member(component, start, end, index, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_FLUSH_SUPPORT_TUBE'.format(index)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(3.2)
    input_.isHollow = False
    body = component.features.pipeFeatures.add(input_).bodies.item(0)
    body.name = 'LOWER_TO_MAIN_FRAME_FLUSH_TUBE_{:02d}_6061'.format(index)
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
        if _find(root, 'REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2'):
            raise RuntimeError('REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2 already exists; nothing was changed.')
        for required in ('REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE',
                         'REV5_MAIN_BUOY_FRAME_SUPPORT'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_lower_cage_v2_tube_OD', '32 mm', 'mm', 'Four corrected support tubes')
        _parameter(p, 'rev5_lower_cage_v2_bottom_radius', '365 mm', 'mm', 'Lower collar tube radius')
        _parameter(p, 'rev5_lower_cage_v2_top_radius', '336 mm', 'mm', 'Main support collar attachment radius')
        _parameter(p, 'rev5_lower_cage_v2_top_z', '385 mm', 'mm', 'Flush attachment within main support clamp')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene', 'Silicone Rubber'))

        collar = _child(system, 'LOWER_BUOY_STRUCTURAL_COLLAR_V2')
        _ring(collar, 30, 38.0, 34.8, '30 mm', 'LOWER_SPLIT_COLLAR_6061', aluminum)
        _ring(collar, 30, 34.8, 34.5, '30 mm', 'LOWER_COLLAR_EPDM_LINER', rubber)
        tubes = _child(system, 'FOUR_INWARD_TAPERED_SUPPORT_TUBES')

        for index, angle in enumerate((45.0, 135.0, 225.0, 315.0), 1):
            radians = math.radians(angle)
            lower = _point(LOWER_RADIUS * math.cos(radians),
                           LOWER_RADIUS * math.sin(radians), LOWER_Z)
            upper = _point(UPPER_RADIUS * math.cos(radians),
                           UPPER_RADIUS * math.sin(radians), UPPER_Z)
            _member(tubes, lower, upper, index, aluminum)

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-LMS-R5-002')
        system.attributes.add('PROJECT_FALCON_01', 'Correction',
                              'Upper tube radius reduced from 365 to 336 mm; overhang removed')
        system.attributes.add('PROJECT_FALCON_01', 'UpperTermination',
                              'Ends at Z=385 mm inside REV5_MAIN_BUOY_FRAME_SUPPORT clamp band')
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'Verify clamp/tube brackets, drag, fatigue and corrosion before fabrication')

        for old_name in ('REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE',
                         'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2',
                         'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE',
                         'REV5_UPPER_TO_LOWER_LOAD_CAGE'):
            old = _find(root, old_name)
            if old:
                old.isLightBulbOn = False
        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2 completed.\n\n'
            'Overhang corrected\n'
            'Lower radius: 365 mm\nUpper attachment radius: 336 mm\n'
            'Upper endpoint: Z=385 mm inside the main support collar\n'
            'Earlier cages hidden, not deleted.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2 failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
