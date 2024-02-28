import os
import bpy

from . import common as Common
from .register import register_wrap
from .translations import t
from mmd_tools_local.operators import morph as Morph
from . import armature as Armature
mmd_tools_local_installed = True

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

    def assignmatslots(self, ob, matlist):
        context = bpy.context
        scn = bpy.context.scene
        ob_active = context.view_layer.objects.active
        Common.set_active(ob)

        for s in ob.material_slots:
            bpy.ops.object.material_slot_remove()

        i = 0
        for m in matlist:
            mat = bpy.data.materials[m]
            ob.data.materials.append(mat)
            i += 1

        Common.set_active(ob_active)

    def cleanmatslots(self):
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

    def execute(self, context):
        print('COMBINE MATERIALS!')
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

                if len(combined_textures) <= 1:
                    continue
                i += len(combined_textures)

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
            self.cleanmatslots()

            Common.clean_material_names(mesh)


        Common.update_material_list()

        saved_data.load()

        if i == 0:
            self.report({'INFO'}, t('CombineMaterialsButton.error.noChanges'))
        else:
            self.report({'INFO'}, t('CombineMaterialsButton.success', number=str(i)))

        return {'FINISHED'}


@register_wrap
class FixMaterialsButton(bpy.types.Operator):
    bl_idname = 'cats_material.fix'
    bl_label = t('FixMaterialsButton.label')
    bl_description = t('FixMaterialsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False

        if len(Common.get_armature_objects()) == 0:
            return False

        return True

    def execute(self, context):           
        armature = Common.get_armature()
        meshes = Common.get_meshes_objects()

        Common.set_material_shading()

        # If all materials are transparent, make them visible. Also set transparency always to Z-Transparency
            # Make materials exportable in Blender 2.80 and remove glossy mmd shader look
            # Common.remove_toon_shader(mesh)
        for mesh in meshes:
            # Clean material names before trying to fix them.
            Common.clean_material_names(mesh)
            
            if mmd_tools_local_installed:
                Common.fix_mmd_shader(mesh)
            Common.fix_vrm_shader(mesh)
            Common.add_principled_shader(mesh)
            for mat_slot in mesh.material_slots:  # Fix transparency per polygon and general garbage look in blender. Asthetic purposes to fix user complaints.
                mat_slot.material.shadow_method = "HASHED"
                mat_slot.material.blend_method = "HASHED"
        
        materials = set() 

        self.report({'INFO'}, "Fixed materials")
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