# MIT License

import bpy
import webbrowser

from .. import globs
from .. import updater
from .main import ToolPanel
from ..tools import common as Common
from ..tools import armature as Armature
from ..tools import importer as Importer
from ..tools import iconloader as Iconloader
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
        
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        sub = col.column(align=True)
        sub.scale_y = 0.75
        row.label(text=t('OtherOptionsPanel.fbtFix'), icon='ARMATURE_DATA')
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 0.1
        sub = col.column(align=True)
        row.label(text=t('OtherOptionsPanel.fbtFix1'), icon='BLANK1')
        col.separator()
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature_manual.FixFBTButton.bl_idname, text=t('OtherOptionsPanel.FixFBTButton.label'))
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature_manual.RemoveFBTButton.bl_idname, text=t('OtherOptionsPanel.RemoveFBTButton.label'))
        
        col.separator()
        col.separator()
        col.separator()
        
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(LegacyReadButton.bl_idname, icon_value=Iconloader.preview_collections["custom_icons"]["help1"].icon_id)
        
        col.separator()
        col.separator()
        
        
@register_wrap
class LegacyReadButton(bpy.types.Operator):
    bl_idname = 'legacy_read.help'
    bl_label = t('LegacyReadButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('LegacyReadButton.URL'))

        self.report({'INFO'}, t('LegacyReadButton.success'))
        return {'FINISHED'}
