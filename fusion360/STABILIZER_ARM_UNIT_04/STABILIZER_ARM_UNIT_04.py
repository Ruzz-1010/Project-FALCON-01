import importlib.util
import math
import os
import traceback

import adsk.core


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        source_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..',
            'STABILIZER_ARM_UNIT_02', 'STABILIZER_ARM_UNIT_02.py'
        ))
        spec = importlib.util.spec_from_file_location(
            'falcon_stabilizer_arm_unit_shared_04', source_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.COMPONENT_NAME = 'STABILIZER_ARM_UNIT_04'
        module.PART_NUMBER = 'FALCON-SAU-004'
        module.ARM_ANGLE = 3 * math.pi / 2
        module.ARM_X = 0
        module.ARM_Y = -43.0
        module.PLACEMENT = 'fourth (-Y) support-frame lug'
        module.run(context)
    except Exception:
        if ui:
            ui.messageBox(
                'STABILIZER_ARM_UNIT_04 loader failed:\n\n{}'.format(
                    traceback.format_exc()
                ),
                'PROJECT FALCON-01'
            )
