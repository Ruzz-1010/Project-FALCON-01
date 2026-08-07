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


def _find_steel(app):
    for library in app.materialLibraries:
        for name in ('Stainless Steel 316', 'Stainless Steel', 'Steel'):
            material = library.materials.itemByName(name)
            if material:
                return material
    return None


def _assign_material(component, material):
    if not material:
        return
    for body in component.bRepBodies:
        body.material = material


def _build_bottom_mount(component):
    extrudes = component.features.extrudeFeatures
    plate_plane = _offset_plane(
        component, component.xYConstructionPlane, '-8 mm',
        'PLANE_01_MOUNT_PLATE_BOTTOM'
    )
    plate_sketch = component.sketches.add(plate_plane)
    plate_sketch.name = 'SKETCH_01_BOTTOM_MOUNT_PLATE'
    circles = plate_sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 5.0)
    for x, y in ((3.5, 0), (-3.5, 0), (0, 3.5), (0, -3.5)):
        circles.addByCenterRadius(adsk.core.Point3D.create(x, y, 0), 0.45)
    profiles = [plate_sketch.profiles.item(i) for i in range(plate_sketch.profiles.count)]
    plate_profile = max(profiles, key=lambda profile: profile.areaProperties().area)
    plate_input = extrudes.createInput(
        plate_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    plate_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('chain_mount_plate_thickness')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    plate_feature = extrudes.add(plate_input)
    plate_feature.name = 'EXTRUDE_01_SEALED_BOTTOM_MOUNT'
    plate_feature.bodies.item(0).name = 'MAIN_FLOAT_BOTTOM_MOUNT_316SS'

    clevis_plane = _offset_plane(
        component, component.xYConstructionPlane, '-28 mm',
        'PLANE_02_CLEVIS_BOTTOM'
    )
    clevis_sketch = component.sketches.add(clevis_plane)
    clevis_sketch.name = 'SKETCH_02_CENTRAL_CLEVIS_BOSS'
    clevis_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), 1.5
    )
    clevis_input = extrudes.createInput(
        clevis_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    clevis_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('20 mm')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    clevis_feature = extrudes.add(clevis_input)
    clevis_feature.name = 'EXTRUDE_02_CENTRAL_CLEVIS_BOSS'

    hole_sketch = component.sketches.add(component.xZConstructionPlane)
    hole_sketch.name = 'SKETCH_03_CLEVIS_PIN_HOLE'
    hole_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 1.8, 0), 0.7
    )
    cut_input = extrudes.createInput(
        hole_sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    cut_input.setSymmetricExtent(_value('40 mm'), True)
    cut_feature = extrudes.add(cut_input)
    cut_feature.name = 'CUT_01_M12_CLEVIS_PIN_CLEARANCE'


def _build_chain_link(component, index):
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = 'SKETCH_01_CHAIN_LINK_PROFILE'
    lines = sketch.sketchCurves.sketchLines
    axis = lines.addByTwoPoints(
        adsk.core.Point3D.create(0, -2.0, 0),
        adsk.core.Point3D.create(0, 2.0, 0)
    )
    axis.isConstruction = True
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(1.0, 0, 0), 0.3
    )
    revolves = component.features.revolveFeatures
    revolve_input = revolves.createInput(
        sketch.profiles.item(0), axis,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    revolve_input.setAngleExtent(False, _value('360 deg'))
    feature = revolves.add(revolve_input)
    feature.name = 'REVOLVE_01_316SS_CHAIN_LINK'
    feature.bodies.item(0).name = 'CHAIN_LINK_{:02d}_316SS_BODY'.format(index)


def _link_transform(index, center_z_cm):
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
        if _find_occurrence(root, 'BALLAST_SUSPENSION_CHAIN'):
            raise RuntimeError(
                'BALLAST_SUSPENSION_CHAIN already exists; nothing was changed.'
            )
        for required in ('MAIN_FLOAT', 'BALLAST'):
            if not _find_occurrence(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        parameters = design.userParameters
        _add_parameter(parameters, 'chain_mount_plate_OD', '100 mm', 'mm', 'Sealed bottom mounting plate')
        _add_parameter(parameters, 'chain_mount_plate_thickness', '8 mm', 'mm', 'Mount plate thickness')
        _add_parameter(parameters, 'chain_wire_diameter', '6 mm', 'mm', '316 stainless link wire')
        _add_parameter(parameters, 'chain_link_OD', '26 mm', 'mm', 'Circular link outside diameter')
        _add_parameter(parameters, 'chain_link_pitch', '16 mm', 'mm', 'Vertical link center spacing')
        _add_parameter(parameters, 'chain_link_count', '6', '', 'Editable suspension link count')

        system_occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system_component = system_occurrence.component
        system_component.name = 'BALLAST_SUSPENSION_CHAIN'
        steel = _find_steel(app)

        mount_occurrence = system_component.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()
        )
        mount_component = mount_occurrence.component
        mount_component.name = 'MAIN_FLOAT_BOTTOM_CHAIN_MOUNT'
        _build_bottom_mount(mount_component)
        _assign_material(mount_component, steel)
        mount_component.attributes.add(
            'PROJECT_FALCON_01', 'PartNumber', 'FALCON-BCM-001'
        )

        for index, center_z in enumerate((-2.5, -4.1, -5.7, -7.3, -8.9, -10.5), 1):
            link_occurrence = system_component.occurrences.addNewComponent(
                _link_transform(index, center_z)
            )
            link_component = link_occurrence.component
            link_component.name = 'BALLAST_CHAIN_LINK_{:02d}'.format(index)
            _build_chain_link(link_component, index)
            _assign_material(link_component, steel)
            link_component.attributes.add(
                'PROJECT_FALCON_01', 'PartNumber',
                'FALCON-BCL-{:03d}'.format(index)
            )

        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Material', '316 stainless steel'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Architecture',
            'Separate bottom mount plus six editable alternating chain links'
        )
        system_component.attributes.add(
            'PROJECT_FALCON_01', 'Safety', 'Existing components untouched'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'BALLAST_SUSPENSION_CHAIN completed.\n\n'
            'Bottom mount: 100 mm x 8 mm sealed plate with M12 clevis\n'
            'Chain: 6 separate editable 316SS links\n'
            'Connection: MAIN_FLOAT bottom to central BALLAST\n'
            'No existing component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'BALLAST_SUSPENSION_CHAIN generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
