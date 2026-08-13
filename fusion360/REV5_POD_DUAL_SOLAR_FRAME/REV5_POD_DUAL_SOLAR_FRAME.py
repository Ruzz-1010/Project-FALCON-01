import adsk.core
import adsk.fusion
import traceback


def _find(root, prefix):
    for occurrence in root.allOccurrences:
        normalized = occurrence.component.name.upper().replace(' ', '_')
        if normalized.startswith(prefix.upper()):
            return occurrence
    return None


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    return existing or parameters.add(name, _value(expression), units, comment)


def _material(app):
    for library in app.materialLibraries:
        for name in ('Aluminum 6061-T6', 'Aluminum 6061', 'Aluminum'):
            try:
                material = library.materials.itemByName(name)
            except Exception:
                material = None
            if material:
                return material
    return None


def _child(parent, name):
    occurrence = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def _point(x, y, z):
    return adsk.core.Point3D.create(x, y, z)


def _member(component, start, end, index, name, material):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'SKETCH_{:02d}_{}'.format(index, name)
    sketch.is3D = True
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    path = component.features.createPath(line, False)
    input_ = component.features.pipeFeatures.createInput(
        path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
    input_.sectionSize = adsk.core.ValueInput.createByReal(2.5)
    input_.isHollow = False
    feature = component.features.pipeFeatures.add(input_)
    feature.name = 'PIPE_{:02d}_{}'.format(index, name)
    body = feature.bodies.item(0)
    body.name = name + '_6061'
    if material:
        body.material = material


def _foot(component, x, y, index, material):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(x, y, 49.4)
    occurrence = component.occurrences.addNewComponent(transform)
    foot = occurrence.component
    foot.name = 'REV5_FRAME_DECK_FOOT_{:02d}'.format(index)
    sketch = foot.sketches.add(foot.xYConstructionPlane)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-2.5, -2.0, 0),
        adsk.core.Point3D.create(2.5, 2.0, 0)
    )
    input_ = foot.features.extrudeFeatures.createInput(
        sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    input_.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(_value('6 mm')),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    body = foot.features.extrudeFeatures.add(input_).bodies.item(0)
    body.name = 'REV5_FRAME_DECK_FOOT_6061'
    if material:
        body.material = material
    foot.attributes.add('PROJECT_FALCON_01', 'Fastener', '2 x M8 316L with isolation washer')


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
        if _find(root, 'REV5_POD_DUAL_SOLAR_FRAME'):
            raise RuntimeError('REV5_POD_DUAL_SOLAR_FRAME already exists; nothing was changed.')
        for required in ('UPPER_ALL_ELECTRONICS_POD', 'DUAL_30W_SOLAR_ARRAY'):
            if not _find(root, required):
                raise RuntimeError('{} was not found.'.format(required))

        p = design.userParameters
        _parameter(p, 'rev5_frame_member_OD', '25 mm', 'mm', '6061-T6 structural member diameter')
        _parameter(p, 'rev5_frame_side_spacing', '380 mm', 'mm', 'East/West frame center spacing')
        _parameter(p, 'rev5_frame_panel_width', '400 mm', 'mm', 'Panel-side rail span')
        _parameter(p, 'rev5_frame_base_z', '500 mm', 'mm', 'Main deck mounting elevation')
        _parameter(p, 'rev5_frame_top_z', '1320 mm', 'mm', 'Upper panel rail elevation')
        _parameter(p, 'rev5_frame_sensor_bridge_z', '1040 mm', 'mm', 'Central sensor bridge elevation')
        _parameter(p, 'rev5_frame_pod_clearance', '20 mm', 'mm', 'Minimum radial pod clearance')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        system = occurrence.component
        system.name = 'REV5_POD_DUAL_SOLAR_FRAME'
        aluminum = _material(app)
        index = 1

        # Four independent deck interfaces surrounding the 320 mm pod.
        feet = ((19.0, -20.0), (19.0, 20.0), (-19.0, -20.0), (-19.0, 20.0))
        for foot_index, (x, y) in enumerate(feet, 1):
            _foot(system, x, y, foot_index, aluminum)

        # Exactly two open portal frames: East and West.
        for x, side in ((19.0, 'EAST'), (-19.0, 'WEST')):
            side_component = _child(system, 'REV5_{}_SOLAR_SIDE_FRAME'.format(side))
            for y in (-20.0, 20.0):
                _member(side_component, _point(x, y, 50.0), _point(x, y, 132.0),
                        index, '{}_VERTICAL'.format(side), aluminum); index += 1
            for z, label in ((102.0, 'LOWER_PANEL_RAIL'),
                             (117.0, 'CENTER_PANEL_RAIL'),
                             (132.0, 'UPPER_PANEL_RAIL')):
                _member(side_component, _point(x, -20.0, z), _point(x, 20.0, z),
                        index, '{}_{}'.format(side, label), aluminum); index += 1
            # Triangulated lower load path into the deck feet.
            _member(side_component, _point(x, -20.0, 50.0), _point(x, 20.0, 72.0),
                    index, '{}_LOWER_DIAGONAL_A'.format(side), aluminum); index += 1
            _member(side_component, _point(x, 20.0, 50.0), _point(x, -20.0, 72.0),
                    index, '{}_LOWER_DIAGONAL_B'.format(side), aluminum); index += 1

        bridge = _child(system, 'REV5_COMPACT_SENSOR_BRIDGE')
        _member(bridge, _point(-19.0, 0, 104.0), _point(19.0, 0, 104.0),
                index, 'CENTRAL_SENSOR_CROSS', aluminum); index += 1
        _member(bridge, _point(0, -16.0, 104.0), _point(0, 16.0, 104.0),
                index, 'CENTRAL_SENSOR_FORE_AFT', aluminum); index += 1
        # Minimal upper ties prevent portal-frame spreading without forming a cage.
        _member(bridge, _point(-19.0, -20.0, 132.0), _point(19.0, -20.0, 132.0),
                index, 'UPPER_REAR_TIE', aluminum); index += 1
        _member(bridge, _point(-19.0, 20.0, 132.0), _point(19.0, 20.0, 132.0),
                index, 'UPPER_FRONT_TIE', aluminum)

        system.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-R5F-001')
        system.attributes.add('PROJECT_FALCON_01', 'Architecture', 'Two open solar side frames around sealed upper pod')
        system.attributes.add('PROJECT_FALCON_01', 'Clearance', '320 mm pod plus nominal 20 mm radial service clearance')
        system.attributes.add('PROJECT_FALCON_01', 'Material', '25 mm 6061-T6 members; 316L isolated fasteners')
        system.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing pod, panels, and sensors were not moved')

        app.activeViewport.fit()
        ui.messageBox(
            'REV5_POD_DUAL_SOLAR_FRAME completed.\n\n'
            'Fresh frame independent of deleted legacy frames\n'
            'Two open structural sides: East and West\n'
            'Four deck feet and triangulated lower braces\n'
            'Three panel rails per side\n'
            'Compact sensor bridge above the sealed pod\n'
            'No circular cage or North/South panel frame\n\n'
            'Click Capture Position, save, then send a screenshot.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_POD_DUAL_SOLAR_FRAME failed:\n\n{}'.format(traceback.format_exc()), 'PROJECT FALCON-01')
