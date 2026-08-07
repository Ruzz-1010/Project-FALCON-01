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


def _rectangle(sketch, x_min, y_min, x_max, y_max):
    return sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x_min, y_min, 0),
        adsk.core.Point3D.create(x_max, y_max, 0)
    )


def _largest_profile(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return max(profiles, key=lambda profile: profile.areaProperties().area)


def _wall_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xZConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _add_fan_wall_sketch(component, plane, name, width, height, fan_x,
                         fan_z, opening_radius, pitch, mount_radius):
    sketch = component.sketches.add(plane)
    sketch.name = name
    # XZ sketch Y is the negative model-Z direction.
    _rectangle(sketch, -width / 2.0, -height, width / 2.0, 0)
    circles = sketch.sketchCurves.sketchCircles
    center = adsk.core.Point3D.create(fan_x, -fan_z, 0)
    circles.addByCenterRadius(center, opening_radius)
    half_pitch = pitch / 2.0
    for dx in (-half_pitch, half_pitch):
        for dz in (-half_pitch, half_pitch):
            circles.addByCenterRadius(
                adsk.core.Point3D.create(fan_x + dx, -fan_z + dz, 0),
                mount_radius
            )
    return sketch


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
        existing = _find_occurrence(root, 'ELECTRONICS_BOX_V2')
        if existing:
            raise RuntimeError(
                'ELECTRONICS_BOX_V2 already exists; non-destructive mode made no changes.'
            )

        float_occurrence = _find_occurrence(root, 'MAIN_FLOAT')
        if not float_occurrence:
            raise RuntimeError('MAIN_FLOAT component was not found.')
        float_body = float_occurrence.component.bRepBodies.itemByName('MAIN_FLOAT_HDPE_BODY')
        if not float_body:
            raise RuntimeError('MAIN_FLOAT_HDPE_BODY was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'ebox_v2_width', '500 mm', 'mm', 'Enclosure width')
        _add_parameter(parameters, 'ebox_v2_depth', '340 mm', 'mm', 'Enclosure depth')
        _add_parameter(parameters, 'ebox_v2_height', '350 mm', 'mm', 'Enclosure height')
        _add_parameter(parameters, 'ebox_v2_wall', '5 mm', 'mm', 'HDPE wall thickness')
        _add_parameter(parameters, 'ebox_v2_base', '6 mm', 'mm', 'Leak-containment floor')
        _add_parameter(parameters, 'ebox_v2_fan_x', '170 mm', 'mm', 'Fan center in hot bay')
        _add_parameter(parameters, 'ebox_v2_fan_z', '120 mm', 'mm', 'Fan center elevation')
        _add_parameter(parameters, 'ebox_v2_fan_opening', '76 mm', 'mm', 'Airflow opening')
        _add_parameter(parameters, 'ebox_v2_fan_pitch', '71.5 mm', 'mm', '80 mm fan mounting pitch')
        _add_parameter(parameters, 'ebox_v2_fan_hole', '4.5 mm', 'mm', 'M4 clearance')

        width = parameters.itemByName('ebox_v2_width').value
        depth = parameters.itemByName('ebox_v2_depth').value
        height = parameters.itemByName('ebox_v2_height').value
        wall = parameters.itemByName('ebox_v2_wall').value
        fan_x = parameters.itemByName('ebox_v2_fan_x').value
        fan_z = parameters.itemByName('ebox_v2_fan_z').value
        opening_radius = parameters.itemByName('ebox_v2_fan_opening').value / 2.0
        pitch = parameters.itemByName('ebox_v2_fan_pitch').value
        mount_radius = parameters.itemByName('ebox_v2_fan_hole').value / 2.0

        box_z = float_body.boundingBox.minPoint.z + 1.0
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, box_z)
        occurrence = root.occurrences.addNewComponent(transform)
        component = occurrence.component
        component.name = 'ELECTRONICS_BOX_V2'
        extrudes = component.features.extrudeFeatures

        base_sketch = component.sketches.add(component.xYConstructionPlane)
        base_sketch.name = 'SKETCH_01_V2_BASE'
        _rectangle(base_sketch, -width / 2.0, -depth / 2.0, width / 2.0, depth / 2.0)
        base_input = extrudes.createInput(
            base_sketch.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        base_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ebox_v2_base')),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        base_feature = extrudes.add(base_input)
        base_feature.name = 'EXTRUDE_01_V2_BASE'
        body = base_feature.bodies.item(0)
        body.name = 'ELECTRONICS_BOX_V2_HDPE_BODY'

        side_sketch = component.sketches.add(component.xYConstructionPlane)
        side_sketch.name = 'SKETCH_02_V2_SIDE_WALLS'
        _rectangle(side_sketch, -width / 2.0, -depth / 2.0,
                   -width / 2.0 + wall, depth / 2.0)
        _rectangle(side_sketch, width / 2.0 - wall, -depth / 2.0,
                   width / 2.0, depth / 2.0)
        side_profiles = adsk.core.ObjectCollection.create()
        for index in range(side_sketch.profiles.count):
            side_profiles.add(side_sketch.profiles.item(index))
        side_input = extrudes.createInput(
            side_profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        side_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ebox_v2_height')),
            adsk.fusion.ExtentDirections.NegativeExtentDirection
        )
        side_feature = extrudes.add(side_input)
        side_feature.name = 'EXTRUDE_02_V2_SIDE_WALLS'

        half_wall = 'ebox_v2_wall / 2'
        front_plane = _wall_plane(
            component, '-ebox_v2_depth / 2 + ' + half_wall, 'PLANE_FRONT_FAN_WALL'
        )
        rear_plane = _wall_plane(
            component, 'ebox_v2_depth / 2 - ' + half_wall, 'PLANE_REAR_FAN_WALL'
        )
        front_sketch = _add_fan_wall_sketch(
            component, front_plane, 'SKETCH_03_V2_INTAKE_WALL', width, height,
            fan_x, fan_z, opening_radius, pitch, mount_radius
        )
        rear_sketch = _add_fan_wall_sketch(
            component, rear_plane, 'SKETCH_04_V2_EXHAUST_WALL', width, height,
            fan_x, fan_z, opening_radius, pitch, mount_radius
        )

        for sketch, feature_name in (
            (front_sketch, 'EXTRUDE_03_V2_INTAKE_WALL'),
            (rear_sketch, 'EXTRUDE_04_V2_EXHAUST_WALL'),
        ):
            wall_input = extrudes.createInput(
                _largest_profile(sketch),
                adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            half_extent_a = adsk.fusion.DistanceExtentDefinition.create(
                _value('ebox_v2_wall / 2')
            )
            half_extent_b = adsk.fusion.DistanceExtentDefinition.create(
                _value('ebox_v2_wall / 2')
            )
            wall_input.setTwoSidesExtent(half_extent_a, half_extent_b)
            wall_feature = extrudes.add(wall_input)
            wall_feature.name = feature_name

        body = component.bRepBodies.itemByName('ELECTRONICS_BOX_V2_HDPE_BODY')
        assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-EB-002')
        component.attributes.add('PROJECT_FALCON_01', 'Revision', 'V2 native fan ports')
        component.attributes.add('PROJECT_FALCON_01', 'Cooling', 'Opposed 80 mm cross-flow')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign HDPE manually if unavailable locally.'
        ui.messageBox(
            'ELECTRONICS_BOX_V2 completed without modifying the original box.\n\n'
            'Native intake and exhaust: 76 mm\nFan pattern: 71.5 mm, M4\n'
            'Old ELECTRONICS_BOX remains untouched and may be hidden.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'ELECTRONICS_BOX_V2 generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )

