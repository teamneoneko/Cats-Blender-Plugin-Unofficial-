# MIT License

import bpy

from .main import ToolPanel
from ..tools import rootbone as Rootbone
from ..tools.register import register_wrap
from ..tools.translations import t
from ..tools.common import wrap_dynamic_enum_items


@register_wrap
class SearchMenuOperator_root_bone(bpy.types.Operator):
    bl_description = t('Scene.root_bone.desc')
    bl_idname = "scene.search_menu_root_bone"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(
        name=t('Scene.root_bone.label'),
        description=t('Scene.root_bone.desc'),
        # get_parent_root_bones caches results so the wrapper cannot run in-place
        items=wrap_dynamic_enum_items(
            Rootbone.get_parent_root_bones, bl_idname, sort=False, in_place=False, is_holder=False
        ),
    )
    
    def execute(self, context):
        context.scene.root_bone = self.my_enum
        print(context.scene.root_bone)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}


@register_wrap
class BoneRootPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_boneroot_v3'
    bl_label = t('BoneRootPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        # Root bone selection
        selection_box = box.box()
        selection_col = selection_box.column(align=True)
        
        row = selection_col.row(align=True)
        row.scale_y = 1.2
        row.operator(SearchMenuOperator_root_bone.bl_idname, text=context.scene.root_bone, icon='BONE_DATA')

        # Action buttons
        actions_box = box.box()
        actions_col = actions_box.column(align=True)
        
        row = actions_col.row(align=True)
        row.scale_y = 1.2
        row.operator(Rootbone.RefreshRootButton.bl_idname, icon='FILE_REFRESH')
        row.operator(Rootbone.RootButton.bl_idname, icon='TRIA_RIGHT')

