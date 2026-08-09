import adsk.core
import adsk.fusion
import math
import traceback


TILT_DEGREES = 12.0


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _tilted_transform(nx, ny, tx, ty):
    angle = math.radians(TILT_DEGREES)
    sine = math.sin(angle)
    cosine = math.cos(angle)
    x_axis = adsk.core.Vector3D.create(tx, ty, 0)
    y_axis = adsk.core.Vector3D.create(nx * cosine, ny * cosine, sine)
    z_axis = adsk.core.Vector3D.create(-nx * sine, -ny * sine, cosine)
    # Preserve the original lower-edge center at R280 mm / Z416 mm.
    center_radius = 28.0 - 22.5 * sine
    center_z = 41.6 + 22.5 * cosine
    origin = adsk.core.Point3D.create(
        nx * center_radius, ny * center_radius, center_z
    )
    transform = adsk.core.Matrix3D.create()
    transform.setWithCoordinateSystem(origin, x_axis, y_axis, z_axis)
    return transform


def _point(radial, tangent, z, nx, ny, tx, ty):
    return adsk.core.Point3D.create(
        radial * nx + tangent * tx,
        radial * ny + tangent * ty,
        z
    )


def _add_strut(component, start, end, index):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_TILT_STRUT_CENTERLINE'.format(index)
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
    feature.name = 'PIPE_{:02d}_SOLAR_TILT_STRUT'.format(index)
    feature.bodies.item(0).name = 'SOLAR_TILT_STRUT_{:02d}_6061'.format(index)


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
        if _find_occurrence(root, 'SOLAR_PANEL_TILT_BRACKETS'):
            raise RuntimeError('Solar-panel tilt upgrade already exists; nothing was changed.')

        placements = (
            ('SOLAR_PANEL_01_NORTH_+Y', 0, 1, 1, 0),
            ('SOLAR_PANEL_02_EAST_+X', 1, 0, 0, -1),
            ('SOLAR_PANEL_03_SOUTH_-Y', 0, -1, -1, 0),
            ('SOLAR_PANEL_04_WEST_-X', -1, 0, 0, 1)
        )
        targets = []
        for name, nx, ny, tx, ty in placements:
            occurrence = _find_occurrence(root, name)
            if not occurrence:
                raise RuntimeError('{} was not found; nothing was changed.'.format(name))
            targets.append((occurrence, nx, ny, tx, ty))

        parameters = design.userParameters
        _add_parameter(parameters, 'solar_panel_tilt_from_vertical', '12 deg', 'deg', 'Safe inward four-panel tilt')
        _add_parameter(parameters, 'solar_tilt_strut_diameter', '12 mm', 'mm', '6061-T6 support rod diameter')

        for occurrence, nx, ny, tx, ty in targets:
            # Deterministic repair: set the exact target transform every run.
            # This does not accumulate or add another 12-degree rotation.
            occurrence.transform2 = _tilted_transform(nx, ny, tx, ty)
            tilt_attribute = occurrence.component.attributes.itemByName(
                'PROJECT_FALCON_01', 'TiltAngle'
            )
            if not tilt_attribute:
                occurrence.component.attributes.add(
                    'PROJECT_FALCON_01', 'TiltAngle',
                    '12 deg inward from vertical'
                )

        bracket_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        bracket_component = bracket_occurrence.component
        bracket_component.name = 'SOLAR_PANEL_TILT_BRACKETS'
        strut_index = 1
        angle = math.radians(TILT_DEGREES)
        panel_center_radius = 28.0 - 22.5 * math.sin(angle)
        panel_center_z = 41.6 + 22.5 * math.cos(angle)
        upper_attach_radius = panel_center_radius - 18.0 * math.sin(angle)
        upper_attach_z = panel_center_z + 18.0 * math.cos(angle)
        for _, nx, ny, tx, ty in targets:
            for tangent in (-12.0, 12.0):
                start = _point(26.0, tangent, 87.0, nx, ny, tx, ty)
                end = _point(
                    upper_attach_radius, tangent, upper_attach_z,
                    nx, ny, tx, ty
                )
                _add_strut(bracket_component, start, end, strut_index)
                strut_index += 1

        aluminum = _find_aluminum(app)
        if aluminum:
            for body in bracket_component.bRepBodies:
                body.material = aluminum
        bracket_component.attributes.add(
            'PROJECT_FALCON_01', 'PartNumber', 'FALCON-SPT-001'
        )
        bracket_component.attributes.add(
            'PROJECT_FALCON_01', 'Construction',
            'Eight 12 mm 6061-T6 upper tilt-support struts'
        )
        bracket_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety',
            'Only the four explicitly approved solar-panel occurrences were reoriented'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'SOLAR_PANEL_TILT_UPGRADE completed.\n\n'
            'Tilt: 12 degrees inward from vertical\n'
            'Lower panel edges retained at their original mounting line\n'
            '8 separate 12 mm aluminum support struts added\n'
            'Frame, sensors, buoy, and all other components were not moved.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'SOLAR_PANEL_TILT_UPGRADE failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
