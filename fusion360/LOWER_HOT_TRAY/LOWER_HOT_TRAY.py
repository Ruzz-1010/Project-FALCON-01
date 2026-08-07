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
        raise RuntimeError('LOWER_HOT_TRAY already exists; non-destructive mode made no changes.')


def _rectangle(sketch, x_min, y_min, x_max, y_max):
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x_min, y_min, 0),
        adsk.core.Point3D.create(x_max, y_max, 0)
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
        box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX')
        if not box_occurrence:
            raise RuntimeError('ELECTRONICS_BOX component was not found.')

        box_base_z = box_occurrence.transform2.translation.z
        tray_z = box_base_z + 0.6  # On top of the 6 mm enclosure floor.
        tray_occurrence = _find_occurrence(root, 'LOWER_HOT_TRAY')
        if not tray_occurrence:
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, tray_z)
            tray_occurrence = root.occurrences.addNewComponent(transform)
            tray_occurrence.component.name = 'LOWER_HOT_TRAY'
        component = tray_occurrence.component

        _remove_known_result(component)
        if component.bRepBodies.count or component.sketches.count:
            raise RuntimeError('LOWER_HOT_TRAY contains unknown geometry. Nothing was overwritten.')

        parameters = design.userParameters
        _add_parameter(parameters, 'lower_tray_width', '485 mm', 'mm', 'Removable tray width')
        _add_parameter(parameters, 'lower_tray_depth', '325 mm', 'mm', 'Removable tray depth')
        _add_parameter(parameters, 'lower_tray_base', '5 mm', 'mm', 'HDPE tray floor')
        _add_parameter(parameters, 'lower_tray_wall', '5 mm', 'mm', 'Retaining wall thickness')
        _add_parameter(parameters, 'lower_tray_wall_height', '20 mm', 'mm', 'Edge retention height')
        _add_parameter(parameters, 'thermal_divider_x', '100 mm', 'mm', 'Divider location from center')
        _add_parameter(parameters, 'thermal_divider_height', '220 mm', 'mm', 'Battery heat-isolation divider')
        _add_parameter(parameters, 'thermal_divider_thickness', '5 mm', 'mm', 'Divider thickness')
        _add_parameter(parameters, 'lower_fan_size', '80 mm', 'mm', 'Electronics-bay fan size')

        width = parameters.itemByName('lower_tray_width').value
        depth = parameters.itemByName('lower_tray_depth').value
        wall = parameters.itemByName('lower_tray_wall').value
        divider_x = parameters.itemByName('thermal_divider_x').value
        divider_t = parameters.itemByName('thermal_divider_thickness').value

        deck_sketch = component.sketches.add(component.xYConstructionPlane)
        deck_sketch.name = 'SKETCH_01_LOWER_DECK'
        _rectangle(deck_sketch, -width / 2.0, -depth / 2.0, width / 2.0, depth / 2.0)

        # Two strap pass-through pairs in the battery bay.
        for x in (-17.0, -7.0):
            _rectangle(deck_sketch, x - 1.5, -0.4, x + 1.5, 0.4)

        deck_profile = _profiles_by_area(deck_sketch)[-1]
        extrudes = component.features.extrudeFeatures
        deck_input = extrudes.createInput(
            deck_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        deck_extent = adsk.fusion.DistanceExtentDefinition.create(_value('lower_tray_base'))
        deck_input.setOneSideExtent(
            deck_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        deck_feature = extrudes.add(deck_input)
        deck_feature.name = 'EXTRUDE_01_LOWER_DECK'
        body = deck_feature.bodies.item(0)
        body.name = 'LOWER_HOT_TRAY_HDPE_BODY'

        wall_sketch = component.sketches.add(component.xYConstructionPlane)
        wall_sketch.name = 'SKETCH_02_RETAINING_WALL'
        _rectangle(wall_sketch, -width / 2.0, -depth / 2.0, width / 2.0, depth / 2.0)
        _rectangle(
            wall_sketch,
            -width / 2.0 + wall,
            -depth / 2.0 + wall,
            width / 2.0 - wall,
            depth / 2.0 - wall,
        )
        wall_profile = _profiles_by_area(wall_sketch)[0]
        wall_input = extrudes.createInput(
            wall_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        wall_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('lower_tray_wall_height')
        )
        wall_input.setOneSideExtent(
            wall_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        wall_feature = extrudes.add(wall_input)
        wall_feature.name = 'EXTRUDE_02_RETAINING_WALL'

        divider_sketch = component.sketches.add(component.xYConstructionPlane)
        divider_sketch.name = 'SKETCH_03_THERMAL_DIVIDER'
        _rectangle(
            divider_sketch,
            divider_x - divider_t / 2.0,
            -depth / 2.0 + wall,
            divider_x + divider_t / 2.0,
            depth / 2.0 - wall,
        )
        divider_input = extrudes.createInput(
            divider_sketch.profiles.item(0),
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        divider_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('thermal_divider_height')
        )
        divider_input.setOneSideExtent(
            divider_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        divider_feature = extrudes.add(divider_input)
        divider_feature.name = 'EXTRUDE_03_THERMAL_DIVIDER'

        body = component.bRepBodies.itemByName('LOWER_HOT_TRAY_HDPE_BODY')
        material_assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-LHT-001')
        component.attributes.add('PROJECT_FALCON_01', 'BatteryBay', 'Left; 340 x 315 mm usable')
        component.attributes.add('PROJECT_FALCON_01', 'HotElectronicsBay', 'Right; isolated cross-flow')
        component.attributes.add('PROJECT_FALCON_01', 'Cooling', '80 mm intake to 80 mm exhaust')

        app.activeViewport.fit()
        note = '' if material_assigned else (
            '\nHDPE metadata was added; assign the physical material manually if needed.'
        )
        ui.messageBox(
            'LOWER_HOT_TRAY completed as a separate removable component.\n\n'
            'Battery bay: left side\nMini PC/MPPT bay: right side\n'
            'Thermal divider: 5 x 220 mm\n'
            'Cooling path: isolated 80 mm intake-to-exhaust cross-flow.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'LOWER_HOT_TRAY generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
