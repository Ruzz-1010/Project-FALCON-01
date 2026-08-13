import adsk.core
import adsk.fusion
import math
import traceback


TILT_DEGREES = 20.0


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _find_occurrence(root, name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == name.upper():
            return occurrence
    return None


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


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


def _find_appearance(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                appearance = library.appearances.itemByName(name)
            except Exception:
                appearance = None
            if appearance:
                return appearance
    return None


def _panel_transform(nx, ny):
    angle = math.radians(TILT_DEGREES)
    sine, cosine = math.sin(angle), math.cos(angle)
    tangent = adsk.core.Vector3D.create(-ny, nx, 0)
    vertical_slope = adsk.core.Vector3D.create(-nx * sine, -ny * sine, cosine)
    outward_normal = adsk.core.Vector3D.create(nx * cosine, ny * cosine, sine)
    origin = adsk.core.Point3D.create(nx * 27.0, ny * 27.0, 117.0)
    transform = adsk.core.Matrix3D.create()
    transform.setWithCoordinateSystem(
        origin, tangent, vertical_slope, outward_normal
    )
    return transform


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _build_panel(component, index, aluminum, glass, appearance):
    extrudes = component.features.extrudeFeatures
    frame_sketch = component.sketches.add(component.xYConstructionPlane)
    frame_sketch.name = 'SKETCH_01_30W_PANEL_FRAME'
    frame_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-22.5, -15.0, 0),
        adsk.core.Point3D.create(22.5, 15.0, 0)
    )
    frame_input = extrudes.createInput(
        frame_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    frame_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('dual_solar_panel_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    frame_feature = extrudes.add(frame_input)
    frame_feature.name = 'EXTRUDE_01_30W_ALUMINUM_FRAME'
    frame_body = frame_feature.bodies.item(0)
    frame_body.name = 'DUAL_SOLAR_{:02d}_ALUMINUM_FRAME'.format(index)
    if aluminum:
        frame_body.material = aluminum

    laminate_plane = _offset_plane(component, '20 mm', 'PLANE_02_SOLAR_FACE')
    laminate_sketch = component.sketches.add(laminate_plane)
    laminate_sketch.name = 'SKETCH_02_30W_MONOCRYSTALLINE_FACE'
    laminate_sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-21.3, -13.8, 0),
        adsk.core.Point3D.create(21.3, 13.8, 0)
    )
    laminate_input = extrudes.createInput(
        laminate_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    laminate_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('dual_solar_laminate_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    laminate_feature = extrudes.add(laminate_input)
    laminate_feature.name = 'EXTRUDE_02_30W_SOLAR_LAMINATE'
    laminate_body = laminate_feature.bodies.item(0)
    laminate_body.name = 'DUAL_SOLAR_{:02d}_MONOCRYSTALLINE_FACE'.format(index)
    if glass:
        laminate_body.material = glass
    if appearance:
        laminate_body.appearance = appearance
    component.attributes.add(
        'PROJECT_FALCON_01', 'Specification',
        '30 W monocrystalline; 450 x 300 x 20 mm; 20 deg outward tilt'
    )


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


def _add_strut(component, start, end, index):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_DUAL_SOLAR_STRUT'.format(index)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    pipe_input = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    pipe_input.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(1.0)
    pipe_input.isHollow = False
    feature = component.features.pipeFeatures.add(pipe_input)
    feature.name = 'PIPE_{:02d}_DUAL_SOLAR_STRUT'.format(index)
    feature.bodies.item(0).name = 'DUAL_SOLAR_STRUT_{:02d}_6061'.format(index)


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
        if _find_occurrence(root, 'DUAL_30W_SOLAR_ARRAY'):
            raise RuntimeError('DUAL_30W_SOLAR_ARRAY already exists; nothing was changed.')
        if not _find_occurrence(root, 'COMPACT_ELEVATED_UPPER_TOWER'):
            raise RuntimeError(
                'COMPACT_ELEVATED_UPPER_TOWER was not found. Run that correction first.'
            )

        parameters = design.userParameters
        _add_parameter(parameters, 'dual_solar_panel_power', '30 W', 'W', 'Nominal power per panel')
        _add_parameter(parameters, 'dual_solar_total_power', '60 W', 'W', 'Two-panel nominal total')
        _add_parameter(parameters, 'dual_solar_panel_width', '450 mm', 'mm', 'Panel tangent width')
        _add_parameter(parameters, 'dual_solar_panel_height', '300 mm', 'mm', 'Panel sloped height')
        _add_parameter(parameters, 'dual_solar_panel_thickness', '20 mm', 'mm', 'Panel frame thickness')
        _add_parameter(parameters, 'dual_solar_laminate_thickness', '3 mm', 'mm', 'Solar laminate')
        _add_parameter(parameters, 'dual_solar_tilt_from_vertical', '20 deg', 'deg', 'Outward sunlight tilt')
        _add_parameter(parameters, 'dual_solar_center_z', '1170 mm', 'mm', 'Elevated panel center')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = system_occurrence.component
        system.name = 'DUAL_30W_SOLAR_ARRAY'
        aluminum = _find_material(app, ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'))
        glass = _find_material(app, ('Glass', 'Tempered Glass'))
        appearance = _find_appearance(app, ('Glass - Dark Tint', 'Blue', 'Paint - Enamel Glossy (Blue)'))

        for index, nx, side in ((1, 1, 'EAST_+X'), (2, -1, 'WEST_-X')):
            occurrence = system.occurrences.addNewComponent(_panel_transform(nx, 0))
            panel = occurrence.component
            panel.name = 'SOLAR_30W_{:02d}_{}'.format(index, side)
            _build_panel(panel, index, aluminum, glass, appearance)
            panel.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-SP30-{:03d}'.format(index))
            panel.attributes.add('PROJECT_FALCON_01', 'Placement', side)

        bracket_occurrence = system.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        brackets = bracket_occurrence.component
        brackets.name = 'DUAL_30W_SOLAR_BRACKETS'
        # Two triangulated struts per side from the compact 1020 mm top rail.
        struts = (
            (_point(21, 12, 102), _point(27, 12, 111)),
            (_point(21, -12, 102), _point(27, -12, 111)),
            (_point(-21, 12, 102), _point(-27, 12, 111)),
            (_point(-21, -12, 102), _point(-27, -12, 111))
        )
        for index, (start, end) in enumerate(struts, 1):
            _add_strut(brackets, start, end, index)
        if aluminum:
            for body in brackets.bRepBodies:
                body.material = aluminum

        system.attributes.add('PROJECT_FALCON_01', 'Array', 'Two opposed 30 W panels; 60 W total')
        system.attributes.add('PROJECT_FALCON_01', 'WindArea', 'Reduced from four panels to two compact opposite panels')
        system.attributes.add('PROJECT_FALCON_01', 'Safety', 'Legacy solar geometry hidden, not deleted')

        # Hide every legacy solar occurrence. The replacement remains fully
        # reversible because no old component is deleted.
        legacy_names = (
            'SOLAR_PANEL_ARRAY', 'SOLAR_PANEL_TILT_BRACKETS',
            'SOLAR_PANEL_ELEVATION_SUPPORTS',
            'SOLAR_PANEL_01_NORTH_+Y', 'SOLAR_PANEL_02_EAST_+X',
            'SOLAR_PANEL_03_SOUTH_-Y', 'SOLAR_PANEL_04_WEST_-X'
        )
        for name in legacy_names:
            legacy = _find_occurrence(root, name)
            if legacy:
                legacy.isLightBulbOn = False

        app.activeViewport.fit()
        ui.messageBox(
            'DUAL_30W_SOLAR_REPLACEMENT completed.\n\n'
            'Panels: 2 x 30 W = 60 W total\n'
            'Placement: opposite East and West sides\n'
            'Size: 450 x 300 x 20 mm each\n'
            'Tilt: 20 degrees outward from vertical\n'
            'Center height: 1170 mm\n'
            'Old four-panel system: hidden, not deleted\n'
            'No buoy, electronics, ballast, sensor, or vent was moved.\n\n'
            'Click Capture Position, then save.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'DUAL_30W_SOLAR_REPLACEMENT failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
