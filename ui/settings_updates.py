# MIT License

import bpy

from .. import globs
from .. import updater
from .main import ToolPanel, layout_split
from ..tools import settings as Settings
from ..tools.register import register_wrap
from ..tools.translations import t, DownloadTranslations

@register_wrap
class UpdaterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_updater_v3'
    bl_label = t('UpdaterPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.scale_y = 0.8
        row.label(text=t('UpdaterPanel.name'), icon=globs.ICON_SETTINGS)
        col.separator()

        row = col.row(align=True)
        row.prop(context.scene, 'embed_textures')
        row = col.row(align=True)
        row.prop(context.scene, 'remove_rigidbodies_joints_global')
        row = col.row(align=True)
        row.prop(context.scene, "export_translate_csv")
        row = col.row(align=True)
        path = context.scene.custom_translate_csv_export_dir
        if path:
            custom_translate_csv_export_dir = path
        else:
            custom_translate_csv_export_dir = default_cats_dir
        row.prop(context.scene, "custom_translate_csv_export_dir")

        col.separator()

        row = col.row(align=True)
        row = layout_split(row, factor=0.56)
        row.label(text=t('Scene.ui_lang.label') + ':')
        row.prop(context.scene, 'ui_lang', text='')

        # Only show this in the dev branch
        if globs.dev_branch:
            col.separator()
            row = col.row(align=True)
            row.operator(DownloadTranslations.bl_idname)

        col.separator()

        row = col.row(align=True)
        row.scale_y = 0.8
        row.operator(Settings.ResetGoogleDictButton.bl_idname, icon='X')
        if globs.dev_branch:
            row = col.row(align=True)
            row.scale_y = 0.8
            row.operator(Settings.DebugTranslations.bl_idname, icon='X')

        if Settings.settings_changed():
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text=t('UpdaterPanel.requireRestart1'), icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text=t('UpdaterPanel.requireRestart2'), icon='BLANK1')
            row = col.row(align=True)
            row.operator(Settings.RevertChangesButton.bl_idname, icon='RECOVER_LAST')

        col.separator()
        updater.draw_updater_panel(context, box)
