# GPL License

import bpy

from .. import globs
from .main import ToolPanel
from .main import layout_split, add_button_with_small_button
from ..tools import translate as Translate
from ..tools import common as Common
from ..tools import armature_manual as Armature_manual
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
        button_height = 1

        col = box.column(align=True)
        row = layout_split(col, factor=0.32, align=True)
        row.scale_y = button_height
        row.label(text="Separate by:", icon='MESH_DATA')
        row.operator(Armature_manual.SeparateByMaterials.bl_idname, text=t('OtherOptionsPanel.SeparateByMaterials.label'))
        row.operator(Armature_manual.SeparateByLooseParts.bl_idname, text=t('OtherOptionsPanel.SeparateByLooseParts.label'))
        row.operator(Armature_manual.SeparateByShapekeys.bl_idname, text=t('OtherOptionsPanel.SeparateByShapekeys.label'))

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text=t('OtherOptionsPanel.joinMeshes'), icon='AUTOMERGE_ON')
        row.operator(Armature_manual.JoinMeshes.bl_idname, text=t('OtherOptionsPanel.JoinMeshes.label'))
        row.operator(Armature_manual.JoinMeshesSelected.bl_idname, text=t('OtherOptionsPanel.JoinMeshesSelected.label'))

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text=t('OtherOptionsPanel.mergeWeights'), icon='BONE_DATA')
        row.operator(Armature_manual.MergeWeights.bl_idname, text=t('OtherOptionsPanel.MergeWeights.label'))
        row.operator(Armature_manual.MergeWeightsToActive.bl_idname, text=t('OtherOptionsPanel.MergeWeightsToActive.label'))

        row = col.row(align=True)
        row.scale_y = 0.75
        row.prop(context.scene, 'keep_merged_bones')
        row = col.row(align=True)
        row.scale_y = 0.75
        row.prop(context.scene, 'merge_visible_meshes_only')

        # Translate
        col.separator()
        row = col.row(align=True)
        row.label(text=t('OtherOptionsPanel.translate'), icon='FILE_REFRESH')

        row = col.row(align=True)
        row.scale_y = button_height
        row.prop(context.scene, 'use_google_only')

        split = layout_split(col, factor=0.27, align=True)

        row = split.row(align=True)
        row.scale_y = 2
        row.operator(Translate.TranslateAllButton.bl_idname, text=t('OtherOptionsPanel.TranslateAllButton.label'), icon=globs.ICON_ALL)

        row = split.column(align=True)
        row.operator(Translate.TranslateShapekeyButton.bl_idname, text=t('OtherOptionsPanel.TranslateShapekeyButton.label'), icon='SHAPEKEY_DATA')
        row.operator(Translate.TranslateObjectsButton.bl_idname, text=t('OtherOptionsPanel.TranslateObjectsButton.label'), icon='MESH_DATA')

        row = split.column(align=True)
        row.operator(Translate.TranslateBonesButton.bl_idname, text=t('OtherOptionsPanel.TranslateBonesButton.label'), icon='BONE_DATA')
        row.operator(Translate.TranslateMaterialsButton.bl_idname, text=t('OtherOptionsPanel.TranslateMaterialsButton.label'), icon='MATERIAL')

        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.85

        if not context.scene.show_more_options:
            row.prop(context.scene, 'show_more_options', icon=globs.ICON_ADD, emboss=True, expand=False, toggle=False, event=False)
        else:
            row.prop(context.scene, 'show_more_options', icon=globs.ICON_REMOVE, emboss=True, expand=False, toggle=False, event=False)

            col.separator()
            row = layout_split(col, factor=0.24, align=True)
            row.scale_y = button_height
            row.label(text=t('OtherOptionsPanel.delete'), icon='X')
            row2 = layout_split(row, factor=0.61, align=True)
            row2.operator(Armature_manual.RemoveZeroWeightBones.bl_idname, text=t('OtherOptionsPanel.RemoveZeroWeightBones.label'))
            row2.operator(Armature_manual.RemoveConstraints.bl_idname, text=t('OtherOptionsPanel.RemoveConstraints'))

            row = layout_split(col, factor=0.24, align=True)
            row.scale_y = button_height
            row.label(text="")
            row.operator(Armature_manual.RemoveZeroWeightGroups.bl_idname, text=t('OtherOptionsPanel.RemoveZeroWeightGroups'))

            col.separator()
            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.DuplicateBonesButton.bl_idname, icon='GROUP_BONE')
            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.ConnectBonesButton.bl_idname, icon='CONSTRAINT_BONE')

            col.separator()
            row = layout_split(col, factor=0.27, align=True)
            row.scale_y = button_height
            row.label(text=t('OtherOptionsPanel.normals'), icon='SNAP_NORMAL')
            row.operator(Armature_manual.RecalculateNormals.bl_idname, text=t('OtherOptionsPanel.RecalculateNormals.label'))
            row.operator(Armature_manual.FlipNormals.bl_idname, text=t('OtherOptionsPanel.FlipNormals.label'))

            add_button_with_small_button(col, Armature_manual.ApplyTransformations.bl_idname, 'OUTLINER_DATA_ARMATURE',
                                              Armature_manual.ApplyAllTransformations.bl_idname, globs.ICON_ALL, scale=button_height)

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.RemoveDoubles.bl_idname, icon='X')
            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.RepairShapekeys.bl_idname, icon='MESH_DATA')
            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.OptimizeStaticShapekeys.bl_idname, icon='MESH_DATA')


            col.separator()
            add_button_with_small_button(col, Armature_manual.CreateDigitigradeLegs.bl_idname, 'OUTLINER_DATA_ARMATURE',
                                                Armature_manual.DigitigradeTutorialButton.bl_idname, 'QUESTION', scale=button_height)
            col.separator()
            add_button_with_small_button(col, Armature_manual.GenerateTwistBones.bl_idname, 'OUTLINER_DATA_ARMATURE',
                                            Armature_manual.TwistTutorialButton.bl_idname, 'QUESTION', scale=button_height)
            row = col.row(align=True)
            row.scale_y = button_height
            row.prop(context.scene, 'generate_twistbones_upper')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.FixVRMShapesButton.bl_idname, icon='SHAPEKEY_DATA')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(Armature_manual.ConvertToValveButton.bl_idname, icon='SMALL_CAPS')

            if globs.dev_branch:
                row = col.row(align=True)
                row.scale_y = button_height
                row.operator(Armature_manual.TestButton.bl_idname)

            # row = col.row(align=True)
            # row.scale_y = button_height
            # row.operator(Armature_manual.SeparateByCopyProtection.bl_idname, icon='SHAPEKEY_DATA')
