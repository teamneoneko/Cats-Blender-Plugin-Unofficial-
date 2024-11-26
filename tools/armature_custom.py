# MIT License

import bpy
import copy
import webbrowser
from typing import Dict, List, Tuple, Optional
from mathutils import Vector, Euler

from . import common as Common
from . import armature_bones as Bones
from .register import register_wrap
from .translations import t

def validate_armature_hierarchies(base_armature: bpy.types.Object, merge_armature: bpy.types.Object) -> Tuple[bool, str]:
    """Validates bone hierarchies of both armatures before merging.
    Returns (is_valid, error_message)"""
    
    for armature in (base_armature, merge_armature):
        bone_hierarchy = {}
        for bone in armature.data.edit_bones:
            parent_chain = []
            current = bone
            while current.parent:
                if current in parent_chain:
                    return False, f"Circular parent relationship detected in {armature.name} for bone {bone.name}"
                parent_chain.append(current)
                current = current.parent
            bone_hierarchy[bone.name] = parent_chain
            
    return True, ""

def validate_armature_transforms(armature: bpy.types.Object, tolerance: float = 0.001) -> Tuple[bool, str]:
    """Checks for invalid transforms and scales on armature and bones."""
    
    for i in range(3):
        if abs(armature.scale[i] - 1.0) > tolerance:
            return False, f"Non-uniform scale detected on armature {armature.name}"
            
        if abs(armature.rotation_euler[i]) > tolerance:
            return False, f"Rotation detected on armature {armature.name}"
    
    bone_transforms: Dict[str, Tuple[Vector, float, Vector]] = {}
    for bone in armature.data.edit_bones:
        bone_transforms[bone.name] = (bone.head.copy(), bone.roll, bone.tail.copy())
        
    return True, ""

def create_bone_mapping(base_armature: bpy.types.Object, merge_armature: bpy.types.Object, 
                       position_threshold: float = 0.01) -> Dict[str, str]:
    """Creates intelligent mapping between bones based on position and name similarity."""
    
    bone_map = {}
    base_bones = {b.name: b for b in base_armature.data.edit_bones}
    merge_bones = {b.name: b for b in merge_armature.data.edit_bones}
    
    for merge_name, merge_bone in merge_bones.items():
        base_name = merge_name.replace('.merge', '')
        if base_name in base_bones:
            base_bone = base_bones[base_name]
            if (merge_bone.head - base_bone.head).length < position_threshold:
                bone_map[merge_name] = base_name
                continue
                
        for base_name, base_bone in base_bones.items():
            if (merge_bone.head - base_bone.head).length < position_threshold:
                bone_map[merge_name] = base_name
                break
                
    return bone_map

def batch_merge_vertex_groups(mesh: bpy.types.Object, bone_map: Dict[str, str]):
    """Efficiently merges vertex groups based on bone mapping"""
    
    vg_indices = {vg.name: vg.index for vg in mesh.vertex_groups}
    vert_weights: Dict[int, List[Tuple[int, float]]] = {}
    
    for vert in mesh.data.vertices:
        weights = []
        for g in vert.groups:
            weights.append((g.group, g.weight))
        vert_weights[vert.index] = weights
            
    for merge_name, base_name in bone_map.items():
        if merge_name in vg_indices and base_name in vg_indices:
            Common.mix_weights(mesh, merge_name, base_name)

def process_bone_rolls(armature: bpy.types.Object, bone_map: Dict[str, str]):
    """Handles bone roll angles during merge"""
    for merge_name, base_name in bone_map.items():
        merge_bone = armature.data.edit_bones.get(merge_name)
        base_bone = armature.data.edit_bones.get(base_name)
        if merge_bone and base_bone:
            merge_bone.roll = base_bone.roll

