import adsk.core
import adsk.fusion
import math
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


def _plane(component, z_mm, name):
    input_ = component.constructionPlanes.createInput()
    input_.setByOffset(component.xYConstructionPlane, _value('{} mm'.format(z_mm)))
    plane = component.constructionPlanes.add(input_)
    plane.name = name
    return plane


def _ring(component, z_mm, outer_cm, inner_cm, thickness, name, material):
    sketch = component.sketches.add(_plane(component, z_mm, 'PLANE_' + name))
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), outer_cm)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), inner_cm)
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


def _member(component, start, end, index, name, material, diameter_cm=2.5):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_{}'.format(index, name)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(diameter_cm)
    input_.isHollow = False
    body = component.features.pipeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _pad(component, x, y, z, index, aluminum, rubber):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    occurrence = component.occurrences.addNewComponent(transform)
    pad = occurrence.component
    pad.name = 'REV5_ISOLATED_FRAME_PAD_{:02d}'.format(index)
    for layer, thickness, material, suffix in ((0, '6 mm', aluminum, '6061_BASE'),
                                                (0.6, '5 mm', rubber, 'EPDM_ISOLATOR')):
        plane = pad.xYConstructionPlane if layer == 0 else _plane(pad, layer * 10, 'PLANE_ISOLATOR')
        sketch = pad.sketches.add(plane)
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(-3.0, -2.5, 0),
            adsk.core.Point3D.create(3.0, 2.5, 0)
        )
        input_ = pad.features.extrudeFeatures.createInput(
            sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        input_.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
                                adsk.fusion.ExtentDirections.PositiveExtentDirection)
        body = pad.features.extrudeFeatures.add(input_).bodies.item(0)
        body.name = 'FRAME_PAD_' + suffix
        if material:
            body.material = material
    pad.attributes.add('PROJECT_FALCON_01', 'Fastener', '2 x M10 316L isolated through deck hardware')


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
        if _find(root, 'REV5_MAIN_BUOY_FRAME_SUPPORT'):
            raise RuntimeError('REV5_MAIN_BUOY_FRAME_SUPPORT already exists; nothing was changed.')
        if not _find(root, 'MAIN_FLOAT_TRADITIONAL_V2'):
            raise RuntimeError('Traditional V2 main float was not found.')

        p = design.userParameters
        _parameter(p, 'rev5_support_clamp_ID', '654 mm', 'mm', 'Lined clearance around 650 mm HDPE body')
        _parameter(p, 'rev5_support_clamp_OD', '690 mm', 'mm', 'Two-half clamp outside diameter')
        _parameter(p, 'rev5_support_clamp_height', '70 mm', 'mm', 'Axial clamp-band height')
        _parameter(p, 'rev5_support_deck_OD', '620 mm', 'mm', 'Annular upper service deck diameter')
        _parameter(p, 'rev5_support_deck_ID', '340 mm', 'mm', 'Pod and cap service opening')
        _parameter(p, 'rev5_support_deck_z', '480 mm', 'mm', 'Upper frame support deck elevation')
        _parameter(p, 'rev5_support_riser_OD', '30 mm', 'mm', 'Diagonal 6061-T6 riser diameter')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_MAIN_BUOY_FRAME_SUPPORT'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('Rubber', 'Neoprene', 'EPDM', 'Silicone Rubber'))

        _ring(system, 350, 34.5, 32.7, '70 mm', 'SPLIT_CLAMP_BAND_6061', aluminum)
        _ring(system, 350, 32.7, 32.5, '70 mm', 'EPDM_CLAMP_LINER', rubber)
        _ring(system, 480, 31.0, 17.0, '10 mm', 'ANNULAR_UPPER_SERVICE_DECK_6061', aluminum)

        index = 1
        # Riser attachment points align with the four Revision 5 frame feet.
        for x, y in ((19.0, -20.0), (19.0, 20.0), (-19.0, -20.0), (-19.0, 20.0)):
            angle = math.atan2(y, x)
            lower = adsk.core.Point3D.create(33.6 * math.cos(angle), 33.6 * math.sin(angle), 38.5)
            upper = adsk.core.Point3D.create(x, y, 48.0)
            _member(system, lower, upper, index, 'DIAGONAL_FRAME_RISER_{:02d}'.format(index), aluminum, 3.0)
            _pad(system, x, y, 48.6, index, aluminum, rubber)
            index += 1

        # Eight short gusset struts triangulate both sides of each riser.
        for x, y in ((19.0, -20.0), (19.0, 20.0), (-19.0, -20.0), (-19.0, 20.0)):
            angle = math.atan2(y, x)
            tangent_x, tangent_y = -math.sin(angle) * 4.0, math.cos(angle) * 4.0
            for sign in (-1, 1):
                start = adsk.core.Point3D.create(
                    33.0 * math.cos(angle) + sign * tangent_x,
                    33.0 * math.sin(angle) + sign * tangent_y, 40.0
                )
                end = adsk.core.Point3D.create(x, y, 48.0)
                _member(system, start, end, index, 'RISER_GUSSET_{:02d}'.format(index), aluminum, 1.6)
                index += 1

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-MBS-005')
        system.attributes.add('PROJECT_FALCON_01', 'LoadPath', 'Upper frame feet to annular deck to diagonal risers to lined split clamp')
        system.attributes.add('PROJECT_FALCON_01', 'ShellInterface', 'Non-penetrating EPDM-lined two-half clamp; no HDPE drilling')
        system.attributes.add('PROJECT_FALCON_01', 'Service', '340 mm central opening retains pod/cap service access')
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'Clamp pressure, HDPE creep, fatigue, wind and wave loads require engineering verification')

        app.activeViewport.fit()
        ui.messageBox(
            'REV5_MAIN_BUOY_FRAME_SUPPORT completed.\n\n'
            'EPDM-lined split clamp around 650 mm main buoy\n'
            'Four diagonal 30 mm risers with eight gusset struts\n'
            '620/340 mm annular upper service deck\n'
            'Four isolated pads aligned to Revision 5 frame feet\n'
            'No drilling through the sealed HDPE body\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_MAIN_BUOY_FRAME_SUPPORT failed:\n\n{}'.format(traceback.format_exc()), 'PROJECT FALCON-01')
