# MIT License

import bpy

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import eyetracking as Eyetracking
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class SearchMenuOperatorBoneHead(bpy.types.Operator):
    bl_description = t('Scene.head.desc')
    bl_idname = "scene.search_menu_head"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(
        name="shapekeys",
        items=Common.wrap_dynamic_enum_items(Common.get_bones_head, bl_idname, is_holder=False),
    )

    def execute(self, context):
        context.scene.head = self.my_enum
        print(context.scene.head)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorBoneEyeLeft(bpy.types.Operator):
    bl_description = t('Scene.eye_left.desc')
    bl_idname = "scene.search_menu_eye_left"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(
        name="shapekeys",
        items=Common.wrap_dynamic_enum_items(Common.get_bones_eye_l, bl_idname, is_holder=False),
    )

    def execute(self, context):
        context.scene.eye_left = self.my_enum
        print(context.scene.eye_left)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorBoneEyeRight(bpy.types.Operator):
    bl_description = t('Scene.eye_right.desc')
    bl_idname = "scene.search_menu_eye_right"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(
        name="shapekeys",
        items=Common.wrap_dynamic_enum_items(Common.get_bones_eye_r, bl_idname, is_holder=False),
    )

    def execute(self, context):
        context.scene.eye_right = self.my_enum
        print(context.scene.eye_right)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}


@register_wrap
class Av3EyeTrackingPanel(ToolPanel, bpy.types.Panel):
    """Avatars 3.0 version of the Eye Tracking Panel
    Contains an operator to reorient eye bones so that they're pointing directly up and have zero roll."""
    bl_idname = 'VIEW3D_PT_av3_eyetracking'
    bl_label = t('EyeTrackingPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        sub = col.column(align=True)
        sub.scale_y = 0.75
        sub.label(text=t("Av3EyeTrackingPanel.info1"), icon='INFO')
        sub.label(text=t("Av3EyeTrackingPanel.info2"), icon='BLANK1')

        row = col.row(align=True)
        row.scale_y = 1.1
        row.label(text=t('Scene.eye_left.label') + ":")
        row.operator(SearchMenuOperatorBoneEyeLeft.bl_idname,
                     text=layout.enum_item_name(scene, "eye_left", scene.eye_left), icon='BONE_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.label(text=t('Scene.eye_right.label') + ":")
        row.operator(SearchMenuOperatorBoneEyeRight.bl_idname,
                     text=layout.enum_item_name(scene, "eye_right", scene.eye_right), icon='BONE_DATA')

        col = box.column(align=True)
        row = col.row(align=True)
        row.operator(Eyetracking.RotateEyeBonesForAv3Button.bl_idname, icon='CON_ROTLIMIT')