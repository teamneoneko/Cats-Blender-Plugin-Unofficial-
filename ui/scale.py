# MIT License

# (global-set-key (kbd "C-c m") (lambda () (interactive) (shell-command "zip -r ../../cats-dev.zip ../../cats-blender-plugin")))

# MIT License

import bpy
import addon_utils
from importlib import import_module
from importlib.util import find_spec

from .main import ToolPanel
from ..tools import scale as Scaler

from ..tools.translations import t
from ..tools.register import register_wrap

draw_imscale_ui = None
imscale_is_disabled = False
old_imscale_version = False

def check_for_imscale():
    global draw_imscale_ui, old_imscale_version, imscale_is_disabled

    draw_imscale_ui = None

    # Check if using immersive scaler shipped with cats
    if find_spec("imscale") and find_spec("imscale.immersive_scaler"):
        import imscale.immersive_scaler as imscale
        draw_imscale_ui = imscale.ui.draw_ui
        return

    # Check if it's present in blender anyway (installed separately)
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Immersive Scaler":
            if mod.bl_info['version'] < (0, 5, 2):
                old_imscale_version = True
                continue
            if not addon_utils.check(mod.__name__)[0]:
                imscale_is_disabled = True
                continue

            old_imscale_version = False
            imscale_is_disabled = False
            draw_imscale_ui = getattr(import_module(mod.__name__ + '.ui'), 'draw_ui')
            break

@register_wrap
class ScalingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_scale_v2'
    bl_label = t('ScalingPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        # Help button section
        help_box = box.box()
        help_col = help_box.column(align=True)
        help_col.scale_y = 1.2
        help_col.operator(Scaler.ImmersiveScalerHelpButton.bl_idname, icon='QUESTION')

        # Status section
        if imscale_is_disabled:
            self.draw_disabled_message(box)
        elif old_imscale_version:
            self.draw_outdated_message(box)
        elif not draw_imscale_ui:
            self.draw_not_installed_message(box)
        else:
            return draw_imscale_ui(context, layout)

        check_for_imscale()

    def draw_disabled_message(self, box):
        message_box = box.box()
        message_col = message_box.column(align=True)
        
        message_col.separator(factor=1.5)
        
        info_col = message_col.column(align=True)
        info_col.scale_y = 0.75
        info_col.label(text=t('ScalingPanel.imscaleDisabled1'), icon='ERROR')
        info_col.label(text=t('ScalingPanel.imscaleDisabled2'), icon='BLANK1')
        
        message_col.separator(factor=1.5)
        
        row = message_col.row(align=True)
        row.scale_y = 1.2
        row.operator(Scaler.EnableIMScale.bl_idname, icon='CHECKBOX_HLT')

    def draw_outdated_message(self, box):
        message_box = box.box()
        message_col = message_box.column(align=True)
        
        message_col.separator(factor=1.5)
        
        info_col = message_col.column(align=True)
        info_col.scale_y = 0.75
        info_col.label(text=t('ScalingPanel.imscaleOldVersion1'), icon='ERROR')
        info_col.label(text=t('ScalingPanel.imscaleNotInstalled2'), icon='BLANK1')
        
        message_col.separator(factor=1.5)
        
        row = message_col.row(align=True)
        row.scale_y = 1.2
        row.operator(Scaler.ImmersiveScalerButton.bl_idname, icon='CHECKBOX_HLT')

    def draw_not_installed_message(self, box):
        message_box = box.box()
        message_col = message_box.column(align=True)
        
        message_col.separator(factor=1.5)
        
        info_col = message_col.column(align=True)
        info_col.scale_y = 0.75
        info_col.label(text=t('ScalingPanel.imscaleNotInstalled1'), icon='ERROR')
        info_col.label(text=t('ScalingPanel.imscaleNotInstalled2'), icon='BLANK1')
        
        message_col.separator(factor=1.5)
        
        row = message_col.row(align=True)
        row.scale_y = 1.2
        row.operator(Scaler.ImmersiveScalerButton.bl_idname, icon='CHECKBOX_HLT')
