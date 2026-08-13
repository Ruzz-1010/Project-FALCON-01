import adsk.core
import adsk.fusion
import math
import traceback


UPPER_Z = 48.0
LOWER_Z = 3.0
OUTER_TUBE_RADIUS = 36.5
MAST_HALF = 21.0


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
        if _find(root, 'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE'):
            raise RuntimeError('REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE already exists; nothing was changed.')
        for required in ('MAIN_FLOAT_TRADITIONAL_V2', 'REV5_MAIN_BUOY_FRAME_SUPPORT',
                         'REV5_TAPERED_MARINE_MAST'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_external_cage_tube_OD', '32 mm', 'mm', 'Four full-height external support tubes')
        _parameter(p, 'rev5_external_cage_radius', '365 mm', 'mm', 'Tube center radius outside 690 mm fairings')
        _parameter(p, 'rev5_external_cage_upper_z', '480 mm', 'mm', 'Upper metal deck connection elevation')
        _parameter(p, 'rev5_external_cage_lower_z', '30 mm', 'mm', 'Lower fairing/collar center elevation')
        _parameter(p, 'rev5_lower_collar_OD', '760 mm', 'mm', 'Lower structural collar outside diameter')
        _parameter(p, 'rev5_lower_collar_ID', '696 mm', 'mm', 'EPDM-lined clearance over lower HDPE fairing')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene', 'Silicone Rubber'))

        collar = _child(system, 'LOWER_KEEL_STRUCTURAL_SPLIT_COLLAR')
        _ring(collar, 15, 38.0, 34.8, '30 mm', 'LOWER_SPLIT_COLLAR_6061', aluminum)
        _ring(collar, 15, 34.8, 34.5, '30 mm', 'LOWER_COLLAR_EPDM_LINER', rubber)
        collar.attributes.add('PROJECT_FALCON_01', 'Fabrication',
                              'Manufacture as two bolted halves; geometry shown as continuous envelope')

        tubes = _child(system, 'FOUR_FULL_HEIGHT_EXTERNAL_TUBES')
        brackets = _child(system, 'UPPER_AND_LOWER_CAGE_BRACING')
        index = 1
        for sx, sy, label in ((1, 1, 'NE'), (-1, 1, 'NW'),
                              (-1, -1, 'SW'), (1, -1, 'SE')):
            angle = math.atan2(sy, sx)
            ux, uy = math.cos(angle), math.sin(angle)
            upper_outer = _point(OUTER_TUBE_RADIUS * ux, OUTER_TUBE_RADIUS * uy, UPPER_Z)
            lower_outer = _point(OUTER_TUBE_RADIUS * ux, OUTER_TUBE_RADIUS * uy, LOWER_Z)
            mast_foot = _point(sx * MAST_HALF, sy * MAST_HALF, 49.0)

            _member(tubes, upper_outer, lower_outer, index,
                    '{}_FULL_HEIGHT_SUPPORT_TUBE'.format(label), aluminum, 3.2)
            index += 1
            _member(brackets, mast_foot, upper_outer, index,
                    '{}_UPPER_RADIAL_LOAD_TIE'.format(label), aluminum, 2.5)
            index += 1
            _member(brackets, _point(OUTER_TUBE_RADIUS * ux, OUTER_TUBE_RADIUS * uy, 9.0),
                    _point(35.5 * ux, 35.5 * uy, LOWER_Z), index,
                    '{}_LOWER_COLLAR_KNEE'.format(label), aluminum, 2.0)
            index += 1

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-FHC-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'LoadPath',
                              'Upper tapered mast to four external tubes to lower structural collar')
        system.attributes.add('PROJECT_FALCON_01', 'ShellProtection',
                              'Tubes remain outside HDPE; lower collar uses EPDM isolation')
        system.attributes.add('PROJECT_FALCON_01', 'Fasteners',
                              'M10 316L isolated bolts; locking hardware and anti-seize required')
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'FEA, drag, fatigue, righting, clamp pressure and corrosion checks required')

        old = _find(root, 'REV5_UPPER_TO_LOWER_LOAD_CAGE')
        if old:
            old.isLightBulbOn = False
        occurrence.isLightBulbOn = True
        app.activeViewport.fit()
        ui.messageBox(
            'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE completed.\n\n'
            'Four 32 mm tubes from upper mast to buoy bottom\n'
            'Tubes run outside the complete main-float body\n'
            'New 760/696 mm EPDM-lined lower structural collar\n'
            'Old short load cage hidden, not deleted\n'
            'No existing component moved, cut or deleted.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
