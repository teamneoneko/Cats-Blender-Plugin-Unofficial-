# MIT License

import bpy

from .. import globs
from .main import ToolPanel
from .main import layout_split, add_button_with_small_button
from ..tools import translate as Translate
from ..tools import common as Common
from ..tools import armature_manual as Armature_manual
from ..tools import shapekey as Shapekey
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class OtherOptionsPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_OtherOptionsPanel_v3'
    bl_label = t('OtherOptionsPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        # Separate By section
        separate_box = box.box()
        separate_col = separate_box.column(align=True)
        row = layout_split(separate_col, factor=0.32, align=True)
        row.scale_y = 1.2
        row.label(text=t('OtherOptionsPanel.separateBy'), icon='MESH_DATA')
        row.operator(Armature_manual.SeparateByMaterials.bl_idname, text=t('OtherOptionsPanel.SeparateByMaterials.label'))
        row.operator(Armature_manual.SeparateByLooseParts.bl_idname, text=t('OtherOptionsPanel.SeparateByLooseParts.label'))
        row.operator(Armature_manual.SeparateByShapekeys.bl_idname, text=t('OtherOptionsPanel.SeparateByShapekeys.label'))

        # Translate section
        translate_box = box.box()
        translate_col = translate_box.column(align=True)
        
        header_row = translate_col.row(align=True)
        header_row.scale_y = 1.1
        header_row.label(text=t('OtherOptionsPanel.translate'), icon='FILE_REFRESH')

        row = translate_col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'use_google_only')

        split = layout_split(translate_col, factor=0.27, align=True)

        row = split.row(align=True)
        row.scale_y = 2
        row.operator(Translate.TranslateAllButton.bl_idname, text=t('OtherOptionsPanel.TranslateAllButton.label'), icon=globs.ICON_ALL)

        col = split.column(align=True)
        col.operator(Translate.TranslateShapekeyButton.bl_idname, text=t('OtherOptionsPanel.TranslateShapekeyButton.label'), icon='SHAPEKEY_DATA')
        col.operator(Translate.TranslateObjectsButton.bl_idname, text=t('OtherOptionsPanel.TranslateObjectsButton.label'), icon='MESH_DATA')

        col = split.column(align=True)
        col.operator(Translate.TranslateBonesButton.bl_idname, text=t('OtherOptionsPanel.TranslateBonesButton.label'), icon='BONE_DATA')
        col.operator(Translate.TranslateMaterialsButton.bl_idname, text=t('OtherOptionsPanel.TranslateMaterialsButton.label'), icon='MATERIAL')

        # More Options section
        more_box = box.box()
        more_col = more_box.column(align=True)
        
        row = more_col.row(align=True)
        row.scale_y = 0.85
        if not context.scene.show_more_options:
            row.prop(context.scene, 'show_more_options', icon=globs.ICON_ADD, emboss=True, expand=False, toggle=False, event=False)
        else:
            row.prop(context.scene, 'show_more_options', icon=globs.ICON_REMOVE, emboss=True, expand=False, toggle=False, event=False)
            
            # Normals section
            normals_box = more_col.box()
            normals_col = normals_box.column(align=True)
            row = layout_split(normals_col, factor=0.27, align=True)
            row.scale_y = 1.2
            row.label(text=t('OtherOptionsPanel.normals'), icon='SNAP_NORMAL')
            row.operator(Armature_manual.RecalculateNormals.bl_idname, text=t('OtherOptionsPanel.RecalculateNormals.label'))
            row.operator(Armature_manual.FlipNormals.bl_idname, text=t('OtherOptionsPanel.FlipNormals.label'))

            # Transformations and Shape Keys
            transforms_box = more_col.box()
            transforms_col = transforms_box.column(align=True)
            add_button_with_small_button(transforms_col, 
                                       Armature_manual.ApplyTransformations.bl_idname, 'OUTLINER_DATA_ARMATURE',
                                       Armature_manual.ApplyAllTransformations.bl_idname, globs.ICON_ALL, 
                                       scale=1.2)
            
            row = transforms_col.row(align=True)
            row.scale_y = 1.2
            row.operator(Shapekey.ShapeKeyPruner.bl_idname, icon='SHAPEKEY_DATA')
            
            row = transforms_col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_manual.RepairShapekeys.bl_idname, icon='MESH_DATA')
            
            row = transforms_col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_manual.OptimizeStaticShapekeys.bl_idname, icon='MESH_DATA')

            # Advanced Options
            advanced_box = more_col.box()
            advanced_col = advanced_box.column(align=True)
            
            add_button_with_small_button(advanced_col, 
                                       Armature_manual.CreateDigitigradeLegs.bl_idname, 'OUTLINER_DATA_ARMATURE',
                                       Armature_manual.DigitigradeTutorialButton.bl_idname, 'QUESTION', 
                                       scale=1.2)
            
            add_button_with_small_button(advanced_col, 
                                       Armature_manual.GenerateTwistBones.bl_idname, 'OUTLINER_DATA_ARMATURE',
                                       Armature_manual.TwistTutorialButton.bl_idname, 'QUESTION', 
                                       scale=1.2)
            
            row = advanced_col.row(align=True)
            row.scale_y = 1.2
            row.prop(context.scene, 'generate_twistbones_upper')

            # Additional Options
            extra_box = more_col.box()
            extra_col = extra_box.column(align=True)
            
            row = extra_col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_manual.FixVRMShapesButton.bl_idname, icon='SHAPEKEY_DATA')

            row = extra_col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_manual.ConvertToValveButton.bl_idname, icon='SMALL_CAPS')
