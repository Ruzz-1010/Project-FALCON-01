import adsk.core
import adsk.fusion
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


def _build_rounded_ring(component, body_name):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_01_ROUNDED_RING_PROFILE'
    lines = sketch.sketchCurves.sketchLines
    axis = lines.addByTwoPoints(
        adsk.core.Point3D.create(0, -4.0, 0),
        adsk.core.Point3D.create(0, 4.0, 0)
    )
    axis.isConstruction = True
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(32.0, 0, 0), 2.5
    )
    revolves = component.features.revolveFeatures
    revolve_input = revolves.createInput(
        sketch.profiles.item(0), axis,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    revolve_input.setAngleExtent(False, _value('360 deg'))
    feature = revolves.add(revolve_input)
    feature.name = 'REVOLVE_01_FULL_ROUND_MARINE_RING'
    body = feature.bodies.item(0)
    body.name = body_name
    return body


def _find_hdpe(app):
    for library in app.materialLibraries:
        for name in ('HDPE', 'High Density Polyethylene', 'Polyethylene, High Density'):
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
        if _find_occurrence(root, 'MAIN_FLOAT_EDGE_FAIRING'):
            raise RuntimeError(
                'MAIN_FLOAT_EDGE_FAIRING already exists; nothing was changed.'
            )
        if not _find_occurrence(root, 'MAIN_FLOAT'):
            raise RuntimeError('MAIN_FLOAT was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'fairing_ring_center_radius', '320 mm', 'mm', 'Ring profile center radius')
        _add_parameter(parameters, 'fairing_round_radius', '25 mm', 'mm', 'Full-round edge radius')
        _add_parameter(parameters, 'fairing_upper_z', '350 mm', 'mm', 'Upper ring center elevation')
        _add_parameter(parameters, 'fairing_lower_z', '30 mm', 'mm', 'Lower ring center elevation')
        _add_parameter(parameters, 'fairing_outside_diameter', '690 mm', 'mm', 'Maximum bumper diameter')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'MAIN_FLOAT_EDGE_FAIRING'
        hdpe = _find_hdpe(app)

        for name, elevation, part_number in (
            ('MAIN_FLOAT_UPPER_ROUNDED_FAIRING', 35.0, 'FALCON-MFF-001'),
            ('MAIN_FLOAT_LOWER_ROUNDED_FAIRING', 3.0, 'FALCON-MFF-002')
        ):
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, elevation)
            occurrence = system_component.occurrences.addNewComponent(transform)
            component = occurrence.component
            component.name = name
            body = _build_rounded_ring(component, name + '_HDPE_BODY')
            if hdpe:
                body.material = hdpe
            component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber', part_number
            )
            component.attributes.add(
                'PROJECT_FALCON_01', 'Material', 'Marine-grade HDPE bumper/fairing'
            )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Separate editable upper and lower full-round edge fairings'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety',
            'Main float seal, bottom mount, and all existing components untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'MAIN_FLOAT_EDGE_FAIRING completed.\n\n'
            'Upper and lower full-round radius: 25 mm\n'
            'Maximum outside diameter: 690 mm\n'
            'Both rings are separate editable child components.\n'
            'Top seal and bottom mounting surface remain untouched.\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'MAIN_FLOAT_EDGE_FAIRING generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
