# MIT License

import bpy

from .main import ToolPanel
from ..tools import common as Common
from ..tools import viseme as Viseme

from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class SearchMenuOperatorMouthA(bpy.types.Operator):
    bl_description = t('Scene.mouth_a.desc')
    bl_idname = "scene.search_menu_mouth_a"
    bl_label = ""
    bl_property = "my_enum"
    
    my_enum: bpy.props.EnumProperty(
        name="shapekeys",
        description=t('Scene.mouth_a.desc'),
        items=Common.wrap_dynamic_enum_items(Common.get_shapekeys_mouth_ah, bl_idname, sort=False, is_holder=False),
    )

    def execute(self, context):
        context.scene.mouth_a = self.my_enum
        print(context.scene.mouth_a)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorMouthO(bpy.types.Operator):
    bl_description = t('Scene.mouth_o.desc')
    bl_idname = "scene.search_menu_mouth_o"
    bl_label = ""
    bl_property = "my_enum"
    
    my_enum: bpy.props.EnumProperty(
        name="shapekeys",
        description=t('Scene.mouth_o.desc'),
        items=Common.wrap_dynamic_enum_items(Common.get_shapekeys_mouth_oh, bl_idname, sort=False, is_holder=False),
    )

    def execute(self, context):
        context.scene.mouth_o = self.my_enum
        print(context.scene.mouth_o)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorMouthCH(bpy.types.Operator):
    bl_description = t('Scene.mouth_ch.desc')
    bl_idname = "scene.search_menu_mouth_ch"
    bl_label = ""
    bl_property = "my_enum"
    
    my_enum: bpy.props.EnumProperty(
        name="shapekeys",
        description=t('Scene.mouth_ch.desc'),
        items=Common.wrap_dynamic_enum_items(Common.get_shapekeys_mouth_ch, bl_idname, sort=False, is_holder=False),
    )

    def execute(self, context):
        context.scene.mouth_ch = self.my_enum
        print(context.scene.mouth_ch)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class VisemePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_viseme_v3'
    bl_label = t('VisemePanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        # Mesh selection section
        mesh_count = len(Common.get_meshes_objects(check=False))
        if mesh_count == 0:
            mesh_box = box.box()
            mesh_col = mesh_box.column(align=True)
            mesh_col.separator(factor=1.5)
            row = mesh_col.row(align=True)
            row.scale_y = 1.1
            row.label(text=t('VisemePanel.error.noMesh'), icon='ERROR')
            mesh_col.separator(factor=1.5)
        elif mesh_count > 1:
            mesh_box = box.box()
            mesh_col = mesh_box.column(align=True)
            mesh_col.separator(factor=1.5)
            row = mesh_col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'mesh_name_viseme', icon='MESH_DATA')
            mesh_col.separator(factor=1.5)

        # Viseme settings section
        settings_box = box.box()
        settings_col = settings_box.column(align=True)

        # Mouth A
        row = settings_col.row(align=True)
        row.scale_y = 1.1
        row.label(text=t('Scene.mouth_a.label')+":")
        mouth_a_text = 'None' if Common.is_enum_empty(context.scene.mouth_a) else context.scene.mouth_a
        row.operator(SearchMenuOperatorMouthA.bl_idname, text=mouth_a_text, icon='SHAPEKEY_DATA')

        # Mouth O
        row = settings_col.row(align=True)
        row.scale_y = 1.1
        row.label(text=t('Scene.mouth_o.label')+":")
        mouth_o_text = 'None' if Common.is_enum_empty(context.scene.mouth_o) else context.scene.mouth_o
        row.operator(SearchMenuOperatorMouthO.bl_idname, text=mouth_o_text, icon='SHAPEKEY_DATA')

        # Mouth CH
        row = settings_col.row(align=True)
        row.scale_y = 1.1
        row.label(text=t('Scene.mouth_ch.label')+":")
        mouth_ch_text = 'None' if Common.is_enum_empty(context.scene.mouth_ch) else context.scene.mouth_ch
        row.operator(SearchMenuOperatorMouthCH.bl_idname, text=mouth_ch_text, icon='SHAPEKEY_DATA')

        settings_col.separator(factor=1.5)

        # Shape intensity
        row = settings_col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'shape_intensity')

        settings_col.separator(factor=1.5)

        # Auto viseme button
        row = settings_col.row(align=True)
        row.scale_y = 1.2
        row.operator(Viseme.AutoVisemeButton.bl_idname, icon='TRIA_RIGHT')

