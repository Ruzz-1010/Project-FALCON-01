import adsk.core
import adsk.fusion
import math
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
    plane_input.setByOffset(component.xZConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _panel_transform(angle, x, y, z):
    transform = adsk.core.Matrix3D.create()
    transform.setToRotation(
        angle,
        adsk.core.Vector3D.create(0, 0, 1),
        adsk.core.Point3D.create(0, 0, 0)
    )
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    return transform


def _find_material(app, names):
    for library in app.materialLibraries:
        for name in names:
            material = library.materials.itemByName(name)
            if material:
                return material
    return None


def _find_appearance(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                appearance = library.appearances.itemByName(name)
            except Exception:
                # Some local Fusion libraries throw for names they do not contain.
                appearance = None
            if appearance:
                return appearance
    return None


def _build_panel(component, index, aluminum, glass, dark_appearance):
    extrudes = component.features.extrudeFeatures

    frame_sketch = component.sketches.add(component.xZConstructionPlane)
    frame_sketch.name = 'SKETCH_01_PANEL_FRAME'
    frame_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-17.5, -22.5, 0),
        adsk.core.Point3D.create(17.5, 22.5, 0)
    )
    frame_input = extrudes.createInput(
        frame_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    frame_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('solar_panel_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    frame_feature = extrudes.add(frame_input)
    frame_feature.name = 'EXTRUDE_01_ALUMINUM_PANEL_FRAME'
    frame_body = frame_feature.bodies.item(0)
    frame_body.name = 'SOLAR_PANEL_{:02d}_ALUMINUM_FRAME'.format(index)
    if aluminum:
        frame_body.material = aluminum

    laminate_plane = _offset_plane(
        component, '25 mm', 'PLANE_01_SOLAR_LAMINATE_FACE'
    )
    laminate_sketch = component.sketches.add(laminate_plane)
    laminate_sketch.name = 'SKETCH_02_MONOCRYSTALLINE_LAMINATE'
    laminate_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-16.0, -21.0, 0),
        adsk.core.Point3D.create(16.0, 21.0, 0)
    )
    laminate_input = extrudes.createInput(
        laminate_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    laminate_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('solar_laminate_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    laminate_feature = extrudes.add(laminate_input)
    laminate_feature.name = 'EXTRUDE_02_SOLAR_LAMINATE'
    laminate_body = laminate_feature.bodies.item(0)
    laminate_body.name = 'SOLAR_PANEL_{:02d}_MONOCRYSTALLINE_FACE'.format(index)
    if glass:
        laminate_body.material = glass
    if dark_appearance:
        laminate_body.appearance = dark_appearance

    component.attributes.add(
        'PROJECT_FALCON_01', 'PartNumber', 'FALCON-SP-{:03d}'.format(index)
    )
    component.attributes.add(
        'PROJECT_FALCON_01', 'Specification',
        '25 W monocrystalline; 450 x 350 x 25 mm nominal'
    )


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
        if _find_occurrence(root, 'SOLAR_PANEL_ARRAY'):
            raise RuntimeError('SOLAR_PANEL_ARRAY already exists; nothing was changed.')
        if not _find_occurrence(root, 'UPPER_EQUIPMENT_FRAME'):
            raise RuntimeError('UPPER_EQUIPMENT_FRAME was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'solar_panel_height', '450 mm', 'mm', 'Panel overall height')
        _add_parameter(parameters, 'solar_panel_width', '350 mm', 'mm', 'Panel overall width')
        _add_parameter(parameters, 'solar_panel_thickness', '25 mm', 'mm', 'Panel frame thickness')
        _add_parameter(parameters, 'solar_laminate_thickness', '3 mm', 'mm', 'Glass and cell laminate')
        _add_parameter(parameters, 'solar_array_mount_radius', '280 mm', 'mm', 'Panel rear-face radius')
        _add_parameter(parameters, 'solar_array_center_z', '641 mm', 'mm', 'Panel vertical center')
        _add_parameter(parameters, 'solar_array_rated_power', '100 W', 'W', 'Four panels at 25 W each')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'SOLAR_PANEL_ARRAY'

        aluminum = _find_material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        glass = _find_material(app, ('Glass', 'Tempered Glass'))
        dark_appearance = _find_appearance(
            app, ('Glass - Dark Tint', 'Paint - Enamel Glossy (Blue)', 'Blue')
        )

        placements = (
            (1, 0, 0, 28.0, 64.1, 'NORTH_+Y'),
            (2, -math.pi / 2, 28.0, 0, 64.1, 'EAST_+X'),
            (3, math.pi, 0, -28.0, 64.1, 'SOUTH_-Y'),
            (4, math.pi / 2, -28.0, 0, 64.1, 'WEST_-X')
        )
        for index, angle, x, y, z, side in placements:
            occurrence = system_component.occurrences.addNewComponent(
                _panel_transform(angle, x, y, z)
            )
            component = occurrence.component
            component.name = 'SOLAR_PANEL_{:02d}_{}'.format(index, side)
            _build_panel(component, index, aluminum, glass, dark_appearance)
            component.attributes.add('PROJECT_FALCON_01', 'Placement', side)

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Array',
            'Four separate editable vertical panels; 100 W nominal total'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing frame and assembly untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'SOLAR_PANEL_ARRAY completed.\n\n'
            '4 separate editable vertical panels\n'
            'Each panel: 450 x 350 x 25 mm; 25 W nominal\n'
            'Array rating: 100 W nominal\n'
            'Placement: four sides around UPPER_EQUIPMENT_FRAME\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'SOLAR_PANEL_ARRAY generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
