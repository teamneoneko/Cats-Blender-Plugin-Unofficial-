# GPL License

import bpy
import webbrowser

from .. import globs
from .. import updater
from .main import ToolPanel
from ..tools import common as Common
from ..tools import armature as Armature
from ..tools import importer as Importer
from ..tools import supporter as Supporter
from ..tools import eyetracking as Eyetracking
from ..tools import armature_manual as Armature_manual
from ..tools.register import register_wrap
from ..tools.translations import t

@register_wrap
class LegacyStuff(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_legacy_stuff'
    bl_label = t('LegacyStuff.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        sub = col.column(align=True)
        sub.scale_y = 0.75
        sub.label(text=t("LegacyStuff.info1"), icon='INFO')
        sub.label(text=t("LegacyStuff.info2"), icon='BLANK1')
        
        col.separator()
        col.separator()
        sub = col.column(align=True)
        sub.scale_y = 0.75
        sub.label(text=t("FixLegacyStuff.info1"), icon='INFO')
        sub.label(text=t("FixLegacyStuff.info2"), icon='BLANK1')
        sub.label(text=t("FixLegacyStuff.info3"), icon='BLANK1')
        
        col.separator()
        col.separator()

        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature.FixArmature.bl_idname, icon=globs.ICON_FIX_MODEL)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = 1.5
        row.operator(ModelSettings.bl_idname, text="", icon='MODIFIER')

        col.separator()
        col.separator()
        
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        sub = col.column(align=True)
        sub.scale_y = 0.75
        row.label(text=t('ManualPanel.fbtFix'), icon='ARMATURE_DATA')
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 0.1
        sub = col.column(align=True)
        row.label(text=t('ManualPanel.fbtFix1'), icon='BLANK1')
        col.separator()
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature_manual.FixFBTButton.bl_idname, text=t('ManualPanel.FixFBTButton.label'))
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature_manual.RemoveFBTButton.bl_idname, text=t('ManualPanel.RemoveFBTButton.label'))
        
        col.separator()
        col.separator()
        col.separator()
        
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(LegacyReadButton.bl_idname, icon_value=Supporter.preview_collections["custom_icons"]["help1"].icon_id)
        
        col.separator()
        col.separator()
        
        
@register_wrap
class LegacyReadButton(bpy.types.Operator):
    bl_idname = 'cats_credits.help'
    bl_label = t('LegacyReadButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('LegacyReadButton.URL'))

        self.report({'INFO'}, t('LegacyReadButton.success'))
        return {'FINISHED'}

@register_wrap        
class ModelSettings(bpy.types.Operator):
    bl_idname = "cats_armature.settings"
    bl_label = t('ModelSettings.label')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 3.25))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.active = context.scene.remove_zero_weight
        row.prop(context.scene, 'keep_end_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'keep_upper_chest')
        row = col.row(align=True)
        row.prop(context.scene, 'keep_twist_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'fix_twist_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'join_meshes')
        row = col.row(align=True)
        row.prop(context.scene, 'connect_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'fix_materials')
        row = col.row(align=True)
        row.prop(context.scene, 'combine_mats')
        row = col.row(align=True)
        row.prop(context.scene, 'remove_zero_weight')
        row = col.row(align=True)
        row.prop(context.scene, 'remove_rigidbodies_joints')

        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.7
        row.label(text=t('ModelSettings.warn.fbtFix1'), icon='INFO')
        row = col.row(align=True)
        row.scale_y = 0.7
        row.label(text=t('ModelSettings.warn.fbtFix2'), icon_value=Supporter.preview_collections["custom_icons"]["empty"].icon_id)
        row = col.row(align=True)
        row.scale_y = 0.7
        row.label(text=t('ModelSettings.warn.fbtFix3'), icon_value=Supporter.preview_collections["custom_icons"]["empty"].icon_id)
        col.separator()