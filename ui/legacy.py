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
from .main import layout_split
from ..tools.translations import t
from ..tools import decimation as Decimation


@register_wrap
class AutoDecimatePresetGoodCats(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_good'
    bl_label = t('DecimationPanel.preset.good.label')
    bl_description = t('DecimationPanel.preset.good.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.max_tris = 70000
        return {'FINISHED'}

@register_wrap
class AutoDecimatePresetExcellentCats(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_excellent'
    bl_label = t('DecimationPanel.preset.excellent.label')
    bl_description = t('DecimationPanel.preset.excellent.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.max_tris = 32000
        return {'FINISHED'}

@register_wrap
class AutoDecimatePresetQuestCats(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_quest'
    bl_label = t('DecimationPanel.preset.quest.label')
    bl_description = t('DecimationPanel.preset.quest.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.max_tris = 5000
        return {'FINISHED'}

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
        col.separator()
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature_manual.FixFBTButton.bl_idname, text=t('OtherOptionsPanel.FixFBTButton.label'))
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature_manual.RemoveFBTButton.bl_idname, text=t('OtherOptionsPanel.RemoveFBTButton.label'))
        col.separator()       
        col = box.column(align=True)
        row = col.column(align=True)
        row.scale_y = 0.75
        row.label(text=t('DecimationLegacy.info1'), icon='INFO')
        row.label(text=t('DecimationLegacy.info2'), icon='BLANK1')
        row.label(text=t('DecimationLegacy.info3'), icon='BLANK1')
        col.separator()       
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator(LegacyDecimationButton.bl_idname, icon_value=Iconloader.preview_collections['custom_icons']['help1'].icon_id)
        col.separator()
        col.separator() 
        row = col.row(align=True)
        row.label(text=t('DecimationPanel.decimationMode'))
        row = col.row(align=True)
        row.prop(context.scene, 'decimation_mode', expand=True)
        row = col.row(align=True)
        row.scale_y = 0.7
        if context.scene.decimation_mode == 'SAFE':
            row.label(text=t('DecimationPanel.safeModeDesc'))
        elif context.scene.decimation_mode == 'HALF':
            row.label(text=t('DecimationPanel.halfModeDesc'))
        elif context.scene.decimation_mode == 'FULL':
            row.label(text=t('DecimationPanel.fullModeDesc'))

        elif context.scene.decimation_mode == 'CUSTOM':
            col.separator()

            if len(Common.get_meshes_objects(check=False)) <= 1:
                row = col.row(align=True)
                row.label(text=t('DecimationPanel.customSeparateMaterials'))
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator(Armature_manual.SeparateByMaterials.bl_idname, text=t('DecimationPanel.SeparateByMaterials.label'), icon='PLAY')
                return
            else:
                row = col.row(align=True)
                row.label(text=t('DecimationPanel.customJoinMeshes'))
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator(Armature_manual.JoinMeshes.bl_idname, icon='PAUSE')

            col.separator()
            col.separator()
            row = col.row(align=True)
            row.label(text=t('DecimationPanel.customWhitelist'))
            row = col.row(align=True)
            row.prop(context.scene, 'selection_mode', expand=True)
            col.separator()
            col.separator()

            if context.scene.selection_mode == 'SHAPES':
                row = layout_split(col, factor=0.7, align=False)
                row.prop(context.scene, 'add_shape_key', icon='SHAPEKEY_DATA')
                row.operator(Decimation.AddShapeButton.bl_idname, icon=globs.ICON_ADD)
                col.separator()

                box2 = col.box()
                col = box2.column(align=True)

                if len(Decimation.ignore_shapes) == 0:
                    col.label(text=t('DecimationPanel.warn.noShapekeySelected'))

                for shape in Decimation.ignore_shapes:
                    row = layout_split(col, factor=0.8, align=False)
                    row.label(text=shape, icon='SHAPEKEY_DATA')
                    op = row.operator(Decimation.RemoveShapeButton.bl_idname, text='', icon=globs.ICON_REMOVE)
                    op.shape_name = shape
            elif context.scene.selection_mode == 'MESHES':
                row = layout_split(col, factor=0.7, align=False)
                row.prop(context.scene, 'add_mesh', icon='MESH_DATA')
                row.operator(Decimation.AddMeshButton.bl_idname, icon=globs.ICON_ADD)
                col.separator()

                if Common.is_enum_empty(context.scene.add_mesh):
                    row = col.row(align=True)
                    col.label(text=t('DecimationPanel.warn.noDecimation'), icon='ERROR')

                box2 = col.box()
                col = box2.column(align=True)

                if len(Decimation.ignore_meshes) == 0:
                    col.label(text=t('DecimationPanel.warn.noMeshSelected'))

                for mesh in Decimation.ignore_meshes:
                    row = layout_split(col, factor=0.8, align=False)
                    row.label(text=mesh, icon='MESH_DATA')
                    op = row.operator(Decimation.RemoveMeshButton.bl_idname, text='', icon=globs.ICON_REMOVE)
                    op.mesh_name = mesh

            col = box.column(align=True)

            if len(Decimation.ignore_shapes) == 0 and len(Decimation.ignore_meshes) == 0:
                col.label(text=t('DecimationPanel.warn.emptyList'), icon='ERROR')
                row = col.row(align=True)
            else:
                col.label(text=t('DecimationPanel.warn.correctWhitelist'), icon='INFO')
                row = col.row(align=True)

        col.separator()
        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'decimate_fingers')
        row = col.row(align=True)
        row.prop(context.scene, 'decimation_remove_doubles')
        row = col.row(align=True)
        row.prop(context.scene, 'decimation_retain_separated_meshes', expand=True)
        row = col.row(align=True)
        row.operator(Decimation.AutoDecimatePresetGoodCats.bl_idname)
        row.operator(Decimation.AutoDecimatePresetExcellentCats.bl_idname)
        row.operator(Decimation.AutoDecimatePresetQuestCats.bl_idname)
        row = col.row(align=True)
        row.prop(context.scene, 'max_tris')
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator(Decimation.AutoDecimateButtonCats.bl_idname, icon='MOD_DECIM')
        col.separator()       
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator(DecimationHelpButton.bl_idname, icon_value=Iconloader.preview_collections['custom_icons']['help1'].icon_id)
        
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
    
@register_wrap
class LegacyDecimationButton(bpy.types.Operator):
    bl_idname = 'legacy_decimation.help'
    bl_label = t('LegacyDecimationButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('LegacyDecimationButton.URL'))

        self.report({'INFO'}, t('LegacyDecimationButton.success'))
        return {'FINISHED'}
        
@register_wrap
class DecimationHelpButton(bpy.types.Operator):
    bl_idname = 'legacy_helpdecimation.help'
    bl_label = t('DecimationHelpButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('DecimationHelpButton.URL'))

        self.report({'INFO'}, t('DecimationHelpButton.success'))
        return {'FINISHED'}