@register_wrap
class MergeArmature(bpy.types.Operator):
    bl_idname = 'cats_custom.merge_armatures'
    bl_label = t('MergeArmature.label')
    bl_description = t('MergeArmature.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(Common.get_armature_objects()) > 1

    def execute(self, context):
        wm = context.window_manager
        wm.progress_begin(0, 100)

        saved_data = Common.SavedData()

        # Set default stage
        Common.set_default_stage()
        Common.remove_rigidbodies_global()
        Common.unselect_all()
        wm.progress_update(10)

        # Get both armatures
        base_armature_name = context.scene.merge_armature_into
        merge_armature_name = context.scene.merge_armature
        base_armature = Common.get_objects()[base_armature_name]
        merge_armature = Common.get_objects()[merge_armature_name]

        # Validate armatures
        is_valid, error_msg = validate_armature_hierarchies(base_armature, merge_armature)
        if not is_valid:
            self.report({'ERROR'}, error_msg)
            saved_data.load()
            wm.progress_end()
            return {'CANCELLED'}

        is_valid, error_msg = validate_armature_transforms(base_armature)
        if not is_valid:
            self.report({'ERROR'}, error_msg)
            saved_data.load() 
            wm.progress_end()
            return {'CANCELLED'}

        is_valid, error_msg = validate_armature_transforms(merge_armature)
        if not is_valid:
            self.report({'ERROR'}, error_msg)
            saved_data.load()
            wm.progress_end()
            return {'CANCELLED'}

        armature = Common.set_default_stage()
        wm.progress_update(20)

        # Remove Rigid Bodies and Joints
        to_delete = []
        for child in Common.get_top_parent(base_armature).children:
            if 'rigidbodies' in child.name or 'joints' in child.name:
                to_delete.append(child.name)
            for child2 in child.children:
                if 'rigidbodies' in child2.name or 'joints' in child2.name:
                    to_delete.append(child2.name)
        for obj_name in to_delete:
            Common.switch('EDIT')
            Common.switch('OBJECT')
            Common.delete_hierarchy(bpy.data.objects[obj_name])
        wm.progress_update(30)

        if len(armature.children) > 1:
            for child in armature.children:
                for child2 in child.children:
                    if child2.type != 'MESH':
                        Common.delete(child2)

                if child.type != 'MESH':
                    Common.delete(child)

        Common.set_default_stage()
        Common.unselect_all()
        Common.remove_empty()
        Common.remove_unused_objects()
        wm.progress_update(40)

        if not merge_armature:
            saved_data.load()
            wm.progress_end()
            Common.show_error(5.2, [t('MergeArmature.error.notFound', name=merge_armature_name)])
            return {'CANCELLED'}
        if not base_armature:
            saved_data.load()
            wm.progress_end()
            Common.show_error(5.2, [t('MergeArmature.error.notFound', name=base_armature_name)])
            return {'CANCELLED'}

        merge_parent = merge_armature.parent
        base_parent = base_armature.parent
        if merge_parent or base_parent:
            if context.scene.merge_same_bones:
                if merge_parent:
                    for i in [0, 1, 2]:
                        if merge_parent.scale[i] != 1 or merge_parent.location[i] != 0 or merge_parent.rotation_euler[i] != 0:
                            if not Common.show_warning(6.5, t('MergeArmature.warning.nonStandardArmature')):
                                saved_data.load()
                                wm.progress_end()
                                return {'CANCELLED'}
                    Common.delete(merge_armature.parent)

                if base_parent:
                    for i in [0, 1, 2]:
                        if base_parent.scale[i] != 1 or base_parent.location[i] != 0 or base_parent.rotation_euler[i] != 0:
                            if not Common.show_warning(6.5, t('MergeArmature.warning.nonStandardArmature')):
                                saved_data.load()
                                wm.progress_end()
                                return {'CANCELLED'}
                    Common.delete(base_armature.parent)
            else:
                if not Common.show_warning(6.2, t('MergeArmature.warning.nonStandardArmature')):
                    saved_data.load()
                    wm.progress_end()
                    return {'CANCELLED'}
        wm.progress_update(50)

        merge_armatures(base_armature_name, merge_armature_name, False, merge_same_bones=context.scene.merge_same_bones)
        wm.progress_update(90)

        saved_data.load()
        wm.progress_update(100)

        wm.progress_end()

        self.report({'INFO'}, t('MergeArmature.success'))
        return {'FINISHED'}

def merge_armatures(base_armature_name: str, merge_armature_name: str, mesh_only: bool, mesh_name: Optional[str] = None, merge_same_bones: bool = False) -> None:
    """Main function to merge two armatures with improved bone handling and validation.
    
    Args:
        base_armature_name: Name of the target armature
        merge_armature_name: Name of the armature to merge in
        mesh_only: Whether to only merge meshes
        mesh_name: Optional name for the merged mesh
        merge_same_bones: Whether to merge bones with matching names
    """
    tolerance = 0.00008726647  # around 0.005 degrees
    base_armature = Common.get_objects()[base_armature_name]
    merge_armature = Common.get_objects()[merge_armature_name]

    # Cache bone data for both armatures
    base_bones = {b.name: b for b in base_armature.data.edit_bones}
    merge_bones = {b.name: b for b in merge_armature.data.edit_bones}

    # Fix zero length bones
    Common.fix_zero_length_bones(base_armature)
    Common.fix_zero_length_bones(merge_armature)

    # Get and process meshes
    if bpy.context.scene.merge_armatures_join_meshes:
        meshes_base = [Common.join_meshes(armature_name=base_armature_name, apply_transformations=False)]
        meshes_merge = [Common.join_meshes(armature_name=merge_armature_name, apply_transformations=False)]
    else:
        meshes_base = Common.get_meshes_objects(armature_name=base_armature_name)
        meshes_merge = Common.get_meshes_objects(armature_name=merge_armature_name)

    # Validate mesh lists
    meshes_base = [] if len(meshes_base) == 1 and not meshes_base[0] else meshes_base
    meshes_merge = [] if len(meshes_merge) == 1 and not meshes_merge[0] else meshes_merge

    # Join meshes if needed
    if bpy.context.scene.merge_armatures_join_meshes:
        meshes_merged = [Common.join_meshes(armature_name=base_armature_name, apply_transformations=False)]
    else:
        meshes_merged = meshes_base + meshes_merge
        for mesh in meshes_merged:
            mesh.parent = base_armature
            Common.repair_mesh(mesh, base_armature_name)

    # Validate merged mesh list
    if len(meshes_merged) == 1 and not meshes_merged[0]:
        meshes_merged = []

    # Apply transforms intelligently
    handle_armature_transforms(base_armature, merge_armature, meshes_merge, mesh_only, tolerance)

    # Create bone mapping and process bones
    bone_map = create_bone_mapping(base_armature, merge_armature)
    process_bones(base_armature, merge_armature, bone_map, mesh_only, merge_same_bones)

    # Process vertex groups and weights
    process_vertex_groups(meshes_merged, bone_map, base_armature_name)

    # Cleanup and finalization
    finalize_merge(base_armature, mesh_name, mesh_only)

def handle_armature_transforms(base_armature: bpy.types.Object, merge_armature: bpy.types.Object, 
                             meshes_merge: List[bpy.types.Object], mesh_only: bool, tolerance: float) -> None:
    """Handles armature transformations during merge process."""
    
    Common.apply_transforms(armature_name=base_armature.name)

    if len(meshes_merge) != 1 or not bpy.context.scene.merge_armatures_join_meshes or \
       bpy.context.scene.apply_transforms or mesh_only:
        Common.apply_transforms(armature_name=merge_armature.name)
    else:
        handle_single_mesh_transforms(merge_armature, meshes_merge[0], tolerance)

def handle_single_mesh_transforms(armature: bpy.types.Object, mesh: bpy.types.Object, tolerance: float) -> None:
    """Handles transforms for a single mesh case."""
    
    for i in [0, 1, 2]:
        if abs(armature.rotation_euler[i]) > tolerance or abs(mesh.rotation_euler[i]) > tolerance:
            if any(armature.location[i] != 0 or abs(armature.rotation_euler[i]) > tolerance or 
                  armature.scale[i] != 1 for i in range(3)):
                reset_armature_transforms(armature)
                Common.show_error(7.5, t('merge_armatures.error.transformReset'))
                return

    transfer_mesh_transforms_to_armature(armature, mesh)

def process_bones(base_armature: bpy.types.Object, merge_armature: bpy.types.Object, 
                 bone_map: Dict[str, str], mesh_only: bool, merge_same_bones: bool) -> None:
    """Processes and merges bones between armatures."""
    
    # Store bone data before joining
    merge_bone_data = {}
    for bone in merge_armature.data.edit_bones:
        merge_bone_data[bone.name] = {
            'head': bone.head.copy(),
            'tail': bone.tail.copy(),
            'roll': bone.roll
        }

    Common.unselect_all()
    Common.set_active(base_armature)
    Common.select(merge_armature)

    # Join the armatures
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()

    if not mesh_only:
        handle_bone_merging(base_armature, merge_bone_data, bone_map, merge_same_bones)
    else:
        rename_mesh_only_bones(base_armature)

def process_vertex_groups(meshes: List[bpy.types.Object], bone_map: Dict[str, str], 
                         armature_name: str) -> None:
    """Processes vertex groups for merged meshes."""
    
    for mesh in meshes:
        batch_merge_vertex_groups(mesh, bone_map)
        Common.repair_mesh(mesh, armature_name)

def finalize_merge(armature: bpy.types.Object, mesh_name: Optional[str], mesh_only: bool) -> None:
    """Finalizes the merge process with cleanup operations."""
    
    Common.fix_armature_names(armature.name)
    if not mesh_only:
        cleanup_unused_data(armature)
    Common.correct_bone_positions(armature_name=armature.name)

def handle_bone_merging(base_armature: bpy.types.Object, merge_bone_data: Dict[str, Dict], 
                       bone_map: Dict[str, str], merge_same_bones: bool) -> None:
    """Handles the merging of bones between armatures."""
    bones_to_merge = copy.deepcopy(Bones.dont_delete_these_main_bones)
    
    if merge_same_bones:
        merge_matching_bones(base_armature, merge_bone_data, bone_map)
    else:
        merge_custom_bones(base_armature, merge_bone_data, bone_map, bones_to_merge)

def merge_matching_bones(base_armature: bpy.types.Object, merge_bone_data: Dict[str, Dict], 
                        bone_map: Dict[str, str]) -> None:
    """Merges bones that match between armatures."""
    for bone_name, bone_data in merge_bone_data.items():
        base_name = bone_name.replace('.merge', '')
        if base_name in base_armature.data.edit_bones:
            merged_bone = base_armature.data.edit_bones.get(bone_name)
            if merged_bone:
                merged_bone.parent = base_armature.data.edit_bones[base_name]

def merge_custom_bones(base_armature: bpy.types.Object, merge_armature: bpy.types.Object, 
                      bone_map: Dict[str, str], bones_to_merge: List[str]) -> None:
    """Handles custom bone merging with position matching."""
    for bone_name in bones_to_merge:
        old_name = f"{bone_name}.merge"
        if old_name in merge_armature.data.edit_bones and bone_name in base_armature.data.edit_bones:
            merge_armature.data.edit_bones[old_name].parent = base_armature.data.edit_bones[bone_name]

    # Position-based matching for remaining bones
    for bone in merge_armature.data.edit_bones:
        if bone.name in bone_map:
            bone.parent = base_armature.data.edit_bones[bone_map[bone.name]]

def cleanup_unused_data(armature: bpy.types.Object) -> None:
    """Cleans up unused data after merging."""
    if bpy.context.scene.merge_armatures_remove_zero_weight_bones:
        Common.remove_unused_vertex_groups()
        if Common.get_meshes_objects(armature_name=armature.name):
            Common.delete_zero_weight(armature_name=armature.name)
    
    Common.delete_bone_constraints(armature_name=armature.name)

def reset_armature_transforms(armature: bpy.types.Object) -> None:
    """Resets armature transforms to default values."""
    for i in range(3):
        armature.location[i] = 0
        armature.rotation_euler[i] = 0
        armature.scale[i] = 1

def transfer_mesh_transforms_to_armature(armature: bpy.types.Object, mesh: bpy.types.Object) -> None:
    """Transfers mesh transforms to its armature."""
    old_loc = armature.location.copy()
    old_scale = armature.scale.copy()

    for i in range(3):
        armature.location[i] = (mesh.location[i] * old_scale[i]) + old_loc[i]
        armature.rotation_euler[i] = mesh.rotation_euler[i]
        armature.scale[i] = mesh.scale[i] * old_scale[i]
        
        mesh.location[i] = 0
        mesh.rotation_euler[i] = 0
        mesh.scale[i] = 1

    Common.apply_transforms(armature_name=armature.name)

@register_wrap
class AttachMesh(bpy.types.Operator):
    bl_idname = 'cats_custom.attach_mesh'
    bl_label = t('AttachMesh.label')
    bl_description = t('AttachMesh.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(Common.get_armature_objects()) > 0 and len(Common.get_meshes_objects(mode=1, check=False)) > 0

    def execute(self, context):
        wm = context.window_manager
        wm.progress_begin(0, 100)

        saved_data = Common.SavedData()

        # Set default stage
        Common.set_default_stage()
        Common.remove_rigidbodies_global()
        Common.unselect_all()
        wm.progress_update(10)

        # Get armature and mesh
        mesh_name = bpy.context.scene.attach_mesh
        base_armature_name = bpy.context.scene.merge_armature_into
        attach_bone_name = bpy.context.scene.attach_to_bone
        mesh = Common.get_objects()[mesh_name]
        armature = Common.get_objects()[base_armature_name]
        wm.progress_update(20)

        # Reparent mesh to target armature
        mesh.parent = armature
        mesh.parent_type = 'OBJECT'
        wm.progress_update(30)

        # Applies transforms of the armature and new mesh
        Common.apply_transforms(armature_name=base_armature_name)
        wm.progress_update(40)

        # Switch mesh to edit mode
        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        wm.progress_update(50)

        # Delete all previous vertex groups
        if mesh.vertex_groups:
            bpy.ops.object.vertex_group_remove(all=True)

        # Select and assign all vertices to new vertex group
        bpy.ops.mesh.select_all(action='SELECT')
        vg = mesh.vertex_groups.new(name=mesh_name)
        bpy.ops.object.vertex_group_assign()
        wm.progress_update(60)

        Common.switch('OBJECT')

        # Verify that the vertex group has vertices assigned
        verts_in_group = []
        for v in mesh.data.vertices:
            for group in v.groups:
                if group.group == vg.index:
                    verts_in_group.append(v)
                    break

        if not verts_in_group:
            self.report({'ERROR'}, f"Vertex group '{mesh_name}' is empty or does not exist.")
            saved_data.load()
            wm.progress_end()
            return {'CANCELLED'}

        # Switch armature to edit mode
        Common.unselect_all()
        Common.set_active(armature)
        Common.switch('EDIT')
        wm.progress_update(70)

        # Create bone in target armature and reparent it to the target bone
        attach_to_bone = armature.data.edit_bones.get(attach_bone_name)
        if not attach_to_bone:
            self.report({'ERROR'}, f"Attach bone '{attach_bone_name}' not found in armature.")
            saved_data.load()
            wm.progress_end()
            return {'CANCELLED'}
        mesh_bone = armature.data.edit_bones.new(mesh_name)
        mesh_bone.parent = attach_to_bone

        # Compute the center vector
        center_vector = Common.find_center_vector_of_vertex_group(mesh, mesh_name)
        if center_vector is None:
            self.report({'ERROR'}, f"Unable to find center of vertex group '{mesh_name}'.")
            saved_data.load()
            wm.progress_end()
            return {'CANCELLED'}

        # Set bone head and tail positions
        mesh_bone.head = center_vector
        mesh_bone.tail = center_vector.copy()
        mesh_bone.tail[2] += 0.1
        wm.progress_update(80)

        # Switch armature back to object mode
        Common.switch('OBJECT')

        # Remove previous armature modifiers
        for mod in mesh.modifiers:
            if mod.type == 'ARMATURE':
                mesh.modifiers.remove(mod)

        # Create new armature modifier
        mod = mesh.modifiers.new('Armature', 'ARMATURE')
        mod.object = armature
        wm.progress_update(90)

        # Restore the attach bone field
        bpy.context.scene.attach_to_bone = attach_bone_name

        saved_data.load()
        wm.progress_update(100)
        wm.progress_end()

        self.report({'INFO'}, t('AttachMesh.success'))
        return {'FINISHED'}

@register_wrap
class CustomModelTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_custom.tutorial'
    bl_label = t('CustomModelTutorialButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('CustomModelTutorialButton.URL'))
        self.report({'INFO'}, t('CustomModelTutorialButton.success'))
        return {'FINISHED'}
