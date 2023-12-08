# -*- coding: utf-8 -*-
# Copyright 2012 MMD Tools authors
# This file is part of MMD Tools.

# MMD Tools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# MMD Tools is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "mmd_tools_local",
    "author": "sugiany",
    "version": (4, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MMD Panel",
    "description": "Utility tools for MMD model editing. (UuuNyaa's forked version)",
    "warning": "",
    "doc_url": "https://mmd-blender.fandom.com/wiki/mmd_tools",
    "wiki_url": "https://mmd-blender.fandom.com/wiki/mmd_tools",
    "tracker_url": "https://github.com/UuuNyaa/blender_mmd_tools/issues",
    "support": "COMMUNITY",
    "category": "Object",
}

mmd_tools_local_VERSION = ".".join(map(str, bl_info["version"]))

# pylint: disable=wrong-import-position
import bpy

from mmd_tools_local import auto_load

auto_load.init()


import mmd_tools_local.operators
import mmd_tools_local.operators.addon_updater
import mmd_tools_local.operators.fileio
import mmd_tools_local.operators.model
import mmd_tools_local.properties


def menu_func_import(self, _context):
    self.layout.operator(mmd_tools_local.operators.fileio.ImportPmx.bl_idname, text="MikuMikuDance Model (.pmd, .pmx)", icon="OUTLINER_OB_ARMATURE")
    self.layout.operator(mmd_tools_local.operators.fileio.ImportVmd.bl_idname, text="MikuMikuDance Motion (.vmd)", icon="ANIM")
    self.layout.operator(mmd_tools_local.operators.fileio.ImportVpd.bl_idname, text="Vocaloid Pose Data (.vpd)", icon="POSE_HLT")


def menu_func_export(self, _context):
    self.layout.operator(mmd_tools_local.operators.fileio.ExportPmx.bl_idname, text="MikuMikuDance Model (.pmx)", icon="OUTLINER_OB_ARMATURE")
    self.layout.operator(mmd_tools_local.operators.fileio.ExportVmd.bl_idname, text="MikuMikuDance Motion (.vmd)", icon="ANIM")
    self.layout.operator(mmd_tools_local.operators.fileio.ExportVpd.bl_idname, text="Vocaloid Pose Data (.vpd)", icon="POSE_HLT")


def menu_func_armature(self, _context):
    self.layout.operator(mmd_tools_local.operators.model.CreateMMDModelRoot.bl_idname, text="Create MMD Model", icon="OUTLINER_OB_ARMATURE")


def menu_view3d_object(self, _context):
    self.layout.separator()
    self.layout.operator("mmd_tools_local.clean_shape_keys")


def menu_view3d_select_object(self, _context):
    self.layout.separator()
    self.layout.operator_context = "EXEC_DEFAULT"
    operator = self.layout.operator("mmd_tools_local.rigid_body_select", text="Select MMD Rigid Body")
    operator.properties = set(["collision_group_number", "shape"])


def menu_view3d_pose_context_menu(self, _context):
    self.layout.operator("mmd_tools_local.flip_pose", text="MMD Flip Pose", icon="ARROW_LEFTRIGHT")


def panel_view3d_shading(self, context):
    if context.space_data.shading.type != "SOLID":
        return

    col = self.layout.column(align=True)
    col.label(text="MMD Shading Presets")
    row = col.row(align=True)
    row.operator("mmd_tools_local.set_glsl_shading", text="GLSL")
    row.operator("mmd_tools_local.set_shadeless_glsl_shading", text="Shadeless")
    row = col.row(align=True)
    row.operator("mmd_tools_local.reset_shading", text="Reset")


@bpy.app.handlers.persistent
def load_handler(_dummy):
    # pylint: disable=import-outside-toplevel
    from mmd_tools_local.core.sdef import FnSDEF

    FnSDEF.clear_cache()
    FnSDEF.register_driver_function()

    from mmd_tools_local.core.material import MigrationFnMaterial

    MigrationFnMaterial.update_mmd_shader()

    from mmd_tools_local.core.morph import MigrationFnMorph

    MigrationFnMorph.update_mmd_morph()

    from mmd_tools_local.core.camera import MigrationFnCamera

    MigrationFnCamera.update_mmd_camera()

    from mmd_tools_local.core.model import MigrationFnModel

    MigrationFnModel.update_mmd_ik_loop_factor()
    MigrationFnModel.update_mmd_tools_local_version()


@bpy.app.handlers.persistent
def save_pre_handler(_dummy):
    # pylint: disable=import-outside-toplevel
    from mmd_tools_local.core.morph import MigrationFnMorph

    MigrationFnMorph.compatible_with_old_version_mmd_tools_local()


def register():
    mmd_tools_local.auto_load.register()
    mmd_tools_local.properties.register()
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.save_pre.append(save_pre_handler)
    bpy.types.VIEW3D_MT_object.append(menu_view3d_object)
    bpy.types.VIEW3D_MT_select_object.append(menu_view3d_select_object)
    bpy.types.VIEW3D_MT_pose.append(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_PT_shading.append(panel_view3d_shading)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.VIEW3D_MT_armature_add.append(menu_func_armature)

    # pylint: disable=import-outside-toplevel
    from mmd_tools_local.m17n import translation_dict

    bpy.app.translations.register(bl_info["name"], translation_dict)

    mmd_tools_local.operators.addon_updater.register_updater(bl_info, __file__)


def unregister():
    mmd_tools_local.operators.addon_updater.unregister_updater()

    bpy.app.translations.unregister(bl_info["name"])

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.VIEW3D_MT_armature_add.remove(menu_func_armature)
    bpy.types.VIEW3D_PT_shading.remove(panel_view3d_shading)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_MT_pose.remove(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_MT_select_object.remove(menu_view3d_select_object)
    bpy.types.VIEW3D_MT_object.remove(menu_view3d_object)
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.save_pre.remove(save_pre_handler)
    mmd_tools_local.properties.unregister()
    mmd_tools_local.auto_load.unregister()


if __name__ == "__main__":
    register()
