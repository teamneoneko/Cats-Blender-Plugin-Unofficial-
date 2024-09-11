# MIT License

import bpy

from .. import globs
from .. import updater
from .main import ToolPanel
from ..tools import common as Common
from ..tools import armature as Armature
from ..tools import importer as Importer
from ..tools import iconloader as Iconloader
from ..tools import material as Material
from ..tools import eyetracking as Eyetracking
from ..tools import armature_manual as Armature_manual
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class QuickAccessPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_quickaccess_v3'
    bl_label = t('QuickAccess.label')

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        updater.check_for_update_background(check_on_startup=True)
        updater.draw_update_notification_panel(box)

        col = box.column(align=True)

        if bpy.app.version < (4, 1, 0):
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.oldBlender1'), icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.oldBlender2'), icon='BLANK1')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.oldBlender3'), icon='BLANK1')
            col.separator()
            col.separator()

        if bpy.app.version > (4, 2, 99):
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.newBlender1'), icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.newBlender2'), icon='BLANK1')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.newBlender3'), icon='BLANK1')
            col.separator()
            col.separator()

        if not globs.dict_found:
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.noDict1'), icon='INFO')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.noDict2'), icon='BLANK1')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('QuickAccess.warn.noDict3'), icon='BLANK1')
            col.separator()
            col.separator()

        arm_count = len(Common.get_armature_objects())
        if arm_count == 0:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.7
            row.operator(Importer.ImportAnyModel.bl_idname, text=t('QuickAccess.ImportAnyModel.label'), icon='ARMATURE_DATA')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.7
            row.operator(Importer.ModelsPopup.bl_idname, text="", icon='COLLAPSEMENU')
            return
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.4
            row.operator(Importer.ImportAnyModel.bl_idname, text=t('QuickAccess.ImportAnyModel.label'), icon='ARMATURE_DATA')
            row.operator(Importer.ExporterModelsPopup.bl_idname, icon='ARMATURE_DATA')
            row = split.row(align=True)
            row.scale_y = 1.4
            row.operator(Importer.ModelsPopup.bl_idname, text="", icon='COLLAPSEMENU')

        if arm_count > 1:
            col.separator()
            col.separator()
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'armature', icon='ARMATURE_DATA')

        col.separator()
        col.separator()

        split = col.row(align=True)
        row = split.row(align=True)
        sub = col.column(align=True)
        sub.scale_y = 0.75
        sub.label(text=t("FixLegacy.info1"), icon='INFO')
        sub.label(text=t("FixLegacy.info2"), icon='BLANK1')
        row.scale_y = 1.5
        col.separator()
        col.separator()
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.1
        row.operator(Material.CombineMaterialsButton.bl_idname, text=t('QuickAccess.CombineMats.label'), icon='MATERIAL')
        row.operator(Armature_manual.JoinMeshes.bl_idname, text=t('QuickAccess.JoinMeshes.label'), icon_value=Iconloader.preview_collections["custom_icons"]["mesh"].icon_id)
        col.separator()
        col.separator()

        armature_obj = Common.get_armature()
        if not armature_obj or armature_obj.mode != 'POSE':
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.1
            row.operator(Armature_manual.StartPoseMode.bl_idname, icon='POSE_HLT')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.1
            row.operator(Armature_manual.StartPoseModeNoReset.bl_idname, text="", icon='POSE_HLT')
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.1
            row.operator(Armature_manual.StopPoseMode.bl_idname, icon=globs.ICON_POSE_MODE)
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.1
            row.operator(Armature_manual.StopPoseModeNoReset.bl_idname, text='', icon=globs.ICON_POSE_MODE)
            if armature_obj or armature_obj.mode != 'POSE':
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator(Armature_manual.PoseToShape.bl_idname, icon='SHAPEKEY_DATA')
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator(Armature_manual.PoseToRest.bl_idname, icon='POSE_HLT')

