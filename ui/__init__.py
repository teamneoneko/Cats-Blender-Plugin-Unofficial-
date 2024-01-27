# GPL License

if "bpy" not in locals():
    # print('STARTUP UI!!')
    import bpy
    from . import main
    from . import quickaccess
    from . import optimization
    from . import custom
    from . import otheroptions
    from . import mmdoptions
    from . import decimation
    from . import visemes
    from . import bone_root
    from . import optimization
    from . import scale
    from . import eye_tracking
    from . import legacy
    from . import copy_protection
    from . import settings_updates
    from . import credits
else:
    # print('RELOAD UI!!')
    import importlib
    importlib.reload(main)
    importlib.reload(quickaccess)
    importlib.reload(optimization)
    importlib.reload(custom)
    importlib.reload(otheroptions)
    importlib.reload(mmdoptions)
    importlib.reload(decimation)
    importlib.reload(visemes)
    importlib.reload(bone_root)
    importlib.reload(scale)
    importlib.reload(eye_tracking)
    importlib.reload(legacy)
    importlib.reload(copy_protection)
    importlib.reload(settings_updates)
    importlib.reload(credits)