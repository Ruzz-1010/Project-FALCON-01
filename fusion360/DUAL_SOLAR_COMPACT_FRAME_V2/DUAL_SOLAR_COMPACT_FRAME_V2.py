import adsk.core
import adsk.fusion
import traceback


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


def _plane(component, elevation, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(component.xYConstructionPlane, _value('{} mm'.format(elevation)))
    result = component.constructionPlanes.add(plane_input)
    result.name = name
    return result


def _profiles(sketch):
    values = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(values, key=lambda profile: profile.areaProperties().area)


def _ring(component, elevation, index):
    sketch = component.sketches.add(
        _plane(component, elevation, 'PLANE_{:02d}_RING'.format(index))
    )
    sketch.name = 'SKETCH_{:02d}_360MM_RING'.format(index)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 18.0)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 16.5)
    extrude_input = component.features.extrudeFeatures.createInput(
        _profiles(sketch)[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('dual_frame_ring_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(extrude_input)
    feature.name = 'EXTRUDE_{:02d}_360MM_RING'.format(index)
    feature.bodies.item(0).name = 'DUAL_FRAME_RING_{:02d}_6061'.format(index)


def _rectangles_extrude(component, elevation, rectangles, height, name):
    sketch = component.sketches.add(_plane(component, elevation, 'PLANE_' + name))
    sketch.name = 'SKETCH_' + name
    lines = sketch.sketchCurves.sketchLines
    for x1, y1, x2, y2 in rectangles:
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(x1, y1, 0),
            adsk.core.Point3D.create(x2, y2, 0)
        )
    collection = adsk.core.ObjectCollection.create()
    for profile in _profiles(sketch):
        collection.add(profile)
    extrude_input = component.features.extrudeFeatures.createInput(
        collection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(height)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(extrude_input)
    feature.name = 'EXTRUDE_' + name
    return feature


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
        if _find_occurrence(root, 'DUAL_SOLAR_COMPACT_FRAME_V2'):
            raise RuntimeError('DUAL_SOLAR_COMPACT_FRAME_V2 already exists; nothing was changed.')
        if not _find_occurrence(root, 'DUAL_30W_SOLAR_ARRAY'):
            raise RuntimeError('DUAL_30W_SOLAR_ARRAY was not found. Run the dual-panel replacement first.')

        parameters = design.userParameters
        _add_parameter(parameters, 'dual_frame_OD', '360 mm', 'mm', 'Low-drag tower outside diameter')
        _add_parameter(parameters, 'dual_frame_ID', '330 mm', 'mm', 'Tower clear diameter')
        _add_parameter(parameters, 'dual_frame_post_size', '20 mm', 'mm', 'Square post outside size')
        _add_parameter(parameters, 'dual_frame_ring_thickness', '8 mm', 'mm', 'Slim ring thickness')
        _add_parameter(parameters, 'dual_frame_base_z', '550 mm', 'mm', 'Tower base elevation')
        _add_parameter(parameters, 'dual_frame_top_z', '1170 mm', 'mm', 'Tower top elevation')
        _add_parameter(parameters, 'dual_frame_height', '620 mm', 'mm', 'Tower post height')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        frame = occurrence.component
        frame.name = 'DUAL_SOLAR_COMPACT_FRAME_V2'
        _ring(frame, 550, 1)
        _ring(frame, 860, 2)
        _ring(frame, 1170, 3)

        posts = (
            (11.5, 11.5, 13.5, 13.5), (-13.5, 11.5, -11.5, 13.5),
            (-13.5, -13.5, -11.5, -11.5), (11.5, -13.5, 13.5, -11.5)
        )
        post_feature = _rectangles_extrude(
            frame, 550, posts, '620 mm', '04_FOUR_20MM_POSTS'
        )
        for index, body in enumerate(post_feature.bodies, 1):
            body.name = 'DUAL_FRAME_POST_{:02d}_6061'.format(index)

        # Short East/West panel ties at lower and upper panel attachment zones.
        ties = ((16.5, -2, 28, 2), (-28, -2, -16.5, 2))
        _rectangles_extrude(frame, 1040, ties, '10 mm', '05_LOWER_PANEL_TIES')
        _rectangles_extrude(frame, 1160, ties, '10 mm', '06_UPPER_PANEL_TIES')

        # Compact top cross for antennas, navigation light, and wind sensor.
        cross = ((-16.5, -1.0, 16.5, 1.0), (-1.0, -16.5, 1.0, 16.5))
        _rectangles_extrude(frame, 1170, cross, '8 mm', '07_TOP_SENSOR_CROSS')

        aluminum = _find_aluminum(app)
        if aluminum:
            for body in frame.bRepBodies:
                body.material = aluminum
        frame.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-DSF-002')
        frame.attributes.add('PROJECT_FALCON_01', 'Frame', '360 mm OD x 620 mm; 20 mm posts')
        frame.attributes.add('PROJECT_FALCON_01', 'SolarInterface', 'Two opposed 30 W panels')
        frame.attributes.add('PROJECT_FALCON_01', 'WindArea', 'Reduced two-side frame')

        for name in (
            'UPPER_EQUIPMENT_FRAME', 'UPPER_FRAME_SUPPORT_STANCHIONS',
            'COMPACT_ELEVATED_UPPER_TOWER', 'SOLAR_PANEL_ELEVATION_SUPPORTS'
        ):
            legacy = _find_occurrence(root, name)
            if legacy:
                legacy.isLightBulbOn = False
        occurrence.isLightBulbOn = True

        app.activeViewport.fit()
        ui.messageBox(
            'DUAL_SOLAR_COMPACT_FRAME_V2 completed.\n\n'
            'Visible replacement frame: 360 mm OD\n'
            'Height: Z550 to Z1170 mm\n'
            'Four 20 mm posts plus three slim rings\n'
            'East/West brackets for the two 30 W panels\n'
            'Compact top cross for sensors and navigation light\n'
            'Old 560 mm and 460 mm frames: hidden, not deleted.\n\n'
            'Click Capture Position, then save.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'DUAL_SOLAR_COMPACT_FRAME_V2 failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
