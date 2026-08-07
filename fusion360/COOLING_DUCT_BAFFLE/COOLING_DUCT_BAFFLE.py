import adsk.core
import adsk.fusion
import math
import traceback


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _find_occurrence(root, name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == name.upper():
            return occurrence
    return None


def _rectangle(sketch, x_min, y_min, x_max, y_max):
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x_min, y_min, 0),
        adsk.core.Point3D.create(x_max, y_max, 0)
    )


def _assign_material(app, body):
    for library in app.materialLibraries:
        for name in ('ABS Plastic', 'ABS', 'Plastic'):
            material = library.materials.itemByName(name)
            if material:
                body.material = material
                return True
    return False


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Open PROJECT FALCON-01 before running this script.')

        root = design.rootComponent
        if _find_occurrence(root, 'COOLING_DUCT_BAFFLE'):
            raise RuntimeError(
                'COOLING_DUCT_BAFFLE already exists; non-destructive mode made no changes.'
            )
        lower_occurrence = _find_occurrence(root, 'LOWER_HOT_TRAY')
        if not lower_occurrence:
            raise RuntimeError('LOWER_HOT_TRAY component was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'duct_width', '135 mm', 'mm', 'Hot-bay channel width')
        _add_parameter(parameters, 'duct_depth', '305 mm', 'mm', 'Intake-to-exhaust channel length')
        _add_parameter(parameters, 'duct_cover_thickness', '3 mm', 'mm', 'ABS cover thickness')
        _add_parameter(parameters, 'duct_flange_thickness', '4 mm', 'mm', 'Side flange thickness')
        _add_parameter(parameters, 'duct_flange_depth', '35 mm', 'mm', 'Downward sealing flange')
        _add_parameter(parameters, 'duct_service_clearance', '8 mm', 'mm', 'Cable and removal clearance')

        width = parameters.itemByName('duct_width').value
        depth = parameters.itemByName('duct_depth').value
        flange = parameters.itemByName('duct_flange_thickness').value

        # Center the channel in the isolated right-side electronics bay.
        lower_z = lower_occurrence.transform2.translation.z
        transform = adsk.core.Matrix3D.create()
        transform.setToRotation(
            math.pi,
            adsk.core.Vector3D.create(1, 0, 0),
            adsk.core.Point3D.create(0, 0, 0)
        )
        transform.translation = adsk.core.Vector3D.create(17.1, 0, lower_z + 22.0)
        occurrence = root.occurrences.addNewComponent(transform)
        component = occurrence.component
        component.name = 'COOLING_DUCT_BAFFLE'
        extrudes = component.features.extrudeFeatures

        cover_sketch = component.sketches.add(component.xYConstructionPlane)
        cover_sketch.name = 'SKETCH_01_DUCT_COVER'
        _rectangle(cover_sketch, -width / 2.0, -depth / 2.0,
                   width / 2.0, depth / 2.0)
        cover_input = extrudes.createInput(
            cover_sketch.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        cover_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                _value('duct_cover_thickness')
            ),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        cover_feature = extrudes.add(cover_input)
        cover_feature.name = 'EXTRUDE_01_DUCT_COVER'
        body = cover_feature.bodies.item(0)
        body.name = 'COOLING_DUCT_BAFFLE_BODY'

        flange_sketch = component.sketches.add(component.xYConstructionPlane)
        flange_sketch.name = 'SKETCH_02_DUCT_FLANGES'
        _rectangle(flange_sketch, -width / 2.0, -depth / 2.0,
                   -width / 2.0 + flange, depth / 2.0)
        _rectangle(flange_sketch, width / 2.0 - flange, -depth / 2.0,
                   width / 2.0, depth / 2.0)
        profiles = adsk.core.ObjectCollection.create()
        for index in range(flange_sketch.profiles.count):
            profiles.add(flange_sketch.profiles.item(index))
        flange_input = extrudes.createInput(
            profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        flange_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('duct_flange_depth')),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        flange_feature = extrudes.add(flange_input)
        flange_feature.name = 'EXTRUDE_02_DUCT_SIDE_FLANGES'

        body = component.bRepBodies.itemByName('COOLING_DUCT_BAFFLE_BODY')
        assigned = _assign_material(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-CDB-001')
        component.attributes.add('PROJECT_FALCON_01', 'AirPath', 'Intake to MPPT/DC-DC to mini PC to exhaust')
        component.attributes.add('PROJECT_FALCON_01', 'BatteryIsolation', 'No hot exhaust recirculation')
        component.attributes.add('PROJECT_FALCON_01', 'Service', 'Removable cover')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign ABS manually if unavailable locally.'
        ui.messageBox(
            'COOLING_DUCT_BAFFLE completed as a separate removable component.\n\n'
            'Channel: 135 x 305 mm\nCover: 3 mm ABS\nFlanges: 4 x 35 mm\n'
            'Air order: MPPT/DC-DC, then mini PC, then exhaust.\n'
            'Battery hot-air recirculation is blocked.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'COOLING_DUCT_BAFFLE generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )

