import adsk.core
import adsk.fusion
import traceback


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _find(root, name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == name.upper():
            return occurrence
    return None


def _parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


def _material(app):
    for library in app.materialLibraries:
        for name in ('Stainless Steel 316', 'Stainless Steel', 'Steel'):
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _child(parent, name, z):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _disk(component, outer_radius, inner_radius, thickness, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), outer_radius)
    if inner_radius:
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), inner_radius)
    profiles = [sketch.profiles.item(i) for i in range(sketch.profiles.count)]
    profile = min(profiles, key=lambda item: item.areaProperties().area) if inner_radius else profiles[0]
    input_ = component.features.extrudeFeatures.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value(thickness)),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _cable(component, start, end, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(0.6)
    input_.isHollow = False
    feature = component.features.pipeFeatures.add(input_)
    feature.bodies.item(0).name = 'SECONDARY_BALLAST_RETENTION_CABLE'
    if material:
        feature.bodies.item(0).material = material


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
            raise RuntimeError('Fusion has uncaptured positions. Click Capture Position, save, then run again.')
        if _find(root, 'ADJUSTABLE_LOW_BALLAST_V2'):
            raise RuntimeError('ADJUSTABLE_LOW_BALLAST_V2 already exists; nothing was changed.')
        if not _find(root, 'MAIN_FLOAT_TRADITIONAL_V2'):
            raise RuntimeError('MAIN_FLOAT_TRADITIONAL_V2 was not found.')

        p = design.userParameters
        _parameter(p, 'ballast_v2_rail_length', '500 mm', 'mm', 'Adjustable central ballast rail')
        _parameter(p, 'ballast_v2_rail_OD', '40 mm', 'mm', '316L rail diameter')
        _parameter(p, 'ballast_v2_plate_OD', '220 mm', 'mm', 'Removable plate diameter')
        _parameter(p, 'ballast_v2_plate_thickness', '25 mm', 'mm', 'Nominal plate thickness')
        _parameter(p, 'ballast_v2_plate_quantity', '4', '', 'Initial removable plate quantity')
        _parameter(p, 'ballast_v2_top_z', '-300 mm', 'mm', 'Rail top below rounded keel')
        _parameter(p, 'ballast_v2_bottom_z', '-800 mm', 'mm', 'Rail bottom and chain interface')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'ADJUSTABLE_LOW_BALLAST_V2'
        steel = _material(app)

        rail = _child(system, 'BALLAST_V2_CENTRAL_RAIL', -80.0)
        _disk(rail, 2.0, 0, '500 mm', 'BALLAST_RAIL_316L', steel)

        for index, z in enumerate((-70.0, -66.5, -63.0, -59.5), 1):
            plate = _child(system, 'BALLAST_V2_REMOVABLE_PLATE_{:02d}'.format(index), z)
            _disk(plate, 11.0, 2.2, '25 mm', 'REMOVABLE_WEIGHT_PLATE_316L', steel)
            plate.attributes.add('PROJECT_FALCON_01', 'Sequence', str(index))
            plate.attributes.add('PROJECT_FALCON_01', 'Warning', 'Final mass determined by controlled flotation test')

        for name, z in (('BALLAST_V2_UPPER_LOCK_COLLAR', -57.0),
                        ('BALLAST_V2_LOWER_LOCK_COLLAR', -73.0)):
            collar = _child(system, name, z)
            _disk(collar, 4.0, 2.1, '18 mm', name + '_316L', steel)

        clevis = _child(system, 'BALLAST_V2_ANCHOR_CHAIN_CLEVIS', -82.0)
        _disk(clevis, 3.5, 0.8, '20 mm', 'LOWER_MOORING_CLEVIS_316L', steel)

        retention = _child(system, 'BALLAST_V2_SECONDARY_RETENTION', 0)
        _cable(retention, adsk.core.Point3D.create(4.0, 0, -30.0),
               adsk.core.Point3D.create(4.0, 0, -78.0), steel)

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-BAL-002')
        system.attributes.add('PROJECT_FALCON_01', 'Architecture', 'Adjustable rail with four removable plates')
        system.attributes.add('PROJECT_FALCON_01', 'Retention', 'Two lock collars plus independent secondary cable')
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'Loaded freeboard, static heel, roll/pitch recovery, righting moment required')

        for name in ('BALLAST', 'BALLAST_SUSPENSION_CHAIN'):
            old = _find(root, name)
            if old:
                old.isLightBulbOn = False
        occurrence.isLightBulbOn = True

        app.activeViewport.fit()
        ui.messageBox(
            'ADJUSTABLE_LOW_BALLAST_V2 completed.\n\n'
            '500 mm central rail below rounded keel\n'
            '4 separate removable ballast plates\n'
            'Upper/lower lock collars and secondary retention cable\n'
            'Lower anchor-chain clevis included\n'
            'Old fixed ballast hidden, not deleted.\n\n'
            'Final plate quantity and depth require controlled stability tests.\n'
            'Click Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('ADJUSTABLE_LOW_BALLAST_V2 failed:\n\n{}'.format(traceback.format_exc()), 'PROJECT FALCON-01')
