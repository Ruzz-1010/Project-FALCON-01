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


def _triangle(sketch):
    lines = sketch.sketchCurves.sketchLines
    # Fusion internal units are cm. These coordinates match the +X arm.
    p1 = adsk.core.Point3D.create(35.0, 8.6, 0)
    p2 = adsk.core.Point3D.create(57.0, 8.6, 0)
    p3 = adsk.core.Point3D.create(43.0, 12.6, 0)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p1)


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xZConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _extrude_gusset(component, plane, direction, feature_name, body_name):
    sketch = component.sketches.add(plane)
    sketch.name = feature_name.replace('EXTRUDE', 'SKETCH')
    _triangle(sketch)
    profile = sketch.profiles.item(0)
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('brace_gusset_thickness')),
        direction
    )
    feature = extrudes.add(extrude_input)
    feature.name = feature_name
    feature.bodies.item(0).name = body_name


def _assign_aluminum(app, bodies):
    material = None
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            material = library.materials.itemByName(name)
            if material:
                break
        if material:
            break
    if not material:
        return False
    for body in bodies:
        body.material = material
    return True


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
        if _find_occurrence(root, 'STABILIZER_ARM_REINFORCEMENT'):
            raise RuntimeError(
                'STABILIZER_ARM_REINFORCEMENT already exists; nothing was changed.'
            )
        if not _find_occurrence(root, 'MAIN_SUPPORT_FRAME'):
            raise RuntimeError('MAIN_SUPPORT_FRAME was not found.')
        if not _find_occurrence(root, 'STABILIZER_ARM'):
            raise RuntimeError('STABILIZER_ARM was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'brace_gusset_thickness', '6 mm', 'mm', 'Twin marine aluminum gusset thickness')
        _add_parameter(parameters, 'brace_gusset_reach', '220 mm', 'mm', 'Length supported along arm')
        _add_parameter(parameters, 'brace_gusset_height', '40 mm', 'mm', 'Vertical triangular reinforcement height')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = 'STABILIZER_ARM_REINFORCEMENT'

        positive_plane = _offset_plane(component, '20 mm', 'PLANE_01_GUSSET_POSITIVE_Y')
        negative_plane = _offset_plane(component, '-20 mm', 'PLANE_02_GUSSET_NEGATIVE_Y')
        _extrude_gusset(
            component,
            positive_plane,
            adsk.fusion.ExtentDirections.PositiveExtentDirection,
            'EXTRUDE_01_POSITIVE_SIDE_GUSSET',
            'BRACE_GUSSET_POSITIVE_6061'
        )
        _extrude_gusset(
            component,
            negative_plane,
            adsk.fusion.ExtentDirections.NegativeExtentDirection,
            'EXTRUDE_02_NEGATIVE_SIDE_GUSSET',
            'BRACE_GUSSET_NEGATIVE_6061'
        )

        assigned = _assign_aluminum(app, component.bRepBodies)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-SAR-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', '6061-T6 marine aluminum')
        component.attributes.add('PROJECT_FALCON_01', 'Construction', 'Twin 6 mm welded triangular gussets')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing parts were not edited or moved')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign 6061-T6 manually if unavailable locally.'
        ui.messageBox(
            'STABILIZER_ARM_REINFORCEMENT completed.\n\n'
            'Twin gussets: 6 mm 6061-T6\n'
            'Supported arm length: 220 mm\n'
            'Existing frame and arm were not edited or moved.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_ARM_REINFORCEMENT generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
