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
        if _find(root, (SYSTEM_NAME,)):
            raise RuntimeError('{} already exists; nothing was changed.'.format(SYSTEM_NAME))
        float_occurrence = _find(root, ('MAIN_FLOAT_TRADITIONAL_V2', 'MAIN_FLOAT'))
        if not float_occurrence:
            raise RuntimeError('MAIN_FLOAT_TRADITIONAL_V2 or MAIN_FLOAT was not found.')

        parameters = design.userParameters
        _parameter(parameters, 'pressure_sensor_radial_offset', '220 mm', 'mm',
                   'Editable sensor offset from buoy centerline')
        _parameter(parameters, 'pressure_sensor_mount_z', '105 mm', 'mm',
                   'Proposed local height on submerged lower shoulder')
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

        occurrence = root.occurrences.addNewComponent(float_occurrence.transform2.copy())
        component = occurrence.component
        component.name = SYSTEM_NAME

        plastic = _material(app, ('ABS Plastic', 'Plastic - ABS', 'Nylon 6'))
        stainless = _material(app, ('Stainless Steel', 'Steel, Stainless', '316 Stainless Steel'))
        rubber = _material(app, ('Rubber', 'Neoprene Rubber', 'Silicone Rubber'))

        # Local coordinates intentionally follow the selected float occurrence.
        # The guard is offset from the centerline and leaves the central ballast/
        # mooring path clear. All dimensions remain editable user parameters.
        x = 22.0
        y = 0.0
        _box(component, 18.0, -4.2, 26.0, 4.2, '105 mm', '6 mm',
             'PRESSURE_SENSOR_MOUNTING_PLATE_316L', stainless)
        _disk(component, x, y, '111 mm', 'pressure_guard_diameter', '6 mm',
              'PRESSURE_GUARD_TOP_RING', plastic)
        _disk(component, x, y, '177 mm', 'pressure_guard_diameter', '6 mm',
              'PRESSURE_GUARD_BOTTOM_RING', plastic)
        for index in range(6):
            angle = math.radians(index * 60.0)
            rod_x = x + 2.7 * math.cos(angle)
            rod_y = y + 2.7 * math.sin(angle)
            _disk(component, rod_x, rod_y, '117 mm', 'pressure_guard_rod_diameter',
                  '60 mm', 'PRESSURE_GUARD_OPEN_ROD_{:02d}'.format(index + 1), plastic)

        _disk(component, x, y, '122 mm', 'pressure_sensor_body_diameter',
              'pressure_sensor_body_height', 'BAR02_COMPATIBLE_SENSOR_ENVELOPE', plastic)
        _disk(component, x, y, '164 mm', '10 mm', '12 mm',
              'DOWNWARD_OPEN_PRESSURE_PORT', stainless)
        _disk(component, x, y, '111 mm', '18 mm', '10 mm',
              'IP68_SENSOR_CABLE_GLAND', rubber)

        component.attributes.add('PROJECT_FALCON_01', 'Status', 'PROPOSED - physical integration TBD')
        component.attributes.add('PROJECT_FALCON_01', 'Function', 'Pressure-based estimated wave input')
        component.attributes.add('PROJECT_FALCON_01', 'Placement', 'Submerged lower shoulder, clear of central ballast and anchor chain')
        component.attributes.add('PROJECT_FALCON_01', 'Calibration', 'CALIBRATION REQUIRED before wave-height claims')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'No existing component moved, hidden, edited, or deleted')

        app.activeViewport.fit()
        ui.messageBox(
            'WATER_PRESSURE_SENSOR_ASSEMBLY completed.\n\n'
            'Proposed location: submerged lower shoulder\n'
            'Includes: mounting plate, Bar02-compatible envelope, downward port,\n'
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
