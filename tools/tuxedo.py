# GPL License

import bpy
import webbrowser
import addon_utils

from . import common as Common
from .register import register_wrap
from .translations import t

@register_wrap
class EnableTuxedo(bpy.types.Operator):
    bl_idname = 'cats_tuxedo.enable_tuxedo_blenderplugin'
    bl_label = t('EnableTuxedo.label')
    bl_description = t('EnableTuxedo.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # disable all wrong versions
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Tuxedo Blender Plugin":
                if mod.bl_info['version'] < (0, 1, 0) and addon_utils.check(mod.__name__)[0]:
                    try:
                        if Common.version_2_79_or_older():
                            bpy.ops.wm.addon_disable(module=mod.__name__)
                        else:
                            bpy.ops.preferences.addon_disable(module=mod.__name__)
                    except:
                        pass
                    continue

        # then enable correct version
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Tuxedo Blender Plugin":
                if mod.bl_info['version'] < (0, 1, 0):
                    continue
                if not addon_utils.check(mod.__name__)[0]:
                    if Common.version_2_79_or_older():
                        bpy.ops.wm.addon_enable(module=mod.__name__)
                    else:
                        bpy.ops.preferences.addon_enable(module=mod.__name__)
                    break
        self.report({'INFO'}, t('EnableTuxedo.success'))
        return {'FINISHED'}


# Link to install
@register_wrap
class TuxedoButton(bpy.types.Operator):
    bl_idname = 'tuxedo.download_tuxedo'
    bl_label = t('TuxedoButton.label')
    bl_description = t('TuxedoButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://github.com/feilen/tuxedo-blender-plugin/releases/')

        self.report({'INFO'}, 'TuxedoButton.success')
        return {'FINISHED'}

# Link to readme for help
@register_wrap
class TuxedoHelpButton(bpy.types.Operator):
    bl_idname = 'tuxedo.help'
    bl_label = t('TuxedoHelpButton.label')
    bl_description = t('TuxedoHelpButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('TuxedoHelpButton.URL'))

        self.report({'INFO'}, t('TuxedoHelpButton.success'))
        return {'FINISHED'}