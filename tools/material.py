import os
import bpy

from . import common as Common
from .register import register_wrap
from .translations import t

from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeBsdfAnisotropic


@register_wrap
class OneTexPerMatButton(bpy.types.Operator):
    bl_idname = 'cats_material.one_tex'
    bl_label = t('OneTexPerMatButton.label')
    bl_description = t('OneTexPerMatButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def execute(self, context):
        self.report({'ERROR'}, t('ToolsMaterial.error.notCompatible'))
        return {'CANCELLED'}

        saved_data = Common.SavedData()

        Common.set_default_stage()

        for mesh in Common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                for i, tex_slot in enumerate(mat_slot.material.texture_slots):
                    if i > 0 and tex_slot:
                        mat_slot.material.use_textures[i] = False

        saved_data.load()

        self.report({'INFO'}, t('OneTexPerMatButton.success'))
        return {'FINISHED'}


@register_wrap
class OneTexPerMatOnlyButton(bpy.types.Operator):
    bl_idname = 'cats_material.one_tex_only'
    bl_label = t('OneTexPerMatOnlyButton.label')
    bl_description = t('OneTexPerMatOnlyButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def execute(self, context):
        self.report({'ERROR'}, t('ToolsMaterial.error.notCompatible'))
        return {'CANCELLED'}

        saved_data = Common.SavedData()

        Common.set_default_stage()

        for mesh in Common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                for i, tex_slot in enumerate(mat_slot.material.texture_slots):
                    if i > 0 and tex_slot:
                        tex_slot.texture = None

        saved_data.load()

        self.report({'INFO'}, t('OneTexPerXButton.success'))
        return {'FINISHED'}


@register_wrap
class StandardizeTextures(bpy.types.Operator):
    bl_idname = 'cats_material.standardize_textures'
    bl_label = t('StandardizeTextures.label')
    bl_description = t('StandardizeTextures.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def execute(self, context):
        self.report({'ERROR'}, t('ToolsMaterial.error.notCompatible'))
        return {'CANCELLED'}

        saved_data = Common.SavedData()

        Common.set_default_stage()

        for mesh in Common.get_meshes_objects():
            for mat_slot in mesh.material_slots:

                mat_slot.material.transparency_method = 'Z_TRANSPARENCY'
                mat_slot.material.alpha = 1

                for tex_slot in mat_slot.material.texture_slots:
                    if tex_slot:
                        tex_slot.use_map_alpha = True
                        tex_slot.use_map_color_diffuse = True
                        tex_slot.blend_type = 'MULTIPLY'

        saved_data.load()

        self.report({'INFO'}, t('StandardizeTextures.success'))
        return {'FINISHED'}


@register_wrap
class CombineMaterialsButton(bpy.types.Operator):
    bl_idname = 'cats_material.combine_mats'
    bl_label = t('CombineMaterialsButton.label')
    bl_description = t('CombineMaterialsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    combined_tex = {}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def assign_material_slots(self, ob, matlist):
        scn = bpy.context.scene
        ob_active = Common.get_active()
        Common.set_active(ob)

        for s in ob.material_slots:
            bpy.ops.object.material_slot_remove()

        i = 0
        for m in matlist:
            mat = bpy.data.materials[m]
            ob.data.materials.append(mat)
            i += 1

        Common.set_active(ob_active)

    def clean_material_slots(self):
        objs = bpy.context.selected_editable_objects

        for ob in objs:
            if ob.type == 'MESH':
                Common.set_active(ob)
                bpy.ops.object.material_slot_remove_unused()

    def generate_combined_tex(self):
        self.combined_tex = {}
        for ob in Common.get_meshes_objects():
            for index, mat_slot in enumerate(ob.material_slots):
                hash_this = ''
                ignore_nodes = ['Material Output', 'mmd_tex_uv', 'Cats Export Shader']

                if mat_slot.material and mat_slot.material.node_tree:
                    nodes = mat_slot.material.node_tree.nodes
                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            hash_this += node.name
                            if 'Base Color' in node.inputs:
                                hash_this += str(node.inputs['Base Color'].default_value[:])
                            if 'Subsurface Weight' in node.inputs:
                                hash_this += str(node.inputs['Subsurface Weight'].default_value)

                        elif node.type == 'BSDF_ANISOTROPIC':
                            hash_this += node.name

                        if node.name in ignore_nodes or node.label in ignore_nodes:
                            continue

                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if 'toon' in node.name or 'sphere' in node.name:
                                nodes.remove(node)
                                continue
                            if not image:
                                nodes.remove(node)
                                continue
                            hash_this += node.name + image.name
                            continue

                        if not node.inputs:
                            continue

                        if node.name == 'mmd_shader':
                            hash_this += node.name\
                                         + str(node.inputs['Diffuse Color'].default_value[:])\
                                         + str(node.inputs['Alpha'].default_value)
                            continue

                        hash_this += node.name
                        for input, value in node.inputs.items():
                            if hasattr(value, 'default_value'):
                                try:
                                    hash_this += str(value.default_value[:])
                                except TypeError:
                                    hash_this += str(value.default_value)
                            else:
                                hash_this += value.name                               
                if hash_this not in self.combined_tex:
                    self.combined_tex[hash_this] = []
                self.combined_tex[hash_this].append({'mat': mat_slot.name, 'index': index})

    def get_image_textures(self, material_name):
        textures = []
        if bpy.data.materials[material_name].node_tree is not None:
            for node in bpy.data.materials[material_name].node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    textures.append(node)
        return textures

    def copy_textures(self, image_textures, target_material):
        if target_material.node_tree is not None:
            for texture in image_textures:
                new_texture_node = target_material.node_tree.nodes.new(type='ShaderNodeTexImage')
                new_texture_node.image = texture.image

    def combine_materials(self, file):
        target_material = bpy.data.materials.new(name="CombinedMaterial")
        return target_material

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        self.generate_combined_tex()
        Common.switch('OBJECT')
        i = 0

        for index, mesh in enumerate(Common.get_meshes_objects()):

            Common.unselect_all()
            Common.set_active(mesh)

            for file in self.combined_tex:
                combined_textures = self.combined_tex[file]
                target_material = self.combine_materials(file)

                if len(combined_textures) <= 1:
                    continue

                image_textures = self.get_image_textures(combined_textures[0]['mat'])
                self.copy_textures(image_textures, target_material)

                if target_material.name not in mesh.data.materials:
                    mesh.data.materials.append(target_material)

                Common.switch('EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')

                for mat in mesh.material_slots:
                    for tex in combined_textures:
                        if mat.name == tex['mat']:
                            mesh.active_material_index = tex['index']
                            bpy.ops.object.material_slot_select()

                    bpy.ops.object.material_slot_assign()
                    bpy.ops.mesh.select_all(action='DESELECT')

                Common.unselect_all()
                Common.set_active(mesh)
                Common.switch('OBJECT')
                self.clean_material_slots()
                Common.clean_material_names(mesh)

                i += 1

        Common.update_material_list()
        saved_data.load()

        if i == 0:
            self.report({'INFO'}, t('CombineMaterialsButton.error.noChanges'))
        else:
            self.report({'INFO'}, t('CombineMaterialsButton.success', number=str(i)))

        return {'FINISHED'}

@register_wrap
class ConvertAllToPngButton(bpy.types.Operator):
    bl_idname = 'cats_material.convert_all_to_png'
    bl_label = t('ConvertAllToPngButton.label')
    bl_description = t('ConvertAllToPngButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bpy.data.images

    def execute(self, context):
        images_to_convert = self.get_convert_list()

        if images_to_convert:
            current_step = 0
            wm = bpy.context.window_manager
            wm.progress_begin(current_step, len(images_to_convert))

            for image in images_to_convert:
                self.convert(image)
                current_step += 1
                wm.progress_update(current_step)

            wm.progress_end()

        self.report({'INFO'}, t('ConvertAllToPngButton.success', number=str(len(images_to_convert))))
        return {'FINISHED'}

    def get_convert_list(self):
        images_to_convert = []
        for image in bpy.data.images:
            tex_path = bpy.path.abspath(image.filepath)
            if tex_path.endswith(('.png', '.spa', '.sph')) or not os.path.isfile(tex_path):
                print('IGNORED:', image.name, tex_path)
                continue
            images_to_convert.append(image)
        return images_to_convert

    def convert(self, image):
        image_name = image.name
        print(image_name)
        image_name_new = ''
        for s in image_name.split('.')[0:-1]:
            image_name_new += s + '.'
        image_name_new += 'png'
        print(image_name_new)

        tex_path = bpy.path.abspath(image.filepath)
        print(tex_path)
        tex_path_new = ''
        for s in tex_path.split('.')[0:-1]:
            tex_path_new += s + '.'
        tex_path_new += 'png'
        print(tex_path_new)

        view_transform = bpy.context.scene.view_settings.view_transform
        bpy.context.scene.view_settings.view_transform = 'Standard'

        scene = bpy.context.scene
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 100
        image.save_render(tex_path_new, scene=scene)

        bpy.context.scene.view_settings.view_transform = view_transform

        bpy.data.images[image_name].filepath = tex_path_new
        bpy.data.images[image_name].name = image_name_new

        return True
