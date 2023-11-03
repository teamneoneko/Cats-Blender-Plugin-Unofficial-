# -*- coding: utf-8 -*-

import logging

import bpy
from mmd_tools.properties.bone import MMDBone, _mmd_ik_toggle_update
from mmd_tools.properties.camera import MMDCamera
from mmd_tools.properties.material import MMDMaterial
from mmd_tools.properties.rigid_body import MMDJoint, MMDRigidBody
from mmd_tools.properties.root import MMDRoot

__properties = {
    bpy.types.Object: {
        'mmd_type': bpy.props.EnumProperty(
            name='Type',
            description='Internal MMD type of this object (DO NOT CHANGE IT DIRECTLY)',
            default='NONE',
            items=[
                ('NONE', 'None', '', 1),
                ('ROOT', 'Root', '', 2),
                ('RIGID_GRP_OBJ', 'Rigid Body Grp Empty', '', 3),
                ('JOINT_GRP_OBJ', 'Joint Grp Empty', '', 4),
                ('TEMPORARY_GRP_OBJ', 'Temporary Grp Empty', '', 5),
                ('PLACEHOLDER', 'Place Holder', '', 6),

                ('CAMERA', 'Camera', '', 21),
                ('JOINT', 'Joint', '', 22),
                ('RIGID_BODY', 'Rigid body', '', 23),
                ('LIGHT', 'Light', '', 24),

                ('TRACK_TARGET', 'Track Target', '', 51),
                ('NON_COLLISION_CONSTRAINT', 'Non Collision Constraint', '', 52),
                ('SPRING_CONSTRAINT', 'Spring Constraint', '', 53),
                ('SPRING_GOAL', 'Spring Goal', '', 54),
            ]
        ),
        'mmd_root': bpy.props.PointerProperty(type=MMDRoot),
        'mmd_camera': bpy.props.PointerProperty(type=MMDCamera),
        'mmd_rigid': bpy.props.PointerProperty(type=MMDRigidBody),
        'mmd_joint': bpy.props.PointerProperty(type=MMDJoint),
    },
    bpy.types.Material: {
        'mmd_material': bpy.props.PointerProperty(type=MMDMaterial),
    },
    bpy.types.PoseBone: {
        'mmd_bone': bpy.props.PointerProperty(type=MMDBone),
        'is_mmd_shadow_bone': bpy.props.BoolProperty(name='is_mmd_shadow_bone', default=False),
        'mmd_shadow_bone_type': bpy.props.StringProperty(name='mmd_shadow_bone_type'),
        # TODO: Replace to driver for NLA
        'mmd_ik_toggle': bpy.props.BoolProperty(
            name='MMD IK Toggle',
            description='MMD IK toggle is used to import/export animation of IK on-off',
            update=_mmd_ik_toggle_update,
            default=True,
        ),
    }
}


def __set_hide(prop, value):
    prop.hide_set(value)
    if getattr(prop, 'hide_viewport'):
        setattr(prop, 'hide_viewport', False)


def __patch(properties):  # temporary patching, should be removed in the future
    def __patch_override(prop: bpy.props._PropertyDeferred):
        """Apply recursively for each mmd_tools property class annotations

        # Hint for bpy.props._PropertyDeferred class
        p = bpy.props.IntProperty(name='abc123')
        assert isinstance(p, bpy.props._PropertyDeferred)
        assert p.function == bpy.props.IntProperty
        assert p.keywords == {'name': 'abc123'}
        """
        prop.keywords.setdefault('override', set()).add('LIBRARY_OVERRIDABLE')

        if prop.function.__name__ not in {'PointerProperty', 'CollectionProperty'}:
            return

        prop_type = prop.keywords['type']
        # The __annotations__ cannot be inherited. Manually search for base classes.
        for inherited_type in [prop_type, *prop_type.__bases__]:
            if not inherited_type.__module__.startswith('mmd_tools.properties'):
                continue
            for annotation in inherited_type.__annotations__.values():
                if not isinstance(annotation, bpy.props._PropertyDeferred):
                    continue
                __patch_override(annotation)

    for props in properties.values():
        for prop in props.values():
            __patch_override(prop)

    prop_obj = properties.setdefault(bpy.types.Object, {})

    prop_obj['select'] = bpy.props.BoolProperty(
        get=lambda prop: prop.select_get(),
        set=lambda prop, value: prop.select_set(value),
        options={'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', },
    )
    prop_obj['hide'] = bpy.props.BoolProperty(
        get=lambda prop: prop.hide_get(),
        set=__set_hide,
        options={'SKIP_SAVE', 'ANIMATABLE', 'LIBRARY_EDITABLE', },
    )


if bpy.app.version >= (2, 80, 0):
    __patch(__properties)


def register():
    for typ, t in __properties.items():
        for attr, prop in t.items():
            if hasattr(typ, attr):
                logging.warning(' * warning: overwrite\t%s\t%s', typ, attr)
            try:
                setattr(typ, attr, prop)
            except:  # pylint: disable=bare-except
                logging.warning(' * warning: register\t%s\t%s', typ, attr)


def unregister():
    for typ, t in __properties.items():
        for attr in t.keys():
            if hasattr(typ, attr):
                delattr(typ, attr)
