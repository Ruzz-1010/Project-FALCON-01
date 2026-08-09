import adsk.core
import adsk.fusion
import traceback


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


def _add_pipe_segment(component, start, end, index, body_name,
                      outside_diameter_cm=7.6, wall_cm=0.3):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_DUCT_CENTERLINE'.format(index)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    pipes = component.features.pipeFeatures
    pipe_input = pipes.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(outside_diameter_cm)
    pipe_input.isHollow = True
    pipe_input.sectionThickness = adsk.core.ValueInput.createByReal(wall_cm)
    feature = pipes.add(pipe_input)
    feature.name = 'PIPE_{:02d}_HOLLOW_DUCT'.format(index)
    feature.bodies.item(0).name = body_name


def _build_duct(component, side_sign, is_exhaust):
    fan_x = 17.0
    fan_y = 17.0 * side_sign
    hidden_x = 0
    hidden_y = 21.0 * side_sign
    hood_y = 25.0 * side_sign
    fan_z = 13.0
    cap_z = 40.0
    top_z = 80.0 if is_exhaust else 76.0
    outlet_z = top_z - 7.0
    prefix = 'EXHAUST' if is_exhaust else 'INTAKE'

    _add_pipe_segment(
        component,
        adsk.core.Point3D.create(fan_x, fan_y, fan_z),
        adsk.core.Point3D.create(fan_x, fan_y, cap_z),
        1, prefix + '_01_VERTICAL_FAN_TO_TOP_CAP'
    )
    _add_pipe_segment(
        component,
        adsk.core.Point3D.create(fan_x, fan_y, cap_z),
        adsk.core.Point3D.create(hidden_x, hidden_y, cap_z),
        2, prefix + '_02_TOP_CAP_TO_HIDDEN_RISER'
    )
    _add_pipe_segment(
        component,
        adsk.core.Point3D.create(hidden_x, hidden_y, cap_z),
        adsk.core.Point3D.create(hidden_x, hidden_y, top_z),
        3, prefix + '_03_HIDDEN_SOLAR_REAR_RISER'
    )
    _add_pipe_segment(
        component,
        adsk.core.Point3D.create(hidden_x, hidden_y, top_z),
        adsk.core.Point3D.create(hidden_x, hood_y, top_z),
        4, prefix + '_04_GOOSE_NECK_TOP'
    )
    _add_pipe_segment(
        component,
        adsk.core.Point3D.create(hidden_x, hood_y, top_z),
        adsk.core.Point3D.create(hidden_x, hood_y, outlet_z),
        5, prefix + '_05_DOWNWARD_RAIN_OUTLET'
    )
    # Compact vertical sealed collar where the duct passes through the top cover.
    _add_pipe_segment(
        component,
        adsk.core.Point3D.create(fan_x, fan_y, 38.5),
        adsk.core.Point3D.create(fan_x, fan_y, 41.5),
        6, prefix + '_06_TOP_CAP_BULKHEAD_COLLAR', 10.0, 1.2
    )
    component.attributes.add(
        'PROJECT_FALCON_01', 'Airflow',
        'Hot air out' if is_exhaust else 'Filtered cool air in'
    )
    component.attributes.add(
        'PROJECT_FALCON_01', 'Protection',
        'Top-cover bulkhead, solar-rear hidden riser, and down-facing rain outlet'
    )


def _find_hdpe(app):
    for library in app.materialLibraries:
        for name in ('HDPE', 'High Density Polyethylene', 'Polyethylene, High Density'):
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _cut_top_cap_ports(root):
    cap_occurrence = _find_occurrence(root, 'TOP_CAP')
    if not cap_occurrence:
        raise RuntimeError('TOP_CAP was not found.')
    component = cap_occurrence.component
    extrudes = component.features.extrudeFeatures
    if extrudes.itemByName('CUT_01_SEALED_INTAKE_EXHAUST_PORTS'):
        raise RuntimeError('TOP_CAP vent penetrations already exist; nothing was changed.')
    body = component.bRepBodies.itemByName('TOP_CAP_HDPE_BODY')
    if not body:
        raise RuntimeError('TOP_CAP_HDPE_BODY was not found.')
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_VENT_01_TOP_CAP_PENETRATIONS'
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(17.0, -17.0, 0), 4.1)
    circles.addByCenterRadius(adsk.core.Point3D.create(17.0, 17.0, 0), 4.1)
    profiles = adsk.core.ObjectCollection.create()
    for index in range(sketch.profiles.count):
        profiles.add(sketch.profiles.item(index))
    cut_input = extrudes.createInput(
        profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    cut_input.participantBodies = [body]
    cut_input.setTwoSidesExtent(
        adsk.fusion.ThroughAllExtentDefinition.create(),
        adsk.fusion.ThroughAllExtentDefinition.create()
    )
    feature = extrudes.add(cut_input)
    feature.name = 'CUT_01_SEALED_INTAKE_EXHAUST_PORTS'


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
        if _find_occurrence(root, 'MAIN_BUOY_VENT_DUCTS'):
            raise RuntimeError('MAIN_BUOY_VENT_DUCTS already exists; nothing was changed.')
        for required in (
            'MAIN_FLOAT', 'ELECTRONICS_BOX_V3',
            'INTAKE_FAN_MODULE', 'EXHAUST_FAN_MODULE'
        ):
            if not _find_occurrence(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        parameters = design.userParameters
        _add_parameter(parameters, 'vent_duct_OD', '76 mm', 'mm', 'Compact marine duct outside diameter')
        _add_parameter(parameters, 'vent_duct_ID', '70 mm', 'mm', 'Low-restriction duct inside diameter')
        _add_parameter(parameters, 'vent_duct_wall', '3 mm', 'mm', 'Marine HDPE duct wall')
        _add_parameter(parameters, 'vent_bulkhead_OD', '100 mm', 'mm', 'Compact sealed top-cover collar')
        _add_parameter(parameters, 'intake_riser_top_z', '760 mm', 'mm', 'Intake gooseneck beside solar-panel frame')
        _add_parameter(parameters, 'exhaust_riser_top_z', '800 mm', 'mm', 'Exhaust above intake behind solar-panel frame')

        # Explicitly approved edit: two sealed penetrations in TOP_CAP only.
        _cut_top_cap_ports(root)

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'MAIN_BUOY_VENT_DUCTS'
        hdpe = _find_hdpe(app)

        intake_occurrence = system_component.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()
        )
        intake = intake_occurrence.component
        intake.name = 'INTAKE_EXTERNAL_DUCT'
        _build_duct(intake, -1, False)
        intake.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-VD-001')

        exhaust_occurrence = system_component.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()
        )
        exhaust = exhaust_occurrence.component
        exhaust.name = 'EXHAUST_EXTERNAL_DUCT'
        _build_duct(exhaust, 1, True)
        exhaust.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-VD-002')

        if hdpe:
            for child in (intake, exhaust):
                for body in child.bRepBodies:
                    body.material = hdpe
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Opposed intake/exhaust with separated outlet elevations'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety',
            'Only two approved TOP_CAP penetrations were added; no component was moved'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'MAIN_BUOY_VENT_DUCTS completed.\n\n'
            'Compact ducts: 70 mm ID / 76 mm OD\n'
            'Both exit through TOP_CAP and rise hidden behind solar panels.\n'
            'Intake top: 760 mm; exhaust top: 800 mm\n'
            'Both include down-facing rain outlets and 100 mm sealed collars.\n'
            'Only TOP_CAP received two approved sealed penetrations; nothing moved.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'MAIN_BUOY_VENT_DUCTS generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
