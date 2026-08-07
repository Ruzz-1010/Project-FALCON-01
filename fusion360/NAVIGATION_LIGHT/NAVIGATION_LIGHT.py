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


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _cylinder(component, z_mm, radius_cm, height, operation, name):
    plane = component.xYConstructionPlane if z_mm == 0 else _offset_plane(
        component, '{} mm'.format(z_mm), name + '_PLANE'
    )
    sketch = component.sketches.add(plane)
    sketch.name = name.replace('EXTRUDE', 'SKETCH')
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), radius_cm
    )
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = name
    return feature.bodies.item(0)


def _find_material(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


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
        if _find_occurrence(root, 'NAVIGATION_LIGHT'):
            raise RuntimeError('NAVIGATION_LIGHT already exists; nothing was changed.')
        if not _find_occurrence(root, 'UPPER_EQUIPMENT_FRAME'):
            raise RuntimeError('UPPER_EQUIPMENT_FRAME was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'nav_light_lens_OD', '80 mm', 'mm', '360-degree LED lens diameter')
        _add_parameter(parameters, 'nav_light_lens_height', '70 mm', 'mm', 'Visible lantern height')
        _add_parameter(parameters, 'nav_light_mast_height', '105 mm', 'mm', 'Deck-to-lantern support')
        _add_parameter(parameters, 'nav_light_total_height', '195 mm', 'mm', 'Complete beacon height')
        _add_parameter(parameters, 'nav_light_deck_z', '882 mm', 'mm', 'Upper equipment deck elevation')

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, -6.0, 88.2)
        occurrence = root.occurrences.addNewComponent(transform)
        component = occurrence.component
        component.name = 'NAVIGATION_LIGHT'

        base = _cylinder(
            component, 0, 2.5, '15 mm',
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            'EXTRUDE_01_NAV_LIGHT_BASE'
        )
        base.name = 'NAVIGATION_LIGHT_316SS_BASE'
        mast = _cylinder(
            component, 12, 1.0, '93 mm',
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            'EXTRUDE_02_NAV_LIGHT_MAST'
        )
        mast.name = 'NAVIGATION_LIGHT_316SS_MAST'
        lower_cap = _cylinder(
            component, 100, 4.5, '12 mm',
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            'EXTRUDE_03_LOWER_LANTERN_CAP'
        )
        lower_cap.name = 'NAVIGATION_LIGHT_LOWER_CAP'
        lens = _cylinder(
            component, 110, 4.0, '70 mm',
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            'EXTRUDE_04_360_DEGREE_LED_LENS'
        )
        lens.name = 'NAVIGATION_LIGHT_CLEAR_LED_LENS'
        upper_cap = _cylinder(
            component, 178, 4.5, '12 mm',
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            'EXTRUDE_05_UPPER_LANTERN_CAP'
        )
        upper_cap.name = 'NAVIGATION_LIGHT_UPPER_CAP'

        steel = _find_material(app, ('Stainless Steel 316', 'Stainless Steel', 'Steel'))
        glass = _find_material(app, ('Glass', 'Tempered Glass', 'Plastic - Clear'))
        if steel:
            for body in (base, mast, lower_cap, upper_cap):
                body.material = steel
        if glass:
            lens.material = glass

        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-NL-001')
        component.attributes.add('PROJECT_FALCON_01', 'Type', '360-degree all-round white LED marine navigation light')
        component.attributes.add('PROJECT_FALCON_01', 'Electrical', '12 VDC; dusk sensor / controller ready')
        component.attributes.add('PROJECT_FALCON_01', 'Service', 'Separate editable and replaceable lantern assembly')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing components untouched')

        app.activeViewport.fit()
        ui.messageBox(
            'NAVIGATION_LIGHT completed.\n\n'
            'Type: 360-degree all-round white LED marine beacon\n'
            'Lens: 80 mm OD x 70 mm high\n'
            'Power interface: 12 VDC\n'
            'Separate editable component on upper deck.\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'NAVIGATION_LIGHT generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
