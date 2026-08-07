import adsk.core
import adsk.fusion
import math
import traceback


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _point(radius_cm, angle, elevation_cm):
    return adsk.core.Point3D.create(
        radius_cm * math.cos(angle),
        radius_cm * math.sin(angle),
        elevation_cm
    )


def _add_tube(component, start, end, index, body_name):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_TUBE_CENTERLINE'.format(index)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line)
    pipes = component.features.pipeFeatures
    pipe_input = pipes.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.SquarePipeSectionType
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(3.0)
    pipe_input.isHollow = True
    pipe_input.sectionThickness = adsk.core.ValueInput.createByReal(0.3)
    feature = pipes.add(pipe_input)
    feature.name = 'PIPE_{:02d}_30X30X3_TUBE'.format(index)
    feature.bodies.item(0).name = body_name


def _find_aluminum(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            material = library.materials.itemByName(name)
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
        if _find_occurrence(root, 'UPPER_FRAME_SUPPORT_STANCHIONS'):
            raise RuntimeError(
                'UPPER_FRAME_SUPPORT_STANCHIONS already exists; nothing was changed.'
            )
        for required in ('MAIN_SUPPORT_FRAME', 'UPPER_EQUIPMENT_FRAME'):
            if not _find_occurrence(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        parameters = design.userParameters
        _add_parameter(parameters, 'stanchion_tube_size', '30 mm', 'mm', 'Square tube outside size')
        _add_parameter(parameters, 'stanchion_tube_wall', '3 mm', 'mm', '6061-T6 tube wall')
        _add_parameter(parameters, 'stanchion_outer_radius', '365 mm', 'mm', 'Clearance outside main float fairing')
        _add_parameter(parameters, 'stanchion_lower_z', '105 mm', 'mm', 'Lower-frame interface elevation')
        _add_parameter(parameters, 'stanchion_upper_z', '406 mm', 'mm', 'Upper-frame base interface elevation')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'UPPER_FRAME_SUPPORT_STANCHIONS'
        aluminum = _find_aluminum(app)

        for index, angle in enumerate(
            (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4), 1
        ):
            occurrence = system_component.occurrences.addNewComponent(
                adsk.core.Matrix3D.create()
            )
            component = occurrence.component
            component.name = 'UPPER_FRAME_STANCHION_{:02d}'.format(index)

            lower_frame = _point(34.0, angle, 10.5)
            lower_outer = _point(36.5, angle, 10.5)
            upper_outer = _point(36.5, angle, 40.6)
            upper_frame = _point(27.0, angle, 40.6)
            _add_tube(
                component, lower_frame, lower_outer, 1,
                'STANCHION_{:02d}_LOWER_BRACKET'.format(index)
            )
            _add_tube(
                component, lower_outer, upper_outer, 2,
                'STANCHION_{:02d}_VERTICAL_POST'.format(index)
            )
            _add_tube(
                component, upper_outer, upper_frame, 3,
                'STANCHION_{:02d}_UPPER_BRACKET'.format(index)
            )
            if aluminum:
                for body in component.bRepBodies:
                    body.material = aluminum
            component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber',
                'FALCON-UFS-{:03d}'.format(index)
            )
            component.attributes.add(
                'PROJECT_FALCON_01', 'Material', '30 x 30 x 3 mm 6061-T6 tube'
            )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'LoadPath',
            'MAIN_SUPPORT_FRAME directly to UPPER_EQUIPMENT_FRAME base ring'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'ServiceClearance',
            '365 mm post radius clears 650 mm main float and rounded fairings'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing components untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'UPPER_FRAME_SUPPORT_STANCHIONS completed.\n\n'
            '4 separate editable structural stanchions\n'
            'Tube: 30 x 30 x 3 mm 6061-T6\n'
            'Load path: lower MAIN_SUPPORT_FRAME to upper base ring\n'
            'Posts clear the main float and rounded fairing.\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'UPPER_FRAME_SUPPORT_STANCHIONS generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
