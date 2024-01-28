# GPL License

import bpy
import addon_utils
from importlib import import_module

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import iconloader as Iconloader
from ..tools import atlas as Atlas
from ..tools import material as Material
from ..tools import bonemerge as Bonemerge
from ..tools import rootbone as Rootbone
from ..tools import armature_manual as Armature_manual

from ..tools.register import register_wrap
from ..tools.translations import t

draw_smc_ui = None
old_smc_version = False
smc_is_disabled = False
found_very_old_smc = False


def check_for_smc():
    global draw_smc_ui, old_smc_version, smc_is_disabled, found_very_old_smc

    draw_smc_ui = None
    found_very_old_smc = False

    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Shotariya-don":
            if hasattr(bpy.context.scene, 'shotariya_tex_idx'):
                found_very_old_smc = True
            continue
        if mod.bl_info['name'] == "Shotariya's Material Combiner":
            # print(mod.__name__, mod.bl_info['version'])
            # print(addon_utils.check(mod.__name__))
            if mod.bl_info['version'] < (2, 1, 2, 6):
                old_smc_version = True
                # print('TOO OLD!')
                continue
            if not addon_utils.check(mod.__name__)[0]:
                smc_is_disabled = True
                # print('DISABLED!')
                continue

            # print('FOUND!')
            old_smc_version = False
            smc_is_disabled = False
            found_very_old_smc = False
            draw_smc_ui = getattr(import_module(mod.__name__ + '.operators.ui.include'), 'draw_ui')
            break
            

@register_wrap
class OptimizePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_optimize_v3'
    bl_label = t('OptimizePanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'optimize_mode', expand=True)

        if context.scene.optimize_mode == 'ATLAS':

            col.label(text="For PBR/Normal maps, use Bake.", icon='INFO')

            col.separator()
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('OptimizePanel.atlasDesc'))

            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 0.9
            row.label(text=t('OptimizePanel.atlasAuthor'), icon_value=Iconloader.preview_collections["custom_icons"]["heart1"].icon_id)
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 0.9
            row.operator(Atlas.AtlasHelpButton.bl_idname, text="", icon='QUESTION')
            # row.separator()
            # row = split.row(align=False)
            # row.alignment = 'RIGHT'
            # row.scale_y = 0.9
            # row.operator(Atlas.AtlasHelpButton.bl_idname, text="", icon='QUESTION')
            col.separator()

            # If supported version is outdated
            if smc_is_disabled:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombDisabled1'))
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombDisabled2'))
                col.separator()
                row = col.row(align=True)
                row.operator(Atlas.EnableSMC.bl_idname, icon='CHECKBOX_HLT')

                check_for_smc()
                return

            # If old version is installed
            if old_smc_version:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated1'))
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated2'))

                col.separator()
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated3'))
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated4', location=t('OptimizePanel.matCombOutdated5_2.8')))

                col.separator()
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated6'))
                col.separator()
                row = col.row(align=True)
                row.operator(Atlas.ShotariyaButton.bl_idname, icon=globs.ICON_URL)

                check_for_smc()
                return

            # Found very old v1.0 mat comb
            if found_very_old_smc:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated1'))
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated2'))
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated6_alt'))
                col.separator()
                row = col.row(align=True)
                row.operator(Atlas.ShotariyaButton.bl_idname, icon=globs.ICON_URL)

                check_for_smc()
                return

            # If no matcomb is found
            if not draw_smc_ui:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombNotInstalled'))
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('OptimizePanel.matCombOutdated6_alt'))
                col.separator()
                row = col.row(align=True)
                row.operator(Atlas.ShotariyaButton.bl_idname, icon=globs.ICON_URL)

                check_for_smc()
                return

            if not hasattr(bpy.context.scene, 'smc_ob_data'):
                check_for_smc()
                return

            draw_smc_ui(context, col)

        elif context.scene.optimize_mode == 'MATERIAL':

            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(Material.CombineMaterialsButton.bl_idname, icon='MATERIAL')
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(Material.ConvertAllToPngButton.bl_idname, icon='IMAGE_RGB_ALPHA')
            col.separator()
            col.separator()
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.label(text=t('OtherOptionsPanel.joinMeshes'), icon='AUTOMERGE_ON')
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(Armature_manual.JoinMeshes.bl_idname, text=t('OtherOptionsPanel.JoinMeshes.label'))
            row.operator(Armature_manual.JoinMeshesSelected.bl_idname, text=t('OtherOptionsPanel.JoinMeshesSelected.label'))
            col.separator()

        elif context.scene.optimize_mode == 'BONEMERGING':
            if len(Common.get_meshes_objects(check=False)) > 1:
                row = box.row(align=True)
                row.prop(context.scene, 'merge_mesh')
            row = box.row(align=True)
            row.prop(context.scene, 'merge_bone')
            row = box.row(align=True)
            row.prop(context.scene, 'merge_ratio')
            row = box.row(align=True)
            col.separator()
            row.operator(Rootbone.RefreshRootButton.bl_idname, icon='FILE_REFRESH')
            row.operator(Bonemerge.BoneMergeButton.bl_idname, icon='AUTOMERGE_ON')
            
            col.separator()
            col.separator()
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.label(text=t('OtherOptionsPanel.mergeWeights'), icon='BONE_DATA')
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(Armature_manual.MergeWeights.bl_idname, text=t('OtherOptionsPanel.MergeWeights.label'))
            row.operator(Armature_manual.MergeWeightsToActive.bl_idname, text=t('OtherOptionsPanel.MergeWeightsToActive.label'))

            row = col.row(align=True)
            row.scale_y = 0.75
            row.prop(context.scene, 'keep_merged_bones')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.prop(context.scene, 'merge_visible_meshes_only')
