import adsk.core
import adsk.fusion
import math
import traceback


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _assign_aluminum(app, bodies):
    material = None
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            material = library.materials.itemByName(name)
            if material:
                break
        if material:
            break
    if not material:
        return False
    for body in bodies:
        body.material = material
    return True


def _rectangle(lines, x1, y1, x2, y2):
    lines.addTwoPointRectangle(
        adsk.core.Point3D.create(x1, y1, 0),
        adsk.core.Point3D.create(x2, y2, 0)
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
        # Adding any timeline feature can restore uncaptured assembly positions.
        # Stop before creating anything so the user can Capture Position first.
        if design.snapshots.hasPendingSnapshot:
            raise RuntimeError(
                'Fusion has uncaptured component positions. Nothing was changed.\n\n'
                'Click Capture Position in the toolbar, save the document, then run again.'
            )
        if _find_occurrence(root, 'MAIN_SUPPORT_FRAME'):
            raise RuntimeError(
                'MAIN_SUPPORT_FRAME already exists; non-destructive mode made no changes.'
            )
        if not _find_occurrence(root, 'MAIN_FLOAT'):
            raise RuntimeError('MAIN_FLOAT component was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'frame_float_clearance', '4 mm', 'mm', 'Diametral installation clearance')
        _add_parameter(parameters, 'frame_collar_ID', '654 mm', 'mm', 'Clear inside diameter around float')
        _add_parameter(parameters, 'frame_collar_OD', '684 mm', 'mm', 'Collar outside diameter')
        _add_parameter(parameters, 'frame_collar_height', '70 mm', 'mm', 'Vertical collar height')
        _add_parameter(parameters, 'frame_elevation', '45 mm', 'mm', 'Bottom elevation above float base')
        _add_parameter(parameters, 'frame_lug_width', '90 mm', 'mm', 'Arm mounting lug width')
        _add_parameter(parameters, 'frame_lug_reach', '430 mm', 'mm', 'Lug outside radius')
        _add_parameter(parameters, 'frame_lug_thickness', '12 mm', 'mm', 'Mounting lug thickness')
        _add_parameter(parameters, 'frame_lug_hole', '11 mm', 'mm', 'M10 clearance diameter')
        _add_parameter(parameters, 'frame_lug_hole_pitch', '42 mm', 'mm', 'Two-hole radial pitch')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = 'MAIN_SUPPORT_FRAME'
        extrudes = component.features.extrudeFeatures

        collar = component.sketches.add(component.xYConstructionPlane)
        collar.name = 'SKETCH_01_COLLAR_RING'
        circles = collar.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 34.2)
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 32.7)
        collar_profile = _profiles_by_area(collar)[0]
        collar_input = extrudes.createInput(
            collar_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        collar_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('frame_collar_height')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        collar_feature = extrudes.add(collar_input)
        collar_feature.name = 'EXTRUDE_01_STRUCTURAL_COLLAR'
        collar_feature.bodies.item(0).name = 'FRAME_6061_COLLAR_BODY'

        plane_input = component.constructionPlanes.createInput()
        plane_input.setByOffset(component.xYConstructionPlane, _value('29 mm'))
        lug_plane = component.constructionPlanes.add(plane_input)
        lug_plane.name = 'PLANE_01_LUG_CENTER'

        lug_sketch = component.sketches.add(lug_plane)
        lug_sketch.name = 'SKETCH_02_FOUR_ARM_LUGS'
        lines = lug_sketch.sketchCurves.sketchLines
        # Dimensions below are centimeters internally: R327 to R430, width 90.
        _rectangle(lines, 32.7, -4.5, 43.0, 4.5)
        _rectangle(lines, -43.0, -4.5, -32.7, 4.5)
        _rectangle(lines, -4.5, 32.7, 4.5, 43.0)
        _rectangle(lines, -4.5, -43.0, 4.5, -32.7)

        lug_profiles = _profiles_by_area(lug_sketch)
        lug_collection = adsk.core.ObjectCollection.create()
        for profile in lug_profiles:
            lug_collection.add(profile)
        lug_input = extrudes.createInput(
            lug_collection, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        lug_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('frame_lug_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        lug_feature = extrudes.add(lug_input)
        lug_feature.name = 'EXTRUDE_02_FOUR_REINFORCED_LUGS'

        hole_sketch = component.sketches.add(lug_plane)
        hole_sketch.name = 'SKETCH_03_M10_ARM_INTERFACES'
        holes = hole_sketch.sketchCurves.sketchCircles
        hole_radius = 0.55
        for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            for radius in (35.8, 40.0):
                holes.addByCenterRadius(
                    adsk.core.Point3D.create(radius * math.cos(angle), radius * math.sin(angle), 0),
                    hole_radius
                )
        hole_profiles = _profiles_by_area(hole_sketch)
        hole_collection = adsk.core.ObjectCollection.create()
        for profile in hole_profiles:
            hole_collection.add(profile)
        cut_input = extrudes.createInput(
            hole_collection, adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        cut_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('frame_lug_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        cut_feature = extrudes.add(cut_input)
        cut_feature.name = 'CUT_01_EIGHT_M10_CLEARANCE_HOLES'

        transform = occurrence.transform2
        transform.translation = adsk.core.Vector3D.create(0, 0, 4.5)
        occurrence.transform2 = transform

        assigned = _assign_aluminum(app, component.bRepBodies)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-MSF-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', '6061-T6 marine aluminum')
        component.attributes.add('PROJECT_FALCON_01', 'Interface', 'Four arm lugs at 90 degrees; 2 x M10 each')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'No existing component edited or moved')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign 6061-T6 manually if unavailable locally.'
        ui.messageBox(
            'MAIN_SUPPORT_FRAME completed.\n\n'
            'Collar: ID 654 mm / OD 684 mm / height 70 mm\n'
            'Position: 45 mm above float base\n'
            'Arm interfaces: 4 lugs at 90 degrees\n'
            'Fasteners: 2 x M10 per lug\n'
            'No existing component was moved or edited.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'MAIN_SUPPORT_FRAME generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
