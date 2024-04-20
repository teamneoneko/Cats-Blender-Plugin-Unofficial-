# -*- coding: utf-8 -*-
# Copyright 2024 MMD Tools authors
# This file is part of MMD Tools.

from typing import List

from mmd_tools_local.properties.morph import BoneMorph, GroupMorph, MaterialMorph, UVMorph, VertexMorph
from mmd_tools_local.properties.translations import MMDTranslation

class MMDDisplayItemFrame:
    pass

class MMDRoot:
    name: str
    name_j: str
    name_e: str
    comment_text: str
    comment_e_text: str
    ik_lookup_factor: int
    show_meshes: bool
    show_rigid_bodies: bool
    show_joints: bool
    show_temporary_objects: bool
    show_armature: bool
    show_names_of_rigid_bodies: bool
    show_names_of_joints: bool
    use_toon_texture: bool
    use_sphere_texture: bool
    use_sdef: bool
    use_property_driver: bool
    is_built: bool
    active_rigidbody_index: int
    active_joint_index: int
    display_item_frames: List[MMDDisplayItemFrame]
    active_display_item_frame: int
    material_morphs: List[MaterialMorph]
    uv_morphs: List[UVMorph]
    bone_morphs: List[BoneMorph]
    vertex_morphs: List[VertexMorph]
    group_morphs: List[GroupMorph]

    active_morph_type: str  # TODO: Replace with StrEnum
    active_morph: int
    morph_panel_show_settings: bool
    active_mesh_index: int
    translation: MMDTranslation

    @staticmethod
    def register() -> None: ...
    @staticmethod
    def unregister() -> None: ...
