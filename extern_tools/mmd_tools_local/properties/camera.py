# -*- coding: utf-8 -*-

import math

import bpy


class MMDCamera(bpy.types.PropertyGroup):
    angle: bpy.props.FloatProperty(
        name='Angle',
        description='Camera lens field of view',
        subtype='ANGLE',
        min=math.radians(1),
        max=math.radians(180),
        soft_max=math.radians(125),
        step=100.0,
    )

    is_perspective: bpy.props.BoolProperty(
        name='Perspective',
        description='Is perspective',
        default=True,
    )
