import adsk.core
import adsk.fusion
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


def _remove_known_result(component):
    if component.bRepBodies.count or component.sketches.count:
        raise RuntimeError('ELECTRONICS_BOX already exists; non-destructive mode made no changes.')


def _rectangle(sketch, width, depth):
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2.0, -depth / 2.0, 0),
        adsk.core.Point3D.create(width / 2.0, depth / 2.0, 0)
    )


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _assign_hdpe(app, body):
    for library in app.materialLibraries:
        for name in ('High Density Polyethylene', 'High-density polyethylene', 'HDPE'):
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
        float_occurrence = _find_occurrence(root, 'MAIN_FLOAT')
        if not float_occurrence:
            raise RuntimeError('MAIN_FLOAT component was not found.')
        float_body = float_occurrence.component.bRepBodies.itemByName('MAIN_FLOAT_HDPE_BODY')
        if not float_body:
            raise RuntimeError('MAIN_FLOAT_HDPE_BODY was not found.')

        box_z = float_body.boundingBox.minPoint.z + 1.0
        box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX')
        if not box_occurrence:
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, box_z)
            box_occurrence = root.occurrences.addNewComponent(transform)
            box_occurrence.component.name = 'ELECTRONICS_BOX'
        component = box_occurrence.component

        _remove_known_result(component)
        if component.bRepBodies.count or component.sketches.count:
            raise RuntimeError('ELECTRONICS_BOX contains unknown geometry. Nothing was overwritten.')

        parameters = design.userParameters
        _add_parameter(parameters, 'electronics_box_width', '500 mm', 'mm', 'Enclosure outside width')
        _add_parameter(parameters, 'electronics_box_depth', '340 mm', 'mm', 'Enclosure outside depth')
        _add_parameter(parameters, 'electronics_box_height', '350 mm', 'mm', 'Enclosure outside height')
        _add_parameter(parameters, 'electronics_box_wall', '5 mm', 'mm', 'HDPE wall thickness')
        _add_parameter(parameters, 'electronics_box_base', '6 mm', 'mm', 'Leak-containment floor')
        _add_parameter(parameters, 'electronics_lower_zone', '240 mm', 'mm', 'Battery and hot electronics zone')
        _add_parameter(parameters, 'electronics_upper_zone', '100 mm', 'mm', 'Control electronics zone')
        _add_parameter(parameters, 'electronics_fan_size', '80 mm', 'mm', 'PWM intake/exhaust fans')

        width = parameters.itemByName('electronics_box_width').value
        depth = parameters.itemByName('electronics_box_depth').value
        wall = parameters.itemByName('electronics_box_wall').value

        base_sketch = component.sketches.add(component.xYConstructionPlane)
        base_sketch.name = 'SKETCH_01_BOX_BASE'
        _rectangle(base_sketch, width, depth)
        base_profile = base_sketch.profiles.item(0)

        extrudes = component.features.extrudeFeatures
        base_input = extrudes.createInput(
            base_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        base_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('electronics_box_base')
        )
        base_input.setOneSideExtent(
            base_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        base_feature = extrudes.add(base_input)
        base_feature.name = 'EXTRUDE_01_BOX_BASE'
        body = base_feature.bodies.item(0)
        body.name = 'ELECTRONICS_BOX_HDPE_BODY'

        wall_sketch = component.sketches.add(component.xYConstructionPlane)
        wall_sketch.name = 'SKETCH_02_BOX_WALLS'
        _rectangle(wall_sketch, width, depth)
        _rectangle(wall_sketch, width - 2.0 * wall, depth - 2.0 * wall)
        wall_profile = _profiles_by_area(wall_sketch)[0]

        wall_input = extrudes.createInput(
            wall_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        wall_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('electronics_box_height')
        )
        wall_input.setOneSideExtent(
            wall_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        wall_feature = extrudes.add(wall_input)
        wall_feature.name = 'EXTRUDE_02_BOX_WALLS'

        body = component.bRepBodies.itemByName('ELECTRONICS_BOX_HDPE_BODY')
        material_assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-EB-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', 'HDPE')
        component.attributes.add('PROJECT_FALCON_01', 'Architecture', 'Two removable layers')
        component.attributes.add('PROJECT_FALCON_01', 'Cooling', 'Dual 80 mm PWM cross-flow')

        app.activeViewport.fit()
        note = '' if material_assigned else (
            '\nHDPE metadata was added; assign the physical material manually if '
            'it is unavailable in the local library.'
        )
        ui.messageBox(
            'ELECTRONICS_BOX completed as a separate component.\n\n'
            'Outside: 500 x 340 x 350 mm\nWall: 5 mm\nBase: 6 mm\n'
            'Lower zone: 240 mm\nUpper zone: 100 mm\n'
            'Cooling architecture: dual 80 mm PWM cross-flow.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'ELECTRONICS_BOX generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
