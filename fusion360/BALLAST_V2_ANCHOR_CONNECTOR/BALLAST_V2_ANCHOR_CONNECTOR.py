import adsk.core
import adsk.fusion
import traceback


def _find(root, prefix):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper().startswith(prefix.upper()):
            return occurrence
    return None


def _material(app, names):
    for library in app.materialLibraries:
        for name in names:
            try:
                result = library.materials.itemByName(name)
            except Exception:
                result = None
            if result:
                return result
    return None


def _child(parent, name, z):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _cylinder(component, radius, height_mm, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), radius)
    input_ = component.features.extrudeFeatures.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    input_.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString(height_mm)), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    body = component.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _line(component, start, end, diameter_cm, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.is3D = True
    curve = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(curve, False)
    input_ = component.features.pipeFeatures.createInput(path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(diameter_cm)
    input_.isHollow = False
    body = component.features.pipeFeatures.add(input_).bodies.item(0)
    body.name = name
    if material:
        body.material = material


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            raise RuntimeError('Open PROJECT FALCON-01 before running this script.')
        root = design.rootComponent
        if design.snapshots.hasPendingSnapshot:
            raise RuntimeError('Click Capture Position, save, then run again.')
        if _find(root, 'BALLAST_V2_ANCHOR_CONNECTOR'):
            raise RuntimeError('BALLAST_V2_ANCHOR_CONNECTOR already exists; nothing was changed.')
        if not _find(root, 'ADJUSTABLE_LOW_BALLAST_V2') or not _find(root, 'ANCHOR_MOORING_SYSTEM'):
            raise RuntimeError('Adjustable ballast V2 and existing anchor system are required.')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component; system.name = 'BALLAST_V2_ANCHOR_CONNECTOR'
        steel = _material(app, ('Stainless Steel 316', 'Stainless Steel', 'Steel'))
        rubber = _material(app, ('Rubber', 'Neoprene', 'Silicone Rubber'))
        upper = _child(system, 'UPPER_M20_SHACKLE', -82.0); _cylinder(upper, 2.0, '12 mm', 'UPPER_SHACKLE_316L', steel)
        swivel = _child(system, 'MOORING_LOAD_SWIVEL', -83.2); _cylinder(swivel, 1.6, '14 mm', 'LOAD_SWIVEL_316L', steel)
        snubber = _child(system, 'COMPACT_ELASTIC_SNUBBER', -84.4); _cylinder(snubber, 1.8, '14 mm', 'ELASTIC_MOORING_SNUBBER', rubber)
        lower = _child(system, 'LOWER_M20_SHACKLE', -85.6); _cylinder(lower, 2.0, '12 mm', 'LOWER_SHACKLE_316L', steel)
        safety = _child(system, 'MOORING_SAFETY_LANYARD', 0)
        _line(safety, adsk.core.Point3D.create(3, 0, -82), adsk.core.Point3D.create(3, 0, -86.5), .6, 'SECONDARY_316L_SAFETY_LANYARD', steel)
        system.attributes.add('PROJECT_FALCON_01', 'LoadPath', 'Ballast V2 clevis to existing anchor eye')
        system.attributes.add('PROJECT_FALCON_01', 'Redundancy', 'Primary swivel/snubber plus secondary lanyard')
        system.attributes.add('PROJECT_FALCON_01', 'Validation', 'Site-specific mooring engineering required')
        app.activeViewport.fit()
        ui.messageBox('BALLAST_V2_ANCHOR_CONNECTOR completed.\n\nUpper/lower M20 shackles\n316L load swivel\nCompact elastic snubber\nSecondary safety lanyard\n\nCapture Position, save, then send a screenshot.', 'PROJECT FALCON-01')
    except Exception:
        if ui:
            ui.messageBox('BALLAST_V2_ANCHOR_CONNECTOR failed:\n\n{}'.format(traceback.format_exc()), 'PROJECT FALCON-01')
