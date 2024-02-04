# MIT License

import bpy
import webbrowser

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import iconloader as Iconloader
from ..tools.register import register_wrap
from ..tools.translations import t
from ..ui.legacy import LegacyDecimationButton 

@register_wrap
class DecimationPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_decimation_v3'
    bl_label = t('DecimationPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        scene = context.scene
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        sub = col.column(align=True)
        sub.label(text=t("DecimationMoved1.info1"), icon='INFO')
        sub.label(text=t("DecimationMoved1.info2"), icon='BLANK1')
        sub.label(text=t("DecimationMoved1.info3"), icon='BLANK1')
        sub.label(text=t("DecimationMoved1.info4"), icon='BLANK1')
              
        col.separator()       
        row = col.row(align=True)
        row.scale_y = 1.5

        row.operator(LegacyDecimationButton.bl_idname, icon_value=Iconloader.preview_collections['custom_icons']['help1'].icon_id)

        col.separator()
        col.separator()
