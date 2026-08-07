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


def _find_steel(app):
    for library in app.materialLibraries:
        for name in ('Stainless Steel 316', 'Stainless Steel', 'Steel'):
            material = library.materials.itemByName(name)
            if material:
                return material
    return None


def _build_cable(component, index, angle):
    ballast_radius = 10.8
    cradle_radius = 102.5
    ballast_z = -14.9
    cradle_z = -3.2
    start = adsk.core.Point3D.create(
        ballast_radius * math.cos(angle),
        ballast_radius * math.sin(angle),
        ballast_z
    )
    end = adsk.core.Point3D.create(
        cradle_radius * math.cos(angle),
        cradle_radius * math.sin(angle),
        cradle_z
    )

    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_01_CABLE_CENTERLINE'
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    line.isConstruction = False

    path = component.features.createPath(line)
    pipes = component.features.pipeFeatures
    pipe_input = pipes.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    # This Fusion build requires a resolved real value here (internal unit: cm).
    # 0.4 cm = 4 mm. The resulting Pipe feature remains timeline-editable.
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(0.4)
    pipe_input.isHollow = False
    feature = pipes.add(pipe_input)
    feature.name = 'PIPE_01_316SS_WIRE_ROPE'
    feature.bodies.item(0).name = 'TENSION_CABLE_{:02d}_316SS_BODY'.format(index)
    component.attributes.add(
        'PROJECT_FALCON_01', 'Endpoints',
        'Ballast lug to stabilizer cradle {:02d}'.format(index)
    )


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
        if _find_occurrence(root, 'STABILIZER_TENSION_CABLE_SYSTEM'):
            raise RuntimeError(
                'STABILIZER_TENSION_CABLE_SYSTEM already exists; nothing was changed.'
            )
        for required in ('BALLAST', 'STABILIZER_BUOY_SYSTEM'):
            if not _find_occurrence(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        parameters = design.userParameters
        _add_parameter(parameters, 'tension_cable_diameter', '4 mm', 'mm', '316 stainless wire-rope diameter')
        _add_parameter(parameters, 'tension_cable_ballast_radius', '108 mm', 'mm', 'Ballast shackle-hole radius')
        _add_parameter(parameters, 'tension_cable_cradle_radius', '1025 mm', 'mm', 'Stabilizer cradle center radius')
        _add_parameter(parameters, 'tension_cable_ballast_z', '-149 mm', 'mm', 'Ballast lug cable elevation')
        _add_parameter(parameters, 'tension_cable_cradle_z', '-32 mm', 'mm', 'Lower cradle attachment elevation')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'STABILIZER_TENSION_CABLE_SYSTEM'
        steel = _find_steel(app)

        for index, angle in enumerate((0, math.pi / 2, math.pi, 3 * math.pi / 2), 1):
            cable_occurrence = system_component.occurrences.addNewComponent(
                adsk.core.Matrix3D.create()
            )
            cable_component = cable_occurrence.component
            cable_component.name = 'TENSION_CABLE_{:02d}'.format(index)
            _build_cable(cable_component, index, angle)
            if steel:
                for body in cable_component.bRepBodies:
                    body.material = steel
            cable_component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber',
                'FALCON-TC-{:03d}'.format(index)
            )
            cable_component.attributes.add(
                'PROJECT_FALCON_01', 'Material', '4 mm 316 stainless wire rope'
            )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Four separate editable radial ballast-to-cradle cables'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing components untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'STABILIZER_TENSION_CABLE_SYSTEM completed.\n\n'
            '4 separate editable 316SS wire-rope cables\n'
            'Diameter: 4 mm\n'
            'Connections: ballast lugs to lower stabilizer cradles\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_TENSION_CABLE_SYSTEM generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
