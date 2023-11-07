# GPL License

import bpy
import addon_utils
from importlib import import_module
from importlib.util import find_spec

from .main import ToolPanel
from ..tools import tuxedo as Tuxedo

from ..tools.translations import t
from ..tools.register import register_wrap

draw_tuxedo_ui = None
tuxedo_is_disabled = False
old_tuxedo_version = False

def check_for_tuxedo():
    global draw_tuxedo_ui, old_tuxedo_version, tuxedo_is_disabled

    draw_tuxedo_ui = None

    # Check if using tuxedo shipped with cats
    if find_spec("tuxedo") and find_spec("tuxedo.tuxedoexternal"):
        import tuxedo.tuxedoexternal as tuxedo
        draw_tuxedo_ui = tuxedo.ui.draw_ui
        return

    # Check if it's present in blender anyway (installed separately)
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Tuxedo Blender Plugin":
            # print(mod.__name__, mod.bl_info['version'])
            # print(addon_utils.check(mod.__name__))
            if mod.bl_info['version'] < (0, 1, 0):
                old_tuxedo_version = True
                # print('TOO OLD!')
                continue
            if not addon_utils.check(mod.__name__)[0]:
                tuxedo_is_disabled = True
                # print('DISABLED!')
                continue

            # print('FOUND!')
            old_tuxedo_version = False
            tuxedo_is_disabled = False
            draw_tuxedo_ui = getattr(import_module(mod.__name__ + '.ui'), 'draw')

            break

@register_wrap
class TuxedoPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_tuxedo'
    bl_label = t('TuxedoPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator(Tuxedo.TuxedoHelpButton.bl_idname, icon='QUESTION')

        # Installed but disabled
        if tuxedo_is_disabled:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)

            row.scale_y = 0.75
            row.label(text=t('TuxedoPanel.tuxedoDisabled1'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('TuxedoPanel.tuxedoDisabled2'))
            col.separator()
            row = col.row(align=True)
            row.operator(Tuxedo.EnableTuxedo.bl_idname, icon='CHECKBOX_HLT')
            check_for_tuxedo()
            return None

        # Currently, instructions for an old version are the same as
        # it not being installed - a manual install either way.
        if old_tuxedo_version:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)

            row.scale_y = 0.75
            row.label(text=t('TuxedoPanel.tuxedoOldVersion1'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('TuxedoPanel.tuxedoNotInstalled2'))
            col.separator()
            row = col.row(align=True)
            row.operator(Tuxedo.TuxedoButton.bl_idname, icon='CHECKBOX_HLT')

            check_for_tuxedo()
            return None

        # Tuxedo is not found
        if not draw_tuxedo_ui:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)

            row.scale_y = 0.75
            row.label(text=t('Tuxedo.tuxedoNotInstalled1'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('Tuxedo.tuxedoNotInstalled2'))
            col.separator()
            row = col.row(align=True)
            row.operator(Tuxedo.TuxedoButton.bl_idname, icon='CHECKBOX_HLT')
            check_for_tuxedo()
            return None

            check_for_tuxedo()
            return None


        # tuxedo = __import__('tuxedo')
        return draw_tuxedo_ui(context, layout)