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


def _assign_hdpe(app, body):
    for library in app.materialLibraries:
        for name in ('HDPE', 'High Density Polyethylene', 'Polyethylene, High Density'):
            material = library.materials.itemByName(name)
            if material:
                body.material = material
                return True
    return False


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
        if _find_occurrence(root, 'STABILIZER_BUOY_01'):
            raise RuntimeError('STABILIZER_BUOY_01 already exists; nothing was changed.')
        if not _find_occurrence(root, 'STABILIZER_ARM'):
            raise RuntimeError('The approved first STABILIZER_ARM was not found.')

        parameters = design.userParameters
        _add_parameter(parameters, 'stabilizer_buoy_OD', '240 mm', 'mm', 'Spherical buoy outside diameter')
        _add_parameter(parameters, 'stabilizer_buoy_wall', '6 mm', 'mm', 'Rotomolded HDPE wall')
        _add_parameter(parameters, 'stabilizer_buoy_center_radius', '1025 mm', 'mm', 'Distance from main buoy axis')
        _add_parameter(parameters, 'stabilizer_buoy_center_z', '106 mm', 'mm', 'Aligned with stabilizer arm center')

        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        component = occurrence.component
        component.name = 'STABILIZER_BUOY_01'

        sketch = component.sketches.add(component.xZConstructionPlane)
        sketch.name = 'SKETCH_01_HOLLOW_SPHERICAL_PROFILE'
        lines = sketch.sketchCurves.sketchLines
        arcs = sketch.sketchCurves.sketchArcs

        axis = lines.addByTwoPoints(
            adsk.core.Point3D.create(0, -13.0, 0),
            adsk.core.Point3D.create(0, 13.0, 0)
        )
        axis.isConstruction = True

        outer_bottom = adsk.core.Point3D.create(0, -12.0, 0)
        outer_side = adsk.core.Point3D.create(12.0, 0, 0)
        outer_top = adsk.core.Point3D.create(0, 12.0, 0)
        inner_bottom = adsk.core.Point3D.create(0, -11.4, 0)
        inner_side = adsk.core.Point3D.create(11.4, 0, 0)
        inner_top = adsk.core.Point3D.create(0, 11.4, 0)

        arcs.addByThreePoints(outer_bottom, outer_side, outer_top)
        lines.addByTwoPoints(outer_top, inner_top)
        arcs.addByThreePoints(inner_top, inner_side, inner_bottom)
        lines.addByTwoPoints(inner_bottom, outer_bottom)

        if sketch.profiles.count != 1:
            raise RuntimeError(
                'Unexpected buoy profile count. Nothing outside the new component was changed.'
            )

        revolves = component.features.revolveFeatures
        revolve_input = revolves.createInput(
            sketch.profiles.item(0), axis,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        revolve_input.setAngleExtent(False, _value('360 deg'))
        revolve = revolves.add(revolve_input)
        revolve.name = 'REVOLVE_01_HOLLOW_HDPE_BUOY'
        body = revolve.bodies.item(0)
        body.name = 'STABILIZER_BUOY_01_HDPE_BODY'

        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(102.5, 0, 10.6)
        occurrence.transform2 = transform

        assigned = _assign_hdpe(app, body)
        component.attributes.add('PROJECT_FALCON_01', 'PartNumber', 'FALCON-SB-001')
        component.attributes.add('PROJECT_FALCON_01', 'Material', 'Rotomolded marine-grade HDPE')
        component.attributes.add('PROJECT_FALCON_01', 'Construction', 'Hollow 240 mm sphere; 6 mm wall')
        component.attributes.add('PROJECT_FALCON_01', 'Interface', 'Separate external aluminum cradle required')
        component.attributes.add('PROJECT_FALCON_01', 'Safety', 'Existing components untouched')

        app.activeViewport.fit()
        note = '' if assigned else '\nAssign HDPE manually if unavailable locally.'
        ui.messageBox(
            'STABILIZER_BUOY_01 completed.\n\n'
            'Outside diameter: 240 mm\nWall: 6 mm HDPE\n'
            'Position: end of first stabilizer arm\n'
            'The separate holding cradle is the next component.\n'
            'No existing component was moved or edited.' + note,
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_BUOY_01 generation failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
