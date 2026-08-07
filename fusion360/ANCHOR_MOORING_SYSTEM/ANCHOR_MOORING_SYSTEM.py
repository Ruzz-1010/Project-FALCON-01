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


def _offset_plane(component, base_plane, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(base_plane, _value(expression))
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _center_square(sketch, half_size_cm):
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-half_size_cm, -half_size_cm, 0),
        adsk.core.Point3D.create(half_size_cm, half_size_cm, 0)
    )


def _build_anchor(component):
    bottom_plane = _offset_plane(
        component, component.xYConstructionPlane, '-500 mm',
        'PLANE_01_ANCHOR_BOTTOM'
    )
    bottom_sketch = component.sketches.add(bottom_plane)
    bottom_sketch.name = 'SKETCH_01_ANCHOR_BOTTOM_650MM'
    _center_square(bottom_sketch, 32.5)
    top_sketch = component.sketches.add(component.xYConstructionPlane)
    top_sketch.name = 'SKETCH_02_ANCHOR_TOP_450MM'
    _center_square(top_sketch, 22.5)

    lofts = component.features.loftFeatures
    loft_input = lofts.createInput(
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    loft_input.loftSections.add(bottom_sketch.profiles.item(0))
    loft_input.loftSections.add(top_sketch.profiles.item(0))
    loft = lofts.add(loft_input)
    loft.name = 'LOFT_01_REINFORCED_CONCRETE_ANCHOR'
    concrete_body = loft.bodies.item(0)
    concrete_body.name = 'ANCHOR_REINFORCED_CONCRETE_BODY'

    eye_sketch = component.sketches.add(component.xYConstructionPlane)
    eye_sketch.name = 'SKETCH_03_EMBEDDED_MOORING_EYE'
    eye_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), 3.0
    )
    extrudes = component.features.extrudeFeatures
    eye_input = extrudes.createInput(
        eye_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    eye_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('100 mm')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    eye_feature = extrudes.add(eye_input)
    eye_feature.name = 'EXTRUDE_01_316SS_MOORING_EYE_POST'
    eye_body = eye_feature.bodies.item(0)
    eye_body.name = 'ANCHOR_316SS_MOORING_EYE'

    hole_sketch = component.sketches.add(component.xZConstructionPlane)
    hole_sketch.name = 'SKETCH_04_MOORING_EYE_HOLE'
    hole_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, -7.0, 0), 1.0
    )
    cut_input = extrudes.createInput(
        hole_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    cut_input.setSymmetricExtent(_value('80 mm'), True)
    cut = extrudes.add(cut_input)
    cut.name = 'CUT_01_M20_MOORING_SHACKLE_CLEARANCE'
    return concrete_body, eye_body


def _build_chain_link(component, index):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_01_HEAVY_CHAIN_LINK_PROFILE'
    axis = sketch.sketchCurves.sketchLines.addByTwoPoints(
        adsk.core.Point3D.create(0, -4.0, 0),
        adsk.core.Point3D.create(0, 4.0, 0)
    )
    axis.isConstruction = True
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(2.0, 0, 0), 0.6
    )
    revolves = component.features.revolveFeatures
    revolve_input = revolves.createInput(
        sketch.profiles.item(0), axis,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    revolve_input.setAngleExtent(False, _value('360 deg'))
    feature = revolves.add(revolve_input)
    feature.name = 'REVOLVE_01_12MM_316SS_CHAIN_LINK'
    feature.bodies.item(0).name = 'ANCHOR_CHAIN_LINK_{:02d}_316SS'.format(index)


def _chain_transform(index, center_z_cm):
    transform = adsk.core.Matrix3D.create()
    axis = (
        adsk.core.Vector3D.create(1, 0, 0)
        if index % 2 else adsk.core.Vector3D.create(0, 1, 0)
    )
    transform.setToRotation(
        math.pi / 2, axis, adsk.core.Point3D.create(0, 0, 0)
    )
    transform.translation = adsk.core.Vector3D.create(0, 0, center_z_cm)
    return transform


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
        if _find_occurrence(root, 'ANCHOR_MOORING_SYSTEM'):
            raise RuntimeError('ANCHOR_MOORING_SYSTEM already exists; nothing was changed.')
        if not _find_occurrence(root, 'BALLAST'):
            raise RuntimeError('BALLAST was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'anchor_bottom_size', '650 mm', 'mm', 'Concrete anchor bottom square')
        _add_parameter(parameters, 'anchor_top_size', '450 mm', 'mm', 'Concrete anchor top square')
        _add_parameter(parameters, 'anchor_height', '500 mm', 'mm', 'Concrete anchor height')
        _add_parameter(parameters, 'anchor_top_z', '-850 mm', 'mm', 'Anchor top elevation below buoy')
        _add_parameter(parameters, 'anchor_nominal_mass', '367 kg', 'kg', 'Approximate concrete mass')
        _add_parameter(parameters, 'anchor_chain_wire', '12 mm', 'mm', '316 stainless chain wire diameter')
        _add_parameter(parameters, 'anchor_chain_link_OD', '52 mm', 'mm', 'Heavy chain link outside diameter')
        _add_parameter(parameters, 'anchor_chain_pitch', '45 mm', 'mm', 'Vertical link pitch')
        _add_parameter(parameters, 'anchor_chain_count', '13', '', 'Editable chain-link count')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'ANCHOR_MOORING_SYSTEM'
        concrete = _find_material(app, ('Concrete', 'Concrete, Cast-in-Place gray'))
        steel = _find_material(app, ('Stainless Steel 316', 'Stainless Steel', 'Steel'))

        anchor_transform = adsk.core.Matrix3D.create()
        anchor_transform.translation = adsk.core.Vector3D.create(0, 0, -85.0)
        anchor_occurrence = system_component.occurrences.addNewComponent(anchor_transform)
        anchor_component = anchor_occurrence.component
        anchor_component.name = 'CONCRETE_MOORING_ANCHOR'
        concrete_body, eye_body = _build_anchor(anchor_component)
        if concrete:
            concrete_body.material = concrete
        if steel:
            eye_body.material = steel
        anchor_component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-ANC-001')
        anchor_component.attributes.add('PROJECT_FALCON_01', 'NominalMass', 'Approximately 367 kg')

        centers = tuple(-28.5 - 4.5 * i for i in range(13))
        for index, center_z in enumerate(centers, 1):
            occurrence = system_component.occurrences.addNewComponent(
                _chain_transform(index, center_z)
            )
            component = occurrence.component
            component.name = 'ANCHOR_CHAIN_LINK_{:02d}'.format(index)
            _build_chain_link(component, index)
            if steel:
                for body in component.bRepBodies:
                    body.material = steel
            component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber',
                'FALCON-ACL-{:03d}'.format(index)
            )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Separate concrete anchor, embedded eye, and 13 editable alternating links'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'LoadPath', 'BALLAST to anchor mooring eye'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing components untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'ANCHOR_MOORING_SYSTEM completed.\n\n'
            'Anchor: 650/450 mm tapered square x 500 mm high\n'
            'Nominal concrete mass: approximately 367 kg\n'
            'Mooring eye: 316SS with M20 shackle clearance\n'
            'Chain: 13 separate editable 12 mm 316SS links\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'ANCHOR_MOORING_SYSTEM generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
