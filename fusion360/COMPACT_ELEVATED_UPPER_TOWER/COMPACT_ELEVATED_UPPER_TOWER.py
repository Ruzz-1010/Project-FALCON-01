import adsk.core
import adsk.fusion
import traceback


ELEVATION_CM = 15.0


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


def _raise(occurrence):
    transform = occurrence.transform2.copy()
    translation = transform.translation
    translation.z += ELEVATION_CM
    transform.translation = translation
    occurrence.transform2 = transform


def _offset_plane(component, elevation_mm, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value('{} mm'.format(elevation_mm)))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _add_ring(component, elevation_mm, index):
    plane = _offset_plane(component, elevation_mm, 'PLANE_{:02d}_COMPACT_RING'.format(index))
    sketch = component.sketches.add(plane)
    sketch.name = 'SKETCH_{:02d}_COMPACT_RING'.format(index)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 23.0)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 21.0)
    profile = _profiles_by_area(sketch)[0]
    extrude_input = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('compact_tower_ring_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(extrude_input)
    feature.name = 'EXTRUDE_{:02d}_COMPACT_RING'.format(index)
    feature.bodies.item(0).name = 'COMPACT_RING_{:02d}_6061'.format(index)


def _add_posts(component):
    plane = _offset_plane(component, 550, 'PLANE_04_COMPACT_POST_BASE')
    sketch = component.sketches.add(plane)
    sketch.name = 'SKETCH_04_FOUR_LOW_DRAG_POSTS'
    lines = sketch.sketchCurves.sketchLines
    for x, y in ((14.1, 14.1), (-14.1, 14.1), (-14.1, -14.1), (14.1, -14.1)):
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(x - 1.0, y - 1.0, 0),
            adsk.core.Point3D.create(x + 1.0, y + 1.0, 0)
        )
    collection = adsk.core.ObjectCollection.create()
    for profile in _profiles_by_area(sketch):
        collection.add(profile)
    extrude_input = component.features.extrudeFeatures.createInput(
        collection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('compact_tower_height')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(extrude_input)
    feature.name = 'EXTRUDE_04_FOUR_20MM_LOW_DRAG_POSTS'
    for index, body in enumerate(feature.bodies, 1):
        body.name = 'COMPACT_POST_{:02d}_6061'.format(index)


def _add_solar_brackets(component):
    for elevation, group in ((562, 1), (785, 2), (1008, 3)):
        plane = _offset_plane(
            component, elevation,
            'PLANE_{}_SOLAR_TIE'.format(group + 4)
        )
        sketch = component.sketches.add(plane)
        sketch.name = 'SKETCH_{}_FOUR_SHORT_SOLAR_TIES'.format(group + 4)
        lines = sketch.sketchCurves.sketchLines
        lines.addTwoPointRectangle(adsk.core.Point3D.create(-2.0, 21.0, 0), adsk.core.Point3D.create(2.0, 28.0, 0))
        lines.addTwoPointRectangle(adsk.core.Point3D.create(-2.0, -28.0, 0), adsk.core.Point3D.create(2.0, -21.0, 0))
        lines.addTwoPointRectangle(adsk.core.Point3D.create(21.0, -2.0, 0), adsk.core.Point3D.create(28.0, 2.0, 0))
        lines.addTwoPointRectangle(adsk.core.Point3D.create(-28.0, -2.0, 0), adsk.core.Point3D.create(-21.0, 2.0, 0))
        profiles = adsk.core.ObjectCollection.create()
        for profile in _profiles_by_area(sketch):
            profiles.add(profile)
        extrude_input = component.features.extrudeFeatures.createInput(
            profiles, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extrude_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('8 mm')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        feature = component.features.extrudeFeatures.add(extrude_input)
        feature.name = 'EXTRUDE_{}_SHORT_SOLAR_TIES'.format(group + 4)


def _find_aluminum(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
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
        if _find_occurrence(root, 'COMPACT_ELEVATED_UPPER_TOWER'):
            raise RuntimeError('Compact elevated upper tower already exists; nothing was changed.')

        old_frame = _find_occurrence(root, 'UPPER_EQUIPMENT_FRAME')
        sensor_array = _find_occurrence(root, 'TOP_SENSOR_ARRAY')
        navigation_light = _find_occurrence(root, 'NAVIGATION_LIGHT')
        if not old_frame or not sensor_array or not navigation_light:
            raise RuntimeError(
                'UPPER_EQUIPMENT_FRAME, TOP_SENSOR_ARRAY, and NAVIGATION_LIGHT are required.'
            )
        panel_names = (
            'SOLAR_PANEL_01_NORTH_+Y', 'SOLAR_PANEL_02_EAST_+X',
            'SOLAR_PANEL_03_SOUTH_-Y', 'SOLAR_PANEL_04_WEST_-X'
        )
        panels = []
        for name in panel_names:
            occurrence = _find_occurrence(root, name)
            if not occurrence:
                raise RuntimeError('{} was not found; nothing was changed.'.format(name))
            panels.append(occurrence)

        parameters = design.userParameters
        _add_parameter(parameters, 'compact_tower_OD', '460 mm', 'mm', 'Reduced-drag frame diameter')
        _add_parameter(parameters, 'compact_tower_ID', '420 mm', 'mm', 'Compact frame clear diameter')
        _add_parameter(parameters, 'compact_tower_post_size', '20 mm', 'mm', 'Low-drag square post size')
        _add_parameter(parameters, 'compact_tower_ring_thickness', '8 mm', 'mm', 'Slim ring thickness')
        _add_parameter(parameters, 'compact_tower_base_z', '550 mm', 'mm', 'Raised compact frame base')
        _add_parameter(parameters, 'compact_tower_top_z', '1020 mm', 'mm', 'Compact upper deck elevation')
        _add_parameter(parameters, 'compact_tower_height', '470 mm', 'mm', 'Compact tower post height')

        # If the earlier panel-only upgrade was not run, bring the panels to
        # the same approved elevation. Never add the offset twice.
        for panel in panels:
            elevated = panel.component.attributes.itemByName(
                'PROJECT_FALCON_01', 'ElevationUpgrade'
            )
            if not elevated:
                _raise(panel)
                panel.component.attributes.add(
                    'PROJECT_FALCON_01', 'ElevationUpgrade', '150 mm upward'
                )

        _raise(sensor_array)
        _raise(navigation_light)

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        tower = occurrence.component
        tower.name = 'COMPACT_ELEVATED_UPPER_TOWER'
        _add_ring(tower, 550, 1)
        _add_ring(tower, 785, 2)
        _add_ring(tower, 1020, 3)
        _add_posts(tower)
        _add_solar_brackets(tower)

        aluminum = _find_aluminum(app)
        if aluminum:
            for body in tower.bRepBodies:
                body.material = aluminum
        tower.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-CUT-001')
        tower.attributes.add('PROJECT_FALCON_01', 'Frame', '460 mm OD; 20 mm posts; 8 mm rings')
        tower.attributes.add('PROJECT_FALCON_01', 'Elevation', '550 to 1020 mm')
        tower.attributes.add('PROJECT_FALCON_01', 'Purpose', 'Reduced wind area elevated solar and sensor tower')

        # Reversible replacement: preserve old geometry but remove it from the
        # active visual representation.
        old_frame.isLightBulbOn = False
        old_stanchions = _find_occurrence(root, 'UPPER_FRAME_SUPPORT_STANCHIONS')
        if old_stanchions:
            old_stanchions.isLightBulbOn = False
        temporary_supports = _find_occurrence(root, 'SOLAR_PANEL_ELEVATION_SUPPORTS')
        if temporary_supports:
            temporary_supports.isLightBulbOn = False

        app.activeViewport.fit()
        ui.messageBox(
            'COMPACT_ELEVATED_UPPER_TOWER completed.\n\n'
            'New frame: 460 mm OD x 470 mm high\n'
            'Posts: four 20 mm low-drag members\n'
            'Solar panels: retained at +150 mm\n'
            'Sensor array and navigation light: raised +150 mm\n'
            'Old frame/supports: hidden, not deleted\n'
            'Buoy, electronics, ballast, cap, and vents were not moved.\n\n'
            'Click Capture Position, then save.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'COMPACT_ELEVATED_UPPER_TOWER failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
