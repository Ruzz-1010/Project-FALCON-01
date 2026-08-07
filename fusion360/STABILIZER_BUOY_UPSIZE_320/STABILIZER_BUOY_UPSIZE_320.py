import adsk.core
import adsk.fusion
import traceback


BUOY_SCALE = 320.0 / 240.0
CRADLE_SCALE = 326.0 / 246.0


def _find_occurrence(root, component_name):
    for occurrence in root.allOccurrences:
        if occurrence.component.name.upper() == component_name.upper():
            return occurrence
    return None


def _value(expression):
    return adsk.core.ValueInput.createByString(expression)


def _add_parameter(parameters, name, expression, units, comment):
    existing = parameters.itemByName(name)
    if existing:
        return existing
    return parameters.add(name, _value(expression), units, comment)


def _scale_component(component, factor, feature_name):
    scales = component.features.scaleFeatures
    if scales.itemByName(feature_name):
        raise RuntimeError('{} is already upscaled.'.format(component.name))
    entities = adsk.core.ObjectCollection.create()
    for body in component.bRepBodies:
        entities.add(body)
    if entities.count == 0:
        raise RuntimeError('{} contains no solid bodies.'.format(component.name))
    scale_input = scales.createInput(
        entities,
        component.originConstructionPoint,
        adsk.core.ValueInput.createByReal(factor)
    )
    feature = scales.add(scale_input)
    feature.name = feature_name


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
        if not _find_occurrence(root, 'STABILIZER_BUOY_SYSTEM'):
            raise RuntimeError('STABILIZER_BUOY_SYSTEM was not found.')

        targets = []
        for index in range(1, 5):
            buoy_name = 'STABILIZER_BUOY_{:02d}'.format(index)
            cradle_name = 'STABILIZER_BUOY_CRADLE_{:02d}'.format(index)
            buoy = _find_occurrence(root, buoy_name)
            cradle = _find_occurrence(root, cradle_name)
            if not buoy or not cradle:
                raise RuntimeError(
                    '{} or {} was not found. Nothing was changed.'.format(
                        buoy_name, cradle_name
                    )
                )
            if buoy.component.features.scaleFeatures.itemByName('SCALE_01_UPSIZE_TO_320MM'):
                raise RuntimeError(
                    '{} is already 320 mm; nothing was changed.'.format(buoy_name)
                )
            targets.append((buoy.component, cradle.component))

        parameters = design.userParameters
        _add_parameter(parameters, 'upsize_stabilizer_buoy_OD', '320 mm', 'mm', 'Upsized stabilizer buoy diameter')
        _add_parameter(parameters, 'upsize_cradle_ID', '326 mm', 'mm', 'Upsized cradle inside diameter')
        _add_parameter(parameters, 'upsize_cradle_OD', '366 mm', 'mm', 'Approximate upsized cradle outside diameter')

        for buoy_component, cradle_component in targets:
            _scale_component(
                buoy_component, BUOY_SCALE, 'SCALE_01_UPSIZE_TO_320MM'
            )
            _scale_component(
                cradle_component, CRADLE_SCALE, 'SCALE_01_UPSIZE_FOR_320MM_BUOY'
            )
            buoy_component.attributes.add(
                'PROJECT_FALCON_01', 'UpsizedDiameter', '320 mm'
            )
            cradle_component.attributes.add(
                'PROJECT_FALCON_01', 'UpsizedInterface', '326 mm ID cradle'
            )

        app.activeViewport.fit()
        ui.messageBox(
            'All four stabilizer buoy units were upscaled.\n\n'
            'Buoy diameter: 240 mm -> 320 mm\n'
            'Cradle inside diameter: 246 mm -> 326 mm\n'
            'Each Scale feature remains editable in its component timeline.\n'
            'No arm, main float, ballast, electronics, or component position was changed.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_BUOY_UPSIZE_320 failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
