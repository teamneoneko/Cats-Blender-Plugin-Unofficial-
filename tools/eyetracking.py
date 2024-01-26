# GPL License

import bpy
import copy
import math
import bmesh
import mathutils

from collections import OrderedDict
from random import random
from itertools import chain

from . import common as Common
from . import armature as Armature
from .register import register_wrap
from .translations import t


@register_wrap
class RotateEyeBonesForAv3Button(bpy.types.Operator):
    """Reorient eye bones to point straight up and have zero roll. This isn't necessary for VRChat because eye-tracking
    rotations can be set separately per eye in Unity, however it does simplify setting up the eye-tracking rotations,
    because both eyes can use the same rotations, and it makes it so that (0,0,0) rotation results in the eyes looking
    forward."""
    bl_idname = "cats_eyes.av3_orient_eye_bones"
    bl_label = t("Av3EyeTrackingRotateEyeBones.label")
    bl_description = t("Av3EyeTrackingRotateEyeBones.desc")
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        # The eye_left and eye_right properties already check that there is an armature, so we don't need to check that
        # here.
        scene = context.scene
        if not (Common.is_enum_non_empty(scene.eye_left) or Common.is_enum_non_empty(scene.eye_right)):
            cls.poll_message_set(t("Av3EyeTrackingRotateEyeBones.poll.noBones"))
            return False

        # If another Object is currently in EDIT mode and the armature is not also in the same EDIT mode, we cannot swap
        # the armature into EDIT mode and then swap back to the original Object in its original EDIT mode because
        # Undo/Redo will not work for the changes made by this Operator.
        armature = Common.get_armature()
        if context.object.mode == 'EDIT' and armature not in context.objects_in_mode:
            cls.poll_message_set(t("Av3EyeTrackingRotateEyeBones.poll.notInCurrentEditMode", armature=armature.name))
            return False

        return True

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene

        armature_obj = Common.get_armature()
        armature = armature_obj.data

        already_editing = armature_obj.mode == 'EDIT'

        # If we're in EDIT mode already, we need to access the matrices of the edit bones because the bones may not be
        # up-to-date.
        if already_editing:
            bones = armature.edit_bones
            matrix_attribute = "matrix"
        else:
            bones = armature.bones
            matrix_attribute = "matrix_local"

        # Both bones could be set the same, so use a set to ensure we only have unique names
        eye_bone_names = {scene.eye_left, scene.eye_right}

        # The position of the head and tail are easy to compare from OBJECT mode through head_local and tail_local, but
        # bone roll is not easily accessible.
        # We can determine bone roll (and the overall orientation of the bone) through matrix_local.
        # The expected matrix_local for a bone pointing straight up and with zero roll is a 90 degrees rotation about
        # the X-axis and no other rotation.
        straight_up_and_zero_roll = mathutils.Matrix.Rotation(math.pi/2, 3, 'X')

        # Check each bone
        for eye_bone_name in list(eye_bone_names):
            bone = bones[eye_bone_name]

            # Due to floating-point precision, it's unlikely that the bone's matrix_local will exactly match, so
            # we'll check if it's close enough.
            matrix_close_enough = True

            # Create iterators to iterate through each value of the matrices in order
            matrix_iter = chain.from_iterable(getattr(bone, matrix_attribute).to_3x3())
            expected_matrix_iter = chain.from_iterable(straight_up_and_zero_roll)
            for bone_val, expected_val in zip(matrix_iter, expected_matrix_iter):
                # Note that while the values may be accessed as standard python float which is up to double-precision,
                # mathutils.Matrix/Vector only store single-precision float, so the tolerances need to be more lenient
                # than they might usually be.
                if not math.isclose(bone_val, expected_val, rel_tol=1e-6, abs_tol=1e-6):
                    matrix_close_enough = False
                    break
            if matrix_close_enough:
                eye_bone_names.remove(eye_bone_name)

        if not eye_bone_names:
            # Both bones are already oriented correctly
            self.report({'INFO'}, t("Av3EyeTrackingRotateEyeBones.info.noChanges"))
            return {'CANCELLED'}

        if not already_editing:
            # Store active/selected/hidden object states, so they can be restored afterwards.
            saved_data = Common.SavedData()

            # set_default_stage will set the armature as active
            armature_obj2 = Common.set_default_stage()
            assert armature_obj == armature_obj2

            # Bones can only be moved while in EDIT mode.
            Common.switch('EDIT')

        edit_bones = armature.edit_bones

        # Get each eye's EditBone
        eye_bones = {edit_bones[eye_bone_name] for eye_bone_name in eye_bone_names}

        # Setting a bone's matrix doesn't currently update mirrored bones like when setting a bone's head/tail, but
        # we'll temporarily disable mirroring in-case this changes in the future.
        orig_mirroring = armature.use_mirror_x
        armature.use_mirror_x = False

        # We're going to result in moving the tails of the eye bones, but we don't want this to affect any other bones,
        # so disconnect any bones that are connected to the eye bones.
        for bone in edit_bones:
            if bone.use_connect and bone.parent in eye_bones:
                bone.use_connect = False

        for eye_bone in eye_bones:
            # Re-orient the bone to point straight up with zero roll, maintaining the original length and the position
            # of the bone's head.
            new_matrix = straight_up_and_zero_roll.to_4x4()
            new_matrix.translation = eye_bone.matrix.translation
            eye_bone.matrix = new_matrix

        # Restore the mirror setting.
        armature.use_mirror_x = orig_mirroring

        if not already_editing:
            Common.switch('OBJECT')
            # Restore active/selected/hidden object states
            saved_data.load()

        self.report({'INFO'}, t("Av3EyeTrackingRotateEyeBones.success"))
        return {'FINISHED'}
