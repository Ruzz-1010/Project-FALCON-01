import adsk.core
import adsk.fusion
import traceback


ELEVATION_CM = 15.0


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


def _raise(occurrence):
    transform = occurrence.transform2.copy()
    translation = transform.translation
    translation.z += ELEVATION_CM
    transform.translation = translation
    occurrence.transform2 = transform


def _point(radial, tangent, z, nx, ny, tx, ty):
    return adsk.core.Point3D.create(
        radial * nx + tangent * tx, radial * ny + tangent * ty, z
    )


def _add_strut(component, start, end, index):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_ELEVATION_STRUT'.format(index)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    pipes = component.features.pipeFeatures
    pipe_input = pipes.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(1.2)
    pipe_input.isHollow = False
    feature = pipes.add(pipe_input)
    feature.name = 'PIPE_{:02d}_SOLAR_ELEVATION_STRUT'.format(index)
    feature.bodies.item(0).name = 'SOLAR_ELEVATION_STRUT_{:02d}_6061'.format(index)


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
        if _find_occurrence(root, 'SOLAR_PANEL_ELEVATION_SUPPORTS'):
            raise RuntimeError('Solar elevation upgrade already exists; nothing was changed.')
        if not _find_occurrence(root, 'UPPER_EQUIPMENT_FRAME'):
            raise RuntimeError('UPPER_EQUIPMENT_FRAME was not found; nothing was changed.')

        names = (
            'SOLAR_PANEL_01_NORTH_+Y', 'SOLAR_PANEL_02_EAST_+X',
            'SOLAR_PANEL_03_SOUTH_-Y', 'SOLAR_PANEL_04_WEST_-X'
        )
        panels = []
        for name in names:
            occurrence = _find_occurrence(root, name)
            if not occurrence:
                raise RuntimeError('{} was not found; nothing was changed.'.format(name))
            panels.append(occurrence)

        _add_parameter(design.userParameters, 'solar_panel_elevation_upgrade',
                       '150 mm', 'mm', 'Approved four-panel upward shift')
        _add_parameter(design.userParameters, 'solar_elevation_strut_diameter',
                       '12 mm', 'mm', '6061-T6 extension diameter')

        for panel in panels:
            _raise(panel)
            if not panel.component.attributes.itemByName(
                    'PROJECT_FALCON_01', 'ElevationUpgrade'):
                panel.component.attributes.add(
                    'PROJECT_FALCON_01', 'ElevationUpgrade', '150 mm upward'
                )

        tilt_brackets = _find_occurrence(root, 'SOLAR_PANEL_TILT_BRACKETS')
        if tilt_brackets:
            _raise(tilt_brackets)

        support_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        supports = support_occurrence.component
        supports.name = 'SOLAR_PANEL_ELEVATION_SUPPORTS'
        directions = (
            (0, 1, 1, 0), (1, 0, 0, -1),
            (0, -1, -1, 0), (-1, 0, 0, 1)
        )
        index = 1
        for nx, ny, tx, ty in directions:
            for tangent in (-12.0, 12.0):
                _add_strut(
                    supports,
                    _point(26.0, tangent, 87.0, nx, ny, tx, ty),
                    _point(26.0, tangent, 102.0, nx, ny, tx, ty),
                    index
                )
                index += 1

        aluminum = _find_aluminum(app)
        if aluminum:
            for body in supports.bRepBodies:
                body.material = aluminum
        supports.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-SPE-001')
        supports.attributes.add('PROJECT_FALCON_01', 'Elevation', '150 mm')
        supports.attributes.add(
            'PROJECT_FALCON_01', 'Safety',
            'Only solar panels and optional tilt brackets were moved'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'SOLAR_PANEL_ELEVATION_UPGRADE completed.\n\n'
            'Four solar panels raised: 150 mm\n'
            'Eight 12 mm aluminum extension struts added\n'
            'Tilt brackets raised when present\n'
            'Buoy, electronics, ballast, and sensors were not moved.\n\n'
            'Click Capture Position, then save.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'SOLAR_PANEL_ELEVATION_UPGRADE failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
