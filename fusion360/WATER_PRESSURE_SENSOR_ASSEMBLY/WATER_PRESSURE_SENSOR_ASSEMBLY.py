import adsk.core
import adsk.fusion
import math
import traceback


SYSTEM_NAME = 'WATER_PRESSURE_SENSOR_ASSEMBLY_REV6_PROPOSED'


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _normalized(name):
    return name.upper().replace(' ', '_')


def _find(root, prefixes):
    for occurrence in root.allOccurrences:
        name = _normalized(occurrence.component.name)
        if any(name.startswith(prefix) for prefix in prefixes):
            return occurrence
    return None


def _parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


def _material(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _underside_transform(float_occurrence):
    """Compose the float placement with its revolved-profile Z-axis correction."""
    transform = float_occurrence.transform2.copy()
    correction = adsk.core.Matrix3D.create()
    correction.setToRotation(
        math.pi,
        adsk.core.Vector3D.create(1, 0, 0),
        adsk.core.Point3D.create(0, 0, 0)
    )
    transform.transformBy(correction)
    return transform


def _plane(component, z_expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value(z_expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _disk(component, x_cm, y_cm, z_expression, diameter_expression,
          height_expression, name, material):
    sketch = component.sketches.add(_plane(component, z_expression, 'PLANE_' + name))
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(x_cm, y_cm, 0),
        component.parentDesign.unitsManager.evaluateExpression(diameter_expression, 'cm') / 2.0
    )
    profile = sketch.profiles.item(0)
    input_ = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height_expression)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    feature.name = 'EXTRUDE_' + name
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def _box(component, x0, y0, x1, y1, z_expression, height_expression,
         name, material):
    sketch = component.sketches.add(_plane(component, z_expression, 'PLANE_' + name))
    sketch.name = 'SKETCH_' + name
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(x0, y0, 0),
        adsk.core.Point3D.create(x1, y1, 0)
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height_expression)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material
    return body


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Open the PROJECT FALCON V2 assembly before running this script.')
        root = design.rootComponent
        if design.snapshots.hasPendingSnapshot:
            raise RuntimeError(
                'Fusion has uncaptured component positions. Nothing was changed.\n\n'
                'Click Capture Position, save, then run again.'
            )
        float_occurrence = _find(root, ('MAIN_FLOAT_TRADITIONAL_V2', 'MAIN_FLOAT'))
        if not float_occurrence:
            raise RuntimeError('MAIN_FLOAT_TRADITIONAL_V2 or MAIN_FLOAT was not found.')
        existing = _find(root, (SYSTEM_NAME,))
        if existing:
            existing.transform2 = _underside_transform(float_occurrence)
            existing.component.attributes.add(
                'PROJECT_FALCON_01', 'PlacementRepair',
                'Reoriented to permanently submerged underside'
            )
            app.activeViewport.fit()
            ui.messageBox(
                'Existing WATER_PRESSURE_SENSOR_ASSEMBLY corrected.\n\n'
                'The complete sensor and 316L saddle were flipped from the upper/inside location\n'
                'to the permanently submerged underside. No other component was changed.\n\n'
                'Capture Position, save, then send a side-view screenshot.',
                'PROJECT FALCON-01'
            )
            return

        parameters = design.userParameters
        _parameter(parameters, 'pressure_sensor_radial_offset', '125 mm', 'mm',
                   'Underside offset that clears the central ballast and mooring line')
        _parameter(parameters, 'pressure_sensor_mount_z', '198 mm', 'mm',
                   'Proposed mounting level at the underside of the rounded keel')
        _parameter(parameters, 'pressure_sensor_body_diameter', '24 mm', 'mm',
                   'Bar02-compatible packaging envelope diameter')
        _parameter(parameters, 'pressure_sensor_body_height', '42 mm', 'mm',
                   'Bar02-compatible packaging envelope height')
        _parameter(parameters, 'pressure_guard_diameter', '64 mm', 'mm',
                   'Open protective guard outside diameter')
        _parameter(parameters, 'pressure_guard_height', '72 mm', 'mm',
                   'Open protective guard overall height')
        _parameter(parameters, 'pressure_guard_rod_diameter', '6 mm', 'mm',
                   'Six open guard rod diameters')

        occurrence = root.occurrences.addNewComponent(_underside_transform(float_occurrence))
        component = occurrence.component
        component.name = SYSTEM_NAME

        plastic = _material(app, ('ABS Plastic', 'Plastic - ABS', 'Nylon 6'))
        stainless = _material(app, ('Stainless Steel', 'Steel, Stainless', '316 Stainless Steel'))
        rubber = _material(app, ('Rubber', 'Neoprene Rubber', 'Silicone Rubber'))

        # Local coordinates follow the selected float occurrence. The sensor is
        # below the rounded keel and offset from the central ballast/mooring path.
        x = 12.5
        y = 0.0
        _box(component, 8.0, -4.5, 17.0, 4.5, '198 mm', '8 mm',
             'UNDERSIDE_SENSOR_SADDLE_PLATE_316L', stainless)
        _box(component, 8.7, -4.1, 9.7, -3.1, '206 mm', '20 mm',
             'SADDLE_STANDOFF_316L_01', stainless)
        _box(component, 15.3, -4.1, 16.3, -3.1, '206 mm', '20 mm',
             'SADDLE_STANDOFF_316L_02', stainless)
        _box(component, 8.7, 3.1, 9.7, 4.1, '206 mm', '20 mm',
             'SADDLE_STANDOFF_316L_03', stainless)
        _box(component, 15.3, 3.1, 16.3, 4.1, '206 mm', '20 mm',
             'SADDLE_STANDOFF_316L_04', stainless)
        _box(component, 8.5, -4.2, 16.5, 4.2, '222 mm', '4 mm',
             'SENSOR_GUARD_CARRIER_PLATE_316L', stainless)
        for index, (bolt_x, bolt_y) in enumerate(((9.7, -3.0), (15.3, -3.0),
                                                  (9.7, 3.0), (15.3, 3.0)), 1):
            _disk(component, bolt_x, bolt_y, '198 mm', '8 mm', '12 mm',
                  'M8_SADDLE_FASTENER_316L_{:02d}'.format(index), stainless)

        _disk(component, x, y, '226 mm', 'pressure_guard_diameter', '6 mm',
              'PRESSURE_GUARD_TOP_RING', plastic)
        _disk(component, x, y, '292 mm', 'pressure_guard_diameter', '6 mm',
              'PRESSURE_GUARD_BOTTOM_RING', plastic)
        for index in range(6):
            angle = math.radians(index * 60.0)
            rod_x = x + 2.7 * math.cos(angle)
            rod_y = y + 2.7 * math.sin(angle)
            _disk(component, rod_x, rod_y, '232 mm', 'pressure_guard_rod_diameter',
                  '60 mm', 'PRESSURE_GUARD_OPEN_ROD_{:02d}'.format(index + 1), plastic)

        _disk(component, x, y, '237 mm', 'pressure_sensor_body_diameter',
              'pressure_sensor_body_height', 'BAR02_COMPATIBLE_SENSOR_ENVELOPE', plastic)
        _disk(component, x, y, '279 mm', '10 mm', '12 mm',
              'DOWNWARD_OPEN_PRESSURE_PORT', stainless)
        _disk(component, x, y, '226 mm', '18 mm', '10 mm',
              'IP68_SENSOR_CABLE_GLAND', rubber)

        component.attributes.add('PROJECT_FALCON_01', 'Status', 'PROPOSED - physical integration TBD')
        component.attributes.add('PROJECT_FALCON_01', 'Function', 'Pressure-based estimated wave input')
        component.attributes.add('PROJECT_FALCON_01', 'Placement', 'Permanently submerged underside, offset from central ballast and anchor chain')
        component.attributes.add('PROJECT_FALCON_01', 'Calibration', 'CALIBRATION REQUIRED before wave-height claims')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'No existing component moved, hidden, edited, or deleted')

        app.activeViewport.fit()
        ui.messageBox(
            'WATER_PRESSURE_SENSOR_ASSEMBLY completed.\n\n'
            'Proposed location: permanently submerged underside\n'
            'Includes: 316L saddle bracket, Bar02-compatible envelope, downward port,\n'
            'open protective guard, and IP68 gland.\n\n'
            'No existing component was changed. Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'WATER_PRESSURE_SENSOR_ASSEMBLY failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )


def stop(context):
    pass
