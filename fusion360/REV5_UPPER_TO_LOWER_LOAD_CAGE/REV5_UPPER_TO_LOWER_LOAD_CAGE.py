import adsk.core
import adsk.fusion
import math
import traceback


UPPER_Z = 49.0
LOWER_Z = 36.0
UPPER_HALF = 21.0
LOWER_RADIUS = 33.6


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


def _child(parent, name):
    occurrence = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


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
    feature = component.features.pipeFeatures.add(input_)
    feature.name = 'PIPE_{:03d}_{}'.format(index, name)
    body = feature.bodies.item(0)
    body.name = name + '_6061_T6'
    if material:
        body.material = material


def _pad(component, center, index, aluminum, rubber):
    for offset, thickness, material, suffix in (
            (0.0, '6 mm', aluminum, '6061_PLATE'),
            (0.6, '4 mm', rubber, 'EPDM_ISOLATOR')):
        plane_input = component.constructionPlanes.createInput()
        plane_input.setByOffset(component.xYConstructionPlane,
                                _value('{} mm'.format((center.z + offset) * 10)))
        plane = component.constructionPlanes.add(plane_input)
        sketch = component.sketches.add(plane)
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            _point(center.x - 3.5, center.y - 3.5, 0),
            _point(center.x + 3.5, center.y + 3.5, 0)
        )
        input_ = component.features.extrudeFeatures.createInput(
            sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        input_.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        body = component.features.extrudeFeatures.add(input_).bodies.item(0)
        body.name = 'UPPER_CAGE_PAD_{:02d}_{}'.format(index, suffix)
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
        if _find(root, 'REV5_UPPER_TO_LOWER_LOAD_CAGE'):
            raise RuntimeError('REV5_UPPER_TO_LOWER_LOAD_CAGE already exists; nothing was changed.')
        for required in ('REV5_MAIN_BUOY_FRAME_SUPPORT', 'REV5_TAPERED_MARINE_MAST'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_load_cage_primary_OD', '32 mm', 'mm', 'Four primary load-transfer struts')
        _parameter(p, 'rev5_load_cage_knee_OD', '20 mm', 'mm', 'Eight anti-racking knee braces')
        _parameter(p, 'rev5_load_cage_lower_radius', '336 mm', 'mm', 'Lower split-clamp attachment radius')
        _parameter(p, 'rev5_load_cage_upper_spacing', '420 mm', 'mm', 'Mast foot square spacing')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_UPPER_TO_LOWER_LOAD_CAGE'
        aluminum = _material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        rubber = _material(app, ('EPDM', 'Rubber', 'Neoprene', 'Silicone Rubber'))
        legs = _child(system, 'LOAD_CAGE_PRIMARY_STRUTS')
        knees = _child(system, 'LOAD_CAGE_KNEE_BRACING')
        pads = _child(system, 'LOAD_CAGE_ISOLATED_MOUNTING_PADS')
        index = 1

        corners = ((1, 1, 'NE'), (-1, 1, 'NW'), (-1, -1, 'SW'), (1, -1, 'SE'))
        for sx, sy, label in corners:
            angle = math.atan2(sy, sx)
            upper = _point(sx * UPPER_HALF, sy * UPPER_HALF, UPPER_Z)
            lower = _point(LOWER_RADIUS * math.cos(angle),
                           LOWER_RADIUS * math.sin(angle), LOWER_Z)
            _member(legs, lower, upper, index,
                    '{}_PRIMARY_LOAD_STRUT'.format(label), aluminum, 3.2)
            _pad(pads, upper, index, aluminum, rubber)
            index += 1

            tangent_x = -math.sin(angle) * 5.0
            tangent_y = math.cos(angle) * 5.0
            for sign, suffix in ((-1, 'A'), (1, 'B')):
                knee_start = _point(lower.x + sign * tangent_x,
                                    lower.y + sign * tangent_y, LOWER_Z + 2.0)
                _member(knees, knee_start, upper, index,
                        '{}_KNEE_BRACE_{}'.format(label, suffix), aluminum, 2.0)
                index += 1

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-LC-R5-001')
        system.attributes.add('PROJECT_FALCON_01', 'LoadPath',
                              'Tapered mast feet to primary struts to lower split-clamp frame')
        system.attributes.add('PROJECT_FALCON_01', 'Fasteners',
                              'M10 316L with insulating sleeves, washers and anti-seize')
        system.attributes.add('PROJECT_FALCON_01', 'ShellProtection',
                              'No HDPE penetration; loads enter existing metal clamp frame')
        system.attributes.add('PROJECT_FALCON_01', 'Validation',
                              'FEA, overturning, fatigue, weld/bolt and clamp-pressure checks required')

        app.activeViewport.fit()
        ui.messageBox(
            'REV5_UPPER_TO_LOWER_LOAD_CAGE completed.\n\n'
            'Four 32 mm mast-to-lower-frame load struts\n'
            'Eight 20 mm anti-racking knee braces\n'
            'EPDM-isolated upper mounting pads\n'
            'No existing component moved, cut or deleted.\n\n'
            'Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_UPPER_TO_LOWER_LOAD_CAGE failed:\n\n{}'.format(
                traceback.format_exc()), 'PROJECT FALCON-01')
