import adsk.core
import adsk.fusion
import math
import traceback


BASE_Z_CM = 58.0


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


def _child(parent, name, x, y, z):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, z)
    occurrence = parent.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence.component


def _box(component, width, depth, height, name, material=None):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-width / 2, -depth / 2, 0),
        adsk.core.Point3D.create(width / 2, depth / 2, 0)
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('{} mm'.format(height * 10))),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _cylinder(component, radius, height, name, material=None):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), radius
    )
    input_ = component.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('{} mm'.format(height * 10))),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = component.features.extrudeFeatures.add(input_)
    body = feature.bodies.item(0)
    body.name = name
    if material:
        body.material = material


def _cable(component, start, end, material=None):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(0.4)
    input_.isHollow = False
    feature = component.features.pipeFeatures.add(input_)
    feature.bodies.item(0).name = 'SECONDARY_LID_RETENTION_CABLE'
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
            raise RuntimeError(
                'Fusion has uncaptured component positions. Nothing was changed.\n\n'
                'Click Capture Position, save, then run again.'
            )
        if _find(root, 'POD_MARINE_PROTECTION_HARDWARE'):
            raise RuntimeError('POD_MARINE_PROTECTION_HARDWARE already exists; nothing was changed.')
        if not _find(root, 'UPPER_ALL_ELECTRONICS_POD'):
            raise RuntimeError('UPPER_ALL_ELECTRONICS_POD was not found.')

        p = design.userParameters
        _parameter(p, 'pod_lid_clamp_quantity', '8', '', '316L over-center clamp quantity')
        _parameter(p, 'pod_isolator_quantity', '4', '', 'Marine vibration-isolator quantity')
        _parameter(p, 'pod_ip68_gland_quantity', '6', '', 'Downward cable-gland quantity')
        _parameter(p, 'pod_lid_clamp_radius', '170 mm', 'mm', 'Lid clamp mounting radius')
        _parameter(p, 'pod_isolator_radius', '125 mm', 'mm', 'Pod base isolator radius')

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, BASE_Z_CM)
        occurrence = root.occurrences.addNewComponent(transform)
        system = occurrence.component
        system.name = 'POD_MARINE_PROTECTION_HARDWARE'
        steel = _material(app, ('Stainless Steel 316', 'Stainless Steel', 'Steel'))
        rubber = _material(app, ('Rubber', 'Neoprene', 'Silicone Rubber'))
        plastic = _material(app, ('Nylon', 'ABS Plastic', 'Plastic'))

        for index in range(8):
            angle = index * math.pi / 4
            clamp = _child(system, 'LID_CLAMP_316L_{:02d}'.format(index + 1),
                           17.0 * math.cos(angle), 17.0 * math.sin(angle), 39.0)
            _box(clamp, 2.2, 1.2, 4.0, 'LID_CLAMP_316L_BODY', steel)

        for index, angle in enumerate((math.pi / 4, 3 * math.pi / 4,
                                       5 * math.pi / 4, 7 * math.pi / 4), 1):
            isolator = _child(system, 'VIBRATION_ISOLATOR_{:02d}'.format(index),
                              12.5 * math.cos(angle), 12.5 * math.sin(angle), -1.5)
            _cylinder(isolator, 1.8, 3.0, 'MARINE_RUBBER_ISOLATOR', rubber)

        for index, x in enumerate((-10, -6, -2, 2, 6, 10), 1):
            gland = _child(system, 'IP68_CABLE_GLAND_{:02d}'.format(index), x, -15.8, 0.5)
            _cylinder(gland, 0.9, 2.5, 'DOWNWARD_IP68_GLAND', plastic)

        disconnect = _child(system, 'EXTERNAL_EMERGENCY_DISCONNECT', 15.5, 0, 24.0)
        _box(disconnect, 4.5, 3.0, 5.5, 'RED_GUARDED_DISCONNECT_ENVELOPE', plastic)
        disconnect.attributes.add('PROJECT_FALCON_01', 'Service', 'External guarded battery isolation')

        surge = _child(system, 'SOLAR_SURGE_PROTECTION_ENCLOSURE', -15.5, 0, 23.0)
        _box(surge, 5.0, 3.0, 7.0, 'IP67_SOLAR_SPD_ENVELOPE', plastic)
        surge.attributes.add('PROJECT_FALCON_01', 'Protection', 'PV fuse, DC SPD, reverse-polarity protection')

        lug = _child(system, 'LIGHTNING_BONDING_LUG', 0, -16.5, 36.0)
        _box(lug, 3.0, 1.0, 3.0, '316L_EXTERNAL_BONDING_LUG', steel)
        lug.attributes.add('PROJECT_FALCON_01', 'Warning', 'Dedicated external lightning path; keep away from electronics ground path')

        cable = _child(system, 'LID_SECONDARY_RETENTION', 0, 0, 0)
        _cable(cable, adsk.core.Point3D.create(14.5, 0, 34.0),
               adsk.core.Point3D.create(17.0, 0, 44.5), steel)

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-PMP-001')
        system.attributes.add('PROJECT_FALCON_01', 'Ingress', 'Eight clamps, dual gasket support, downward IP68 glands')
        system.attributes.add('PROJECT_FALCON_01', 'Shock', 'Four replaceable marine vibration isolators')
        system.attributes.add('PROJECT_FALCON_01', 'Electrical', 'Emergency disconnect, PV surge protection, external lightning bond')
        system.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing pod and equipment positions untouched')

        app.activeViewport.fit()
        ui.messageBox(
            'POD_MARINE_PROTECTION_HARDWARE completed.\n\n'
            '8 x 316L lid clamps\n4 x vibration isolators\n'
            '6 x downward IP68 glands\nExternal emergency disconnect\n'
            'Solar surge enclosure and lightning bonding lug\n'
            'Secondary lid-retention cable\n'
            'Existing components were not moved or deleted.\n\n'
            'Click Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'POD_MARINE_PROTECTION_HARDWARE failed:\n\n{}'.format(traceback.format_exc()),
                'PROJECT FALCON-01'
            )
