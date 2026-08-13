import adsk.core
import adsk.fusion
import traceback


def _find_occurrence(root, name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == name.upper():
            return occurrence
    return None


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


def _tube(component, start, end, index, label):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_{}'.format(index, label)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    pipes = component.features.pipeFeatures
    pipe_input = pipes.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(2.0)
    pipe_input.isHollow = True
    pipe_input.sectionThickness = adsk.core.ValueInput.createByReal(0.2)
    feature = pipes.add(pipe_input)
    feature.name = 'PIPE_{:02d}_{}'.format(index, label)
    feature.bodies.item(0).name = '{}_6061_TUBE'.format(label)


def _find_aluminum(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


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
        if _find_occurrence(root, 'TWO_SIDE_SOLAR_FRAME_V3'):
            raise RuntimeError('TWO_SIDE_SOLAR_FRAME_V3 already exists; nothing was changed.')
        if not _find_occurrence(root, 'DUAL_30W_SOLAR_ARRAY'):
            raise RuntimeError('DUAL_30W_SOLAR_ARRAY was not found; nothing was changed.')

        parameters = design.userParameters
        _add_parameter(parameters, 'two_side_frame_tube_OD', '20 mm', 'mm', 'Round low-drag aluminum tube')
        _add_parameter(parameters, 'two_side_frame_tube_wall', '2 mm', 'mm', 'Tube wall thickness')
        _add_parameter(parameters, 'two_side_frame_half_spacing', '180 mm', 'mm', 'East/West side-frame center')
        _add_parameter(parameters, 'two_side_frame_width', '360 mm', 'mm', 'Each panel-frame rail width')
        _add_parameter(parameters, 'two_side_frame_base_z', '550 mm', 'mm', 'Side-frame base elevation')
        _add_parameter(parameters, 'two_side_frame_top_z', '1170 mm', 'mm', 'Side-frame top elevation')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        frame = occurrence.component
        frame.name = 'TWO_SIDE_SOLAR_FRAME_V3'
        index = 1

        # Exactly two panel-support planes: East (+X) and West (-X).
        for side_index, x in enumerate((18.0, -18.0), 1):
            side = 'EAST' if x > 0 else 'WEST'
            for y in (-18.0, 18.0):
                _tube(
                    frame, _point(x, y, 55.0), _point(x, y, 117.0),
                    index, '{}_VERTICAL_POST'.format(side)
                )
                index += 1
            for z, rail in ((55.0, 'LOWER'), (86.0, 'MIDDLE'), (117.0, 'UPPER')):
                _tube(
                    frame, _point(x, -18.0, z), _point(x, 18.0, z),
                    index, '{}_{}_RAIL'.format(side, rail)
                )
                index += 1

        # Minimal connections keep the two sides rigid and carry the top deck.
        for y, label in ((-18.0, 'REAR'), (18.0, 'FRONT')):
            _tube(
                frame, _point(-18.0, y, 55.0), _point(18.0, y, 55.0),
                index, 'LOWER_{}_TIE'.format(label)
            )
            index += 1
        _tube(frame, _point(-18.0, 0, 117.0), _point(18.0, 0, 117.0),
              index, 'TOP_SENSOR_CROSSBAR')

        aluminum = _find_aluminum(app)
        if aluminum:
            for body in frame.bRepBodies:
                body.material = aluminum
        frame.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-TSF-003')
        frame.attributes.add('PROJECT_FALCON_01', 'Architecture', 'East and West open side frames only')
        frame.attributes.add('PROJECT_FALCON_01', 'Tube', '20 x 2 mm round 6061-T6')
        frame.attributes.add('PROJECT_FALCON_01', 'WindArea', 'No North/South panel frames or circular rings')

        for name in (
            'UPPER_EQUIPMENT_FRAME', 'UPPER_FRAME_SUPPORT_STANCHIONS',
            'COMPACT_ELEVATED_UPPER_TOWER', 'DUAL_SOLAR_COMPACT_FRAME_V2',
            'SOLAR_PANEL_ELEVATION_SUPPORTS'
        ):
            old = _find_occurrence(root, name)
            if old:
                old.isLightBulbOn = False
        occurrence.isLightBulbOn = True

        app.activeViewport.fit()
        ui.messageBox(
            'TWO_SIDE_SOLAR_FRAME_V3 completed.\n\n'
            'Frame sides: East and West only\n'
            'No North/South frames and no circular rings\n'
            'Tube: 20 mm OD x 2 mm wall 6061-T6\n'
            'Height: Z550 to Z1170 mm\n'
            'Minimal top sensor crossbar included\n'
            'Previous frames hidden, not deleted.\n\n'
            'Click Capture Position, then save.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'TWO_SIDE_SOLAR_FRAME_V3 failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
