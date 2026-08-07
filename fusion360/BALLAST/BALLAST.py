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


def _offset_plane(component, base_plane, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(base_plane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _profiles_by_area(sketch):
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    return sorted(profiles, key=lambda profile: profile.areaProperties().area)


def _assign_steel(app, bodies):
    material = None
    for library in app.materialLibraries:
        for name in ('Stainless Steel 316', 'Stainless Steel', 'Steel'):
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
        if _find_occurrence(root, 'BALLAST'):
            raise RuntimeError('BALLAST already exists; nothing was changed.')
        if not _find_occurrence(root, 'MAIN_FLOAT'):
            raise RuntimeError('MAIN_FLOAT was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'ballast_diameter', '180 mm', 'mm', 'Central ballast diameter')
        _add_parameter(parameters, 'ballast_height', '125 mm', 'mm', 'Central ballast height')
        _add_parameter(parameters, 'ballast_center_z', '-190 mm', 'mm', 'Ballast center below main float')
        _add_parameter(parameters, 'ballast_lug_reach', '125 mm', 'mm', 'Cable lug outside radius')
        _add_parameter(parameters, 'ballast_lug_width', '44 mm', 'mm', 'Cable lug width')
        _add_parameter(parameters, 'ballast_lug_thickness', '12 mm', 'mm', 'Cable lug thickness')
        _add_parameter(parameters, 'ballast_cable_hole', '14 mm', 'mm', 'M12 shackle clearance')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = 'BALLAST'
        extrudes = component.features.extrudeFeatures

        bottom_plane = _offset_plane(
            component, component.xYConstructionPlane, '-62.5 mm',
            'PLANE_01_BALLAST_BOTTOM'
        )
        body_sketch = component.sketches.add(bottom_plane)
        body_sketch.name = 'SKETCH_01_BALLAST_BODY'
        body_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 9.0
        )
        body_input = extrudes.createInput(
            body_sketch.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        body_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ballast_height')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        body_feature = extrudes.add(body_input)
        body_feature.name = 'EXTRUDE_01_SOLID_BALLAST_CORE'
        body_feature.bodies.item(0).name = 'BALLAST_316SS_CORE'

        lug_plane = _offset_plane(
            component, component.xYConstructionPlane, '35 mm',
            'PLANE_02_CABLE_LUG_BOTTOM'
        )
        lug_sketch = component.sketches.add(lug_plane)
        lug_sketch.name = 'SKETCH_02_FOUR_CABLE_LUGS'
        lines = lug_sketch.sketchCurves.sketchLines
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(7.5, -2.2, 0),
            adsk.core.Point3D.create(12.5, 2.2, 0)
        )
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-12.5, -2.2, 0),
            adsk.core.Point3D.create(-7.5, 2.2, 0)
        )
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-2.2, 7.5, 0),
            adsk.core.Point3D.create(2.2, 12.5, 0)
        )
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-2.2, -12.5, 0),
            adsk.core.Point3D.create(2.2, -7.5, 0)
        )
        lug_profiles = adsk.core.ObjectCollection.create()
        for profile in _profiles_by_area(lug_sketch):
            lug_profiles.add(profile)
        lug_input = extrudes.createInput(
            lug_profiles, adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        lug_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ballast_lug_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        lug_feature = extrudes.add(lug_input)
        lug_feature.name = 'EXTRUDE_02_FOUR_CABLE_LUGS'

        hole_sketch = component.sketches.add(lug_plane)
        hole_sketch.name = 'SKETCH_03_FOUR_SHACKLE_HOLES'
        circles = hole_sketch.sketchCurves.sketchCircles
        for x, y in ((10.8, 0), (-10.8, 0), (0, 10.8), (0, -10.8)):
            circles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), 0.7)
        hole_profiles = adsk.core.ObjectCollection.create()
        for profile in _profiles_by_area(hole_sketch):
            hole_profiles.add(profile)
        cut_input = extrudes.createInput(
            hole_profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        cut_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('ballast_lug_thickness')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        cut_feature = extrudes.add(cut_input)
        cut_feature.name = 'CUT_01_FOUR_M12_SHACKLE_CLEARANCES'

        top_sketch = component.sketches.add(component.xYConstructionPlane)
        top_sketch.name = 'SKETCH_04_CENTRAL_SUSPENSION_EYE_BASE'
        top_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0), 2.5
        )
        top_input = extrudes.createInput(
            top_sketch.profiles.item(0),
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        top_input.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(_value('85 mm')),
            adsk.fusion.ExtentDirections.PositiveExtentDirection
        )
        top_feature = extrudes.add(top_input)
        top_feature.name = 'EXTRUDE_03_CENTRAL_SUSPENSION_POST'

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, -19.0)
        occurrence.transform2 = transform

        assigned = _assign_steel(app, component.bRepBodies)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-BAL-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', '316 stainless steel')
        component.attributes.add('PROJECT_FALCON_01', 'NominalMass', 'Approximately 25 kg before lug allowance')
        component.attributes.add('PROJECT_FALCON_01', 'CableInterface', 'Four M12 shackle holes at 90 degrees')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing components untouched')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign 316 stainless steel manually if unavailable locally.'
        ui.messageBox(
            'BALLAST completed.\n\n'
            'Core: 180 mm diameter x 125 mm high\n'
            'Nominal mass: approximately 25 kg\n'
            'Location: centered 190 mm below the main buoy base\n'
            'Cable interfaces: four M12 shackle holes\n'
            'No existing component was moved or edited.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'BALLAST generation failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
