import adsk.core
import adsk.fusion
import traceback


ACTIVE_PREFIXES = (
    'TOP_CAP',
    'BALLAST_SUSPENSION_CHAIN',
    'BALLAST',
    'MAIN_FLOAT_EDGE_FAIRING',
    'TOP_SENSOR_ARRAY',
    'NAVIGATION_LIGHT',
    'ANCHOR_MOORING_SYSTEM',
    'MAIN_FLOAT_TRADITIONAL_V2',
    'DUAL_30W_SOLAR_ARRAY',
    'SEALED_POD_THERMAL_SYSTEM',
    'UPPER_POD_ELECTRONICS_LAYOUT',
    'POD_MARINE_PROTECTION_HARDWARE',
    'ADJUSTABLE_LOW_BALLAST_V2',
    'BALLAST_V2_ANCHOR_CONNECTOR',
    'REV5_MAIN_BUOY_FRAME_SUPPORT',
    'REV5_TAPERED_MARINE_MAST',
    'REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE_V2',
    'REV5_RECTANGULAR_MARINE_ELECTRONICS_POD',
    'REV5_TOWER_FRONT_MAINTENANCE_GATE',
    'WATER_PRESSURE_SENSOR_ASSEMBLY_REV6_PROPOSED'
)

LEGACY_PREFIXES = (
    'SEALED_POD_THERMAL_SYSTEM',
    'REV5_LOWER_TO_MAIN_FRAME_SUPPORT_CAGE',
    'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE_V2',
    'REV5_FULL_HEIGHT_EXTERNAL_SUPPORT_CAGE',
    'REV5_UPPER_TO_LOWER_LOAD_CAGE',
    'UPPER_ALL_ELECTRONICS_POD',
    'UPPER_POD_ELECTRONICS_LAYOUT',
    'POD_MARINE_PROTECTION_HARDWARE',
    'MAIN_FLOAT',
    'ELECTRONICS_BOX',
    'LOWER_HOT_TRAY',
    'UPPER_CONTROL_TRAY',
    'INTAKE_FAN_MODULE',
    'EXHAUST_FAN_MODULE',
    'COOLING_DUCT_BAFFLE',
    'MAIN_BUOY_VENT_DUCTS',
    'MAIN_SUPPORT_FRAME',
    'UPPER_EQUIPMENT_FRAME',
    'UPPER_FRAME_SUPPORT_STANCHIONS',
    'COMPACT_ELEVATED_UPPER_TOWER',
    'DUAL_SOLAR_COMPACT_FRAME_V2',
    'TWO_SIDE_SOLAR_FRAME_V3',
    'REV5_POD_DUAL_SOLAR_FRAME',
    'SOLAR_PANEL_ARRAY',
    'SOLAR_PANEL_TILT_BRACKETS',
    'SOLAR_PANEL_ELEVATION_SUPPORTS',
    'SOLAR_PANEL_01_',
    'SOLAR_PANEL_02_',
    'SOLAR_PANEL_03_',
    'SOLAR_PANEL_04_',
    'STABILIZER_ARM',
    'STABILIZER_BUOY',
    'STABILIZER_TENSION_CABLE',
    'BALLAST_SUSPENSION_CHAIN',
    'BALLAST'
)


def _matches(name, prefixes):
    upper = name.upper().replace(' ', '_')
    return any(upper.startswith(prefix) for prefix in prefixes)


def _active_match(name):
    return _matches(name, ACTIVE_PREFIXES)


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
            raise RuntimeError('Click Capture Position, save, then run again.')

        found_active = set()
        hidden = 0
        shown = 0
        # Top-level occurrences are the assembly representation controls. Child
        # equipment remains controlled by its active parent occurrence.
        for occurrence in root.occurrences:
            name = occurrence.component.name
            if _active_match(name):
                occurrence.isLightBulbOn = True
                shown += 1
                for prefix in ACTIVE_PREFIXES:
                    if name.upper().replace(' ', '_').startswith(prefix):
                        found_active.add(prefix)
            elif _matches(name, LEGACY_PREFIXES):
                occurrence.isLightBulbOn = False
                hidden += 1

        missing = [name for name in ACTIVE_PREFIXES if name not in found_active]
        root.attributes.add('PROJECT_FALCON_01', 'ActiveMechanicalRevision', 'PROJECT FALCON V2 finalized export set')
        root.attributes.add('PROJECT_FALCON_01', 'AssemblyRepresentation', 'Matches exports/PROJECT FALCON -V2.fbx top-level systems')
        root.attributes.add('PROJECT_FALCON_01', 'CleanupSafety', 'Visibility only; no occurrence moved or deleted')
        root.attributes.add('PROJECT_FALCON_01', 'ExportStatus', 'CAD review required before R5 export')

        app.activeViewport.fit()
        missing_text = '\n'.join('- ' + item for item in missing) if missing else 'None'
        ui.messageBox(
            'REV5_FINAL_ASSEMBLY_CLEANUP completed.\n\n'
            'Active top-level systems shown: {}\n'
            'Legacy top-level systems hidden: {}\n'
            'Components moved or deleted: 0\n\n'
            'Missing required active systems:\n{}\n\n'
            'Capture Position and save. Inspect the complete assembly before export.'
            .format(shown, hidden, missing_text),
            'PROJECT FALCON-01'
        )
    except Exception:
        if ui:
            ui.messageBox('REV5_FINAL_ASSEMBLY_CLEANUP failed:\n\n{}'.format(traceback.format_exc()), 'PROJECT FALCON-01')
