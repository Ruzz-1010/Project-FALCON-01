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


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _add_ring(component, elevation, index, operation):
    plane = _offset_plane(
        component, '{} mm'.format(elevation),
        'PLANE_{:02d}_RING'.format(index)
    )
    sketch = component.sketches.add(plane)
    sketch.name = 'SKETCH_{:02d}_SUPPORT_RING'.format(index)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 28.0)
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 25.0)
    profile = _profiles_by_area(sketch)[0]
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(profile, operation)
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('upper_frame_ring_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = 'EXTRUDE_{:02d}_SUPPORT_RING'.format(index)
    return feature


def _find_aluminum(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            material = library.materials.itemByName(name)
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
        if _find_occurrence(root, 'UPPER_EQUIPMENT_FRAME'):
            raise RuntimeError('UPPER_EQUIPMENT_FRAME already exists; nothing was changed.')
        for required in ('MAIN_FLOAT', 'TOP_CAP'):
            if not _find_occurrence(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        parameters = design.userParameters
        _add_parameter(parameters, 'upper_frame_ring_OD', '560 mm', 'mm', 'Equipment cage outside diameter')
        _add_parameter(parameters, 'upper_frame_ring_ID', '500 mm', 'mm', 'Equipment cage inside diameter')
        _add_parameter(parameters, 'upper_frame_ring_thickness', '12 mm', 'mm', 'Horizontal ring thickness')
        _add_parameter(parameters, 'upper_frame_post_size', '30 mm', 'mm', 'Square vertical post size')
        _add_parameter(parameters, 'upper_frame_base_z', '400 mm', 'mm', 'Base ring elevation')
        _add_parameter(parameters, 'upper_frame_mid_z', '635 mm', 'mm', 'Solar-panel middle rail elevation')
        _add_parameter(parameters, 'upper_frame_top_z', '870 mm', 'mm', 'Top antenna-deck elevation')
        _add_parameter(parameters, 'upper_frame_height', '482 mm', 'mm', 'Overall removable frame height')
        _add_parameter(parameters, 'upper_frame_antenna_plate_OD', '120 mm', 'mm', 'Central antenna mounting plate')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = 'UPPER_EQUIPMENT_FRAME'
        extrudes = component.features.extrudeFeatures

        base_feature = _add_ring(
            component, 400, 1,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        base_feature.bodies.item(0).name = 'UPPER_FRAME_6061_BODY'
        _add_ring(
            component, 635, 2,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        _add_ring(
            component, 870, 3,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )

        post_plane = _offset_plane(component, '400 mm', 'PLANE_04_POST_BASE')
        post_sketch = component.sketches.add(post_plane)
        post_sketch.name = 'SKETCH_04_FOUR_VERTICAL_POSTS'
        lines = post_sketch.sketchCurves.sketchLines
        for x in (-18.4, 18.4):
            for y in (-18.4, 18.4):
                lines.addTwoPointRectangle(
                    adsk.core.Point3D.create(x - 1.5, y - 1.5, 0),
                    adsk.core.Point3D.create(x + 1.5, y + 1.5, 0)
                )
        post_profiles = adsk.core.ObjectCollection.create()
        for profile in _profiles_by_area(post_sketch):
            post_profiles.add(profile)
        post_input = extrudes.createInput(
            post_profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        post_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('upper_frame_height')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        post_feature = extrudes.add(post_input)
        post_feature.name = 'EXTRUDE_04_FOUR_SOLAR_SUPPORT_POSTS'

        top_plane = _offset_plane(component, '870 mm', 'PLANE_05_ANTENNA_DECK')
        cross_sketch = component.sketches.add(top_plane)
        cross_sketch.name = 'SKETCH_05_TOP_CROSS_AND_ANTENNA_PLATE'
        cross_lines = cross_sketch.sketchCurves.sketchLines
        cross_lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-25.0, -1.5, 0),
            adsk.core.Point3D.create(25.0, 1.5, 0)
        )
        cross_lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-1.5, -25.0, 0),
            adsk.core.Point3D.create(1.5, 25.0, 0)
        )
        cross_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 6.0
        )
        cross_profiles = adsk.core.ObjectCollection.create()
        for profile in _profiles_by_area(cross_sketch):
            cross_profiles.add(profile)
        cross_input = extrudes.createInput(
            cross_profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        cross_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('upper_frame_ring_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        cross_feature = extrudes.add(cross_input)
        cross_feature.name = 'EXTRUDE_05_REINFORCED_ANTENNA_DECK'

        antenna_hole_sketch = component.sketches.add(top_plane)
        antenna_hole_sketch.name = 'SKETCH_06_ANTENNA_MOUNTING_HOLES'
        holes = antenna_hole_sketch.sketchCurves.sketchCircles
        for x, y in ((4.0, 0), (-4.0, 0), (0, 4.0), (0, -4.0)):
            holes.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), 0.45)
        hole_profiles = adsk.core.ObjectCollection.create()
        for profile in _profiles_by_area(antenna_hole_sketch):
            hole_profiles.add(profile)
        hole_input = extrudes.createInput(
            hole_profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        hole_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('upper_frame_ring_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        hole_feature = extrudes.add(hole_input)
        hole_feature.name = 'CUT_01_FOUR_M8_ANTENNA_MOUNTS'

        aluminum = _find_aluminum(app)
        if aluminum:
            for body in component.bRepBodies:
                body.material = aluminum
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-UEF-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', '6061-T6 marine aluminum')
        component.attributes.add('PROJECT_FALCON_01', 'SolarInterface', 'Four faces with base/mid/top rails')
        component.attributes.add('PROJECT_FALCON_01', 'AntennaInterface', '120 mm center deck; 4 x M8')
        component.attributes.add('PROJECT_FALCON_01', 'Service', 'Removable before opening TOP_CAP')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing components untouched')

        app.activeViewport.fit()
        ui.messageBox(
            'UPPER_EQUIPMENT_FRAME completed.\n\n'
            'Cage: 560 mm OD x 482 mm high\n'
            'Structure: three rings plus four 30 mm square posts\n'
            'Solar interfaces: four vertical faces\n'
            'Antenna deck: 120 mm with four M8 holes\n'
            'Frame is separate and removable.\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'UPPER_EQUIPMENT_FRAME generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
