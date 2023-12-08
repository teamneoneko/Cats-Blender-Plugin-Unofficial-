# -*- coding: utf-8 -*-
# Copyright 2018 MMD Tools authors
# This file is part of MMD Tools.

# SUPPORT_UNTIL: 3.3 LTS

class MMDViewHeader:
    bl_idname = "mmd_tools_local_local_HT_view_header"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "ARMATURE" and context.active_object.mode == "POSE"

    def draw(self, context):
        if self.poll(context):
            self.layout.operator("mmd_tools_local_local.flip_pose", text="", icon="ARROW_LEFTRIGHT")
