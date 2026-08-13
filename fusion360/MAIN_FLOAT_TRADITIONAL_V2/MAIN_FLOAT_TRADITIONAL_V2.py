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


def _find_hdpe(app):
    for library in app.materialLibraries:
        for name in ('HDPE', 'High Density Polyethylene', 'High-density polyethylene'):
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _largest_profile(sketch, label):
    """Return the intended closed region when Fusion reports split regions."""
    count = sketch.profiles.count
    if count < 1:
        raise RuntimeError(
            '{} did not produce a closed profile (Fusion reported 0 regions).'.format(label)
        )
    largest = sketch.profiles.item(0)
    largest_area = -1.0
    for index in range(count):
        profile = sketch.profiles.item(index)
        try:
            area = profile.areaProperties().area
        except Exception:
            area = 0.0
        if area > largest_area:
            largest = profile
            largest_area = area
    return largest


def _outer_profile(sketch):
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    axis_top = adsk.core.Point3D.create(0, -38.0, 0)
    rim_top = adsk.core.Point3D.create(32.5, -38.0, 0)
    shoulder = adsk.core.Point3D.create(32.5, 0, 0)
    lower_side = adsk.core.Point3D.create(31.5, 4.0, 0)
    lower_mid = adsk.core.Point3D.create(22.0, 15.0, 0)
    keel_side = adsk.core.Point3D.create(10.0, 22.0, 0)
    keel_tip = adsk.core.Point3D.create(0, 24.0, 0)
    # Keep the centerline as a normal profile boundary. Fusion can use this
    # boundary as the revolve axis, and the profile remains closed.
    axis = lines.addByTwoPoints(axis_top, keel_tip)
    lines.addByTwoPoints(axis_top, rim_top)
    lines.addByTwoPoints(rim_top, shoulder)
    arcs.addByThreePoints(shoulder, lower_side, lower_mid)
    arcs.addByThreePoints(lower_mid, keel_side, keel_tip)
    return axis


def _inner_cavity_profile(sketch):
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    axis_top = adsk.core.Point3D.create(0, -38.0, 0)
    inner_rim = adsk.core.Point3D.create(31.9, -38.0, 0)
    inner_lower = adsk.core.Point3D.create(31.9, -0.6, 0)
    inner_mid = adsk.core.Point3D.create(21.4, 14.4, 0)
    inner_keel = adsk.core.Point3D.create(9.4, 21.4, 0)
    inner_tip = adsk.core.Point3D.create(0, 23.4, 0)
    # This line closes the cavity profile and also serves as its revolve axis.
    axis = lines.addByTwoPoints(axis_top, inner_tip)
    lines.addByTwoPoints(axis_top, inner_rim)
    lines.addByTwoPoints(inner_rim, inner_lower)
    arcs.addByThreePoints(inner_lower, adsk.core.Point3D.create(29.0, 6.0, 0), inner_mid)
    arcs.addByThreePoints(inner_mid, inner_keel, inner_tip)
    return axis


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
        existing_occurrence = _find_occurrence(root, 'MAIN_FLOAT_TRADITIONAL_V2')
        if existing_occurrence and existing_occurrence.component.bRepBodies.count > 0:
            raise RuntimeError('MAIN_FLOAT_TRADITIONAL_V2 already contains a body; nothing was changed.')
        if not _find_occurrence(root, 'MAIN_FLOAT'):
            raise RuntimeError('The original MAIN_FLOAT was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'traditional_float_OD', '650 mm', 'mm', 'Upper drum diameter')
        _add_parameter(parameters, 'traditional_float_upper_height', '380 mm', 'mm', 'Upper drum height')
        _add_parameter(parameters, 'traditional_float_keel_depth', '240 mm', 'mm', 'Rounded tapered underwater depth')
        _add_parameter(parameters, 'traditional_float_wall', '6 mm', 'mm', 'Marine-grade HDPE wall')
        _add_parameter(parameters, 'traditional_float_total_height', '620 mm', 'mm', 'Overall body height')
        _add_parameter(parameters, 'traditional_float_keel_tip_OD', '200 mm', 'mm', 'Rounded keel zone diameter')

        if existing_occurrence:
            component = existing_occurrence.component
        else:
            occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            component = occurrence.component
            component.name = 'MAIN_FLOAT_TRADITIONAL_V2'

        outer_sketch = component.sketches.add(component.xZConstructionPlane)
        outer_sketch.name = 'SKETCH_01_TRADITIONAL_OUTER_PROFILE'
        outer_axis = _outer_profile(outer_sketch)
        outer_profile = _largest_profile(outer_sketch, 'Outer float sketch')
        revolves = component.features.revolveFeatures
        outer_input = revolves.createInput(
            outer_profile, outer_axis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        outer_input.setAngleExtent(False, _value('360 deg'))
        outer_feature = revolves.add(outer_input)
        outer_feature.name = 'REVOLVE_01_DRUM_AND_ROUNDED_KEEL'
        body = outer_feature.bodies.item(0)
        body.name = 'MAIN_FLOAT_TRADITIONAL_V2_HDPE_BODY'

        cavity_sketch = component.sketches.add(component.xZConstructionPlane)
        cavity_sketch.name = 'SKETCH_02_OPEN_TOP_INNER_CAVITY'
        cavity_axis = _inner_cavity_profile(cavity_sketch)
        cavity_profile = _largest_profile(cavity_sketch, 'Inner cavity sketch')
        cavity_input = revolves.createInput(
            cavity_profile, cavity_axis,
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        cavity_input.setAngleExtent(False, _value('360 deg'))
        cavity_input.participantBodies = [body]
        cavity_feature = revolves.add(cavity_input)
        cavity_feature.name = 'REVOLVE_02_OPEN_TOP_PARAMETRIC_CAVITY'

        hdpe = _find_hdpe(app)
        if hdpe:
            body.material = hdpe
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-MF-002')
        component.attributes.add('PROJECT_FALCON_01', 'Revision', 'Traditional single-body buoy V2')
        component.attributes.add('PROJECT_FALCON_01', 'Material', '6 mm marine-grade HDPE')
        component.attributes.add('PROJECT_FALCON_01', 'Hydrodynamics', 'Rounded tapered 240 mm keel bottom')
        component.attributes.add('PROJECT_FALCON_01', 'Compatibility', 'Original 650 mm top-cap interface retained')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'No existing component moved, hidden, or deleted')

        app.activeViewport.fit()
        ui.messageBox(
            'MAIN_FLOAT_TRADITIONAL_V2 completed.\n\n'
            'Upper drum: 650 mm OD x 380 mm\n'
            'Rounded tapered keel: 240 mm deep\n'
            'Overall height: 620 mm\nWall: 6 mm HDPE\n'
            'Original top-cap interface retained.\n'
            'Old float and stabilizer system were not deleted or hidden.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'MAIN_FLOAT_TRADITIONAL_V2 generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
