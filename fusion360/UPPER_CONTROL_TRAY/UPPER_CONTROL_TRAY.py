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
        raise RuntimeError('UPPER_CONTROL_TRAY already exists; non-destructive mode made no changes.')


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
        box_occurrence = _find_occurrence(root, 'ELECTRONICS_BOX')
        if not box_occurrence:
            raise RuntimeError('ELECTRONICS_BOX component was not found.')

        box_base_z = box_occurrence.transform2.translation.z
        tray_z = box_base_z + 24.6  # 6 mm floor + 240 mm lower zone.
        tray_occurrence = _find_occurrence(root, 'UPPER_CONTROL_TRAY')
        if not tray_occurrence:
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, tray_z)
            tray_occurrence = root.occurrences.addNewComponent(transform)
            tray_occurrence.component.name = 'UPPER_CONTROL_TRAY'
        component = tray_occurrence.component

        _remove_known_result(component)
        if component.bRepBodies.count or component.sketches.count:
            raise RuntimeError('UPPER_CONTROL_TRAY contains unknown geometry. Nothing was overwritten.')

        parameters = design.userParameters
        _add_parameter(parameters, 'upper_tray_width', '485 mm', 'mm', 'Removable upper tray width')
        _add_parameter(parameters, 'upper_tray_depth', '325 mm', 'mm', 'Removable upper tray depth')
        _add_parameter(parameters, 'upper_tray_base', '5 mm', 'mm', 'HDPE tray floor')
        _add_parameter(parameters, 'upper_tray_wall', '5 mm', 'mm', 'Retaining wall thickness')
        _add_parameter(parameters, 'upper_tray_wall_height', '20 mm', 'mm', 'Edge retention height')
        _add_parameter(parameters, 'upper_grid_hole', '4.5 mm', 'mm', 'M4 clearance hole')
        _add_parameter(parameters, 'upper_grid_x', '100 mm', 'mm', 'Universal mounting-grid X pitch')
        _add_parameter(parameters, 'upper_grid_y', '80 mm', 'mm', 'Universal mounting-grid Y pitch')

        width = parameters.itemByName('upper_tray_width').value
        depth = parameters.itemByName('upper_tray_depth').value
        wall = parameters.itemByName('upper_tray_wall').value
        hole_radius = parameters.itemByName('upper_grid_hole').value / 2.0
        pitch_x = parameters.itemByName('upper_grid_x').value
        pitch_y = parameters.itemByName('upper_grid_y').value

        deck_sketch = component.sketches.add(component.xYConstructionPlane)
        deck_sketch.name = 'SKETCH_01_UPPER_DECK'
        _rectangle(deck_sketch, width, depth)
        circles = deck_sketch.sketchCurves.sketchCircles
        for x_index in (-1.5, -0.5, 0.5, 1.5):
            for y_index in (-1, 0, 1):
                circles.addByCenterRadius(
                    adsk.core.Point3D.create(x_index * pitch_x, y_index * pitch_y, 0),
                    hole_radius
                )

        deck_profile = _profiles_by_area(deck_sketch)[-1]
        extrudes = component.features.extrudeFeatures
        deck_input = extrudes.createInput(
            deck_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        deck_extent = adsk.fusion.DistanceExtentDefinition.create(_value('upper_tray_base'))
        deck_input.setOneSideExtent(
            deck_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        deck_feature = extrudes.add(deck_input)
        deck_feature.name = 'EXTRUDE_01_UPPER_DECK'
        body = deck_feature.bodies.item(0)
        body.name = 'UPPER_CONTROL_TRAY_HDPE_BODY'

        wall_sketch = component.sketches.add(component.xYConstructionPlane)
        wall_sketch.name = 'SKETCH_02_UPPER_WALL'
        _rectangle(wall_sketch, width, depth)
        inner_lines = wall_sketch.sketchCurves.sketchLines
        inner_lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-width / 2.0 + wall, -depth / 2.0 + wall, 0),
            adsk.core.Point3D.create(width / 2.0 - wall, depth / 2.0 - wall, 0)
        )
        wall_profile = _profiles_by_area(wall_sketch)[0]
        wall_input = extrudes.createInput(
            wall_profile, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        wall_extent = adsk.fusion.DistanceExtentDefinition.create(
            _value('upper_tray_wall_height')
        )
        wall_input.setOneSideExtent(
            wall_extent, adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        wall_feature = extrudes.add(wall_input)
        wall_feature.name = 'EXTRUDE_02_UPPER_WALL'

        body = component.bRepBodies.itemByName('UPPER_CONTROL_TRAY_HDPE_BODY')
        material_assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-UCT-001')
        component.attributes.add('PROJECT_FALCON_01', 'Zone', 'Low-power controls and communications')
        component.attributes.add('PROJECT_FALCON_01', 'MountingGrid', '4 x 3 M4 grid; 100 x 80 mm pitch')
        component.attributes.add('PROJECT_FALCON_01', 'ThermalPolicy', 'Isolated from lower hot-air exhaust')

        app.activeViewport.fit()
        note = '' if material_assigned else (
            '\nHDPE metadata was added; assign the physical material manually if needed.'
        )
        ui.messageBox(
            'UPPER_CONTROL_TRAY completed as a separate removable component.\n\n'
            'Usable zone: ESP32, communications, IMU, RTC, and sensor interfaces\n'
            'Mounting: 12 x M4 universal grid holes\n'
            'Thermal zone: isolated from lower hot exhaust.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'UPPER_CONTROL_TRAY generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
