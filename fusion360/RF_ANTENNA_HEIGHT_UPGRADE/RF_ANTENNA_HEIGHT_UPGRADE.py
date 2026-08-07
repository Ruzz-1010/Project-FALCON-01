import adsk.core
import adsk.fusion
import traceback


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


def _stretch_height(component, factor, feature_name):
    scales = component.features.scaleFeatures
    if scales.itemByName(feature_name):
        raise RuntimeError('{} is already upgraded.'.format(component.name))
    entities = adsk.core.ObjectCollection.create()
    for body in component.bRepBodies:
        entities.add(body)
    if entities.count == 0:
        raise RuntimeError('{} contains no bodies.'.format(component.name))
    scale_input = scales.createInput(
        entities,
        component.originConstructionPoint,
        adsk.core.ValueInput.createByReal(1.0)
    )
    success = scale_input.setToNonUniform(
        adsk.core.ValueInput.createByReal(1.0),
        adsk.core.ValueInput.createByReal(1.0),
        adsk.core.ValueInput.createByReal(factor)
    )
    if not success:
        raise RuntimeError('Fusion rejected the editable Z-height scale for {}.'.format(component.name))
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

        lte_occurrence = _find_occurrence(root, 'LTE_4G_ANTENNA')
        wifi_occurrence = _find_occurrence(root, 'WIFI_ANTENNA')
        if not lte_occurrence or not wifi_occurrence:
            raise RuntimeError(
                'LTE_4G_ANTENNA or WIFI_ANTENNA was not found. Run TOP_SENSOR_ARRAY first.'
            )
        if lte_occurrence.component.features.scaleFeatures.itemByName('SCALE_01_TALL_RF_MAST'):
            raise RuntimeError('RF antenna height upgrade already exists; nothing was changed.')

        parameters = design.userParameters
        _add_parameter(parameters, 'lte_upgraded_total_height', '350 mm', 'mm', 'Raised LTE antenna assembly')
        _add_parameter(parameters, 'wifi_upgraded_total_height', '320 mm', 'mm', 'Raised Wi-Fi antenna assembly')

        _stretch_height(
            lte_occurrence.component, 350.0 / 242.0,
            'SCALE_01_TALL_RF_MAST'
        )
        _stretch_height(
            wifi_occurrence.component, 320.0 / 202.0,
            'SCALE_01_TALL_RF_MAST'
        )
        lte_occurrence.component.attributes.add(
            'PROJECT_FALCON_01', 'UpgradedHeight', '350 mm'
        )
        wifi_occurrence.component.attributes.add(
            'PROJECT_FALCON_01', 'UpgradedHeight', '320 mm'
        )
        app.activeViewport.fit()
        ui.messageBox(
            'RF antenna height upgrade completed.\n\n'
            '4G/LTE assembly height: 350 mm\n'
            'Wi-Fi assembly height: 320 mm\n'
            'Diameter and X/Y placement were unchanged.\n'
            'Both Z-height Scale features remain editable.\n'
            'No other component was moved or edited.',
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox(
                'RF_ANTENNA_HEIGHT_UPGRADE failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
