# MIT License

import re
import os
import bpy
import copy
import json
import pathlib
import traceback
import collections
import requests.exceptions
import csv

from datetime import datetime, timezone
from collections import OrderedDict

from . import common as Common
from pathlib import Path
from .register import register_wrap
from .. import globs
# from ..googletrans import Translator  # TODO Remove this
from ..extern_tools.google_trans_new.google_trans_new import google_translator
from .translations import t

from mmd_tools_local import translations as mmd_translations

LANGUAGE_CODES = {
    'Japanese': 'ja',
    'Korean': 'ko'
}

selected_source_language = LANGUAGE_CODES['Japanese']

dictionary = {}
dictionary_google = {}

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
dictionary_file = os.path.join(resources_dir, "dictionary.json")
dictionary_google_file = os.path.join(resources_dir, "dictionary_google.json")

# Constant for Japanese character regex
JAPANESE_CHAR_REGEX = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'

def get_cats_dir(context):
    prefs = context.preferences.addons["cats-blender-plugin"].preferences
    
    if prefs.custom_shapekeys_export_dir: 
        return prefs.custom_shapekeys_export_dir
    
    # Fallback to default cats directory
    return os.path.join(bpy.utils.user_resource('DATAFILES'), "cats") 

@register_wrap
class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'cats_translate.shapekeys'
    bl_label = t('TranslateShapekeyButton.label')
    bl_description = t('TranslateShapekeyButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        saved_data = Common.SavedData()

        cats_dir = context.scene.custom_shapekeys_export_dir
        if not cats_dir:
            # Fallback to default dir
            cats_dir = get_cats_dir(context)  
            
        # Check if dir exists or can be created
        if not os.path.exists(cats_dir):
            try:
                os.makedirs(cats_dir) 
            except OSError:
                self.report({'ERROR'}, "Unable to create export folder. Please manually set the export directory")
                return {'CANCELLED'}
                
        if not os.path.exists(cats_dir) or not os.access(cats_dir, os.W_OK):  
            self.report({'ERROR'}, "Unable to write to export folder. Please manually set the export directory")
            return {'CANCELLED'}
            
        if context.scene.export_shapekeys_csv:
            
            blend_path = bpy.context.blend_data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save blend first!")
                return {'CANCELLED'}
            
            to_translate = []
            for mesh in Common.get_meshes_objects(mode=2):
                if Common.has_shapekeys(mesh):
                    for key in mesh.data.shape_keys.key_blocks:
                        if 'vrc.' not in key.name:
                            to_translate.append(key.name)

            update_dictionary(to_translate, translating_shapes=True, self=self)
            Common.update_shapekey_orders()
            
            shapekeys = []
            i = 0
            for mesh in Common.get_meshes_objects(mode=2):
                if Common.has_shapekeys(mesh):
                    for key in mesh.data.shape_keys.key_blocks:
                        if 'vrc.' not in key.name:  
                            original_name = key.name
                            key.name, translated = translate(key.name, add_space=True, translating_shapes=True)
                
                            if translated:
                                i += 1
                                shapekeys.append({
                                    'mesh/object': mesh.name,
                                    'original': original_name,
                                    'translated': key.name
                                })

            blend_name = os.path.splitext(os.path.basename(blend_path))[0] 
            export_path = os.path.join(str(cats_dir), blend_name + "_shapekeys.csv")
            
            with open(export_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['mesh/object', 'original', 'translated'])
                for key in shapekeys:
                    writer.writerow([key['mesh/object'], key['original'], key['translated']])

        else:
            to_translate = []
            for mesh in Common.get_meshes_objects(mode=2):
                if Common.has_shapekeys(mesh):
                    for shapekey in mesh.data.shape_keys.key_blocks:
                        if 'vrc.' not in shapekey.name and shapekey.name not in to_translate:
                            to_translate.append(shapekey.name)

            update_dictionary(to_translate, translating_shapes=True, source_language=selected_source_language, self=self)

            Common.update_shapekey_orders()

            i = 0
            for mesh in Common.get_meshes_objects(mode=2):
                if Common.has_shapekeys(mesh):
                    for shapekey in mesh.data.shape_keys.key_blocks:
                        if 'vrc.' not in shapekey.name:
                            shapekey.name, translated = translate(shapekey.name, add_space=True, translating_shapes=True)
                            if translated:
                                i += 1

        Common.ui_refresh()

        saved_data.load()

        self.report({'INFO'}, t('TranslateShapekeyButton.success', number=str(i)))
        return {'FINISHED'}


@register_wrap
class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'cats_translate.bones'
    bl_label = t('TranslateBonesButton.label')
    bl_description = t('TranslateBonesButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False
        return True

    def execute(self, context):
        to_translate = []
        for armature in Common.get_armature_objects():
            for bone in armature.data.bones:
                to_translate.append(bone.name)

        update_dictionary(to_translate, self=self)

        count = 0
        for armature in Common.get_armature_objects():
            for bone in armature.data.bones:
                bone.name, translated = translate(bone.name)
                if translated:
                    count += 1

        self.report({'INFO'}, t('TranslateBonesButton.success', number=str(count)))
        return {'FINISHED'}


@register_wrap
class TranslateObjectsButton(bpy.types.Operator):
    bl_idname = 'cats_translate.objects'
    bl_label = t('TranslateObjectsButton.label')
    bl_description = t('TranslateObjectsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}
        to_translate = []
        for obj in Common.get_objects():
            if obj.name not in to_translate:
                to_translate.append(obj.name)
            if obj.type == 'ARMATURE':
                if obj.data and obj.data.name not in to_translate:
                    to_translate.append(obj.data.name)
                if obj.animation_data and obj.animation_data.action:
                    to_translate.append(obj.animation_data.action.name)

        update_dictionary(to_translate, self=self)

        i = 0
        for obj in Common.get_objects():
            obj.name, translated = translate(obj.name)
            if translated:
                i += 1

            if obj.type == 'ARMATURE':
                if obj.data:
                    obj.data.name, translated = translate(obj.data.name)
                    if translated:
                        i += 1

                if obj.animation_data and obj.animation_data.action:
                    obj.animation_data.action.name, translated = translate(obj.animation_data.action.name)
                    if translated:
                        i += 1

        self.report({'INFO'}, t('TranslateObjectsButton.success', number=str(i)))
        return {'FINISHED'}


@register_wrap
class TranslateMaterialsButton(bpy.types.Operator):
    bl_idname = 'cats_translate.materials'
    bl_label = t('TranslateMaterialsButton.label')
    bl_description = t('TranslateMaterialsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}

        saved_data = Common.SavedData()

        to_translate = []
        for mesh in Common.get_meshes_objects(mode=2):
            for matslot in mesh.material_slots:
                if matslot.name not in to_translate:
                    to_translate.append(matslot.name)

        update_dictionary(to_translate, self=self)

        i = 0
        for mesh in Common.get_meshes_objects(mode=2):
            Common.set_active(mesh)
            for index, matslot in enumerate(mesh.material_slots):
                mesh.active_material_index = index
                if bpy.context.object.active_material:
                    bpy.context.object.active_material.name, translated = translate(bpy.context.object.active_material.name)
                    if translated:
                        i += 1

        saved_data.load()
        self.report({'INFO'}, t('TranslateMaterialsButton.success', number=str(i)))
        return {'FINISHED'}


@register_wrap
class TranslateAllButton(bpy.types.Operator):
    bl_idname = 'cats_translate.all'
    bl_label = t('TranslateAllButton.label')
    bl_description = t('TranslateAllButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}

        error_shown = False

        try:
            if Common.get_armature():
                bpy.ops.cats_translate.bones('INVOKE_DEFAULT')
        except RuntimeError as e:
            self.report({'ERROR'}, str(e).replace('Error: ', ''))
            error_shown = True

        try:
            bpy.ops.cats_translate.shapekeys('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        try:
            bpy.ops.cats_translate.objects('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        try:
            bpy.ops.cats_translate.materials('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        if error_shown:
            return {'CANCELLED'}
        self.report({'INFO'}, t('TranslateAllButton.success'))
        return {'FINISHED'}


# Loads the dictionaries at the start of blender
def load_translations():
    global dictionary
    dictionary = OrderedDict()
    temp_dict = OrderedDict()
    dict_found = False

    # Load internal dictionary
    try:
        with open(dictionary_file, encoding="utf8") as file:
            temp_dict = json.load(file, object_pairs_hook=collections.OrderedDict)
            dict_found = True
            # print('DICTIONARY LOADED!')
    except FileNotFoundError:
        print('DICTIONARY NOT FOUND!')
        pass
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN DICTIONARY")
        pass

    # Load local google dictionary and add it to the temp dict
    try:
        with open(dictionary_google_file, encoding="utf8") as file:
            global dictionary_google
            dictionary_google = json.load(file, object_pairs_hook=collections.OrderedDict)

            if 'created' not in dictionary_google \
                    or 'translations' not in dictionary_google \
                    or 'translations_full' not in dictionary_google:
                reset_google_dict()
            else:
                for name, trans in dictionary_google.get('translations').items():
                    if not name:
                        continue

                    if name in temp_dict.keys():
                        print(name, 'ALREADY IN INTERNAL DICT!')
                        continue

                    temp_dict[name] = trans

            # print('GOOGLE DICTIONARY LOADED!')
    except FileNotFoundError:
        print('GOOGLE DICTIONARY NOT FOUND!')
        reset_google_dict()
        pass
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN GOOOGLE DICTIONARY")
        reset_google_dict()
        pass

    # Sort temp dictionary by lenght and put it into the global dict
    for key in sorted(temp_dict, key=lambda k: len(k), reverse=True):
        dictionary[key] = temp_dict[key]

    # for key, value in dictionary.items():
    #     print('"' + key + '" - "' + value + '"')

    return dict_found


def update_dictionary(to_translate_list, translating_shapes=False, source_language=selected_source_language, self=None):
    global dictionary, dictionary_google

    use_google_only = False
    if translating_shapes and bpy.context.scene.use_google_only:
        use_google_only = True

    # Check if single string is given and put it into an array
    if isinstance(to_translate_list, str):
        to_translate_list = [to_translate_list]

    google_input = set()

    # Translate everything
    for to_translate in to_translate_list:
        to_translate = fix_jp_chars(to_translate)

        # Translate shape keys with Google Translator only, if the user chose this
        if use_google_only:
            # If name doesn't contain any source language chars, don't translate
            if not re.findall(JAPANESE_CHAR_REGEX, to_translate):
                continue

            translated = False
            for key, value in dictionary_google.get(source_language, {}).get('translations_full', {}).items():
                if to_translate == key and value:
                    translated = True

            if not translated:
                google_input.add(to_translate)

        # Translate with internal dictionary
        else:
            def replace_with_translation(match):
                key = match.group()
                value = dictionary.get(source_language, {}).get(key)
                return value if value else key

            to_translate = re.sub(JAPANESE_CHAR_REGEX, replace_with_translation, to_translate)

            # If not fully translated, translate the rest with Google
            if re.search(JAPANESE_CHAR_REGEX, to_translate):
                google_input.update(re.findall(JAPANESE_CHAR_REGEX, to_translate))

    if not google_input:
        return

    # Translate the rest with google translate
    print('GOOGLE DICT UPDATE!')
    translator = google_translator(url_suffix='com')
    token_tries = 0
    while True:
        try:
            translations = []
            for text in google_input:
                translation = translator.translate(text, lang_src=source_language, lang_tgt='en').strip()
                if translation != text:
                    translations.append(translation)
                else:
                    print(f"Translation failed for: {text}")
                    translations.append(text)  # Use the original text if translation fails
            break
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            print('CONNECTION TO GOOGLE FAILED!')
            if self:
                self.report({'ERROR'}, t('update_dictionary.error.cantConnect'))
            return
        except json.JSONDecodeError as e:
            if self:
                print(traceback.format_exc())
                self.report({'ERROR'}, 'Either Google changed their API or you got banned from Google Translate temporarily!'
                                       '\nCats translated what it could with the local dictionary,'
                                       '\nbut you will have to try again later for the Google translations.')
            print('YOU GOT BANNED BY GOOGLE!')
            return
        except RuntimeError as e:
            error = Common.html_to_text(str(e))
            if self:
                if 'Please try your request again later' in error:
                    self.report({'ERROR'}, t('update_dictionary.error.temporaryBan') + t('update_dictionary.error.catsTranslated'))
                    print('YOU GOT BANNED BY GOOGLE!')
                    return

                if 'Error 403' in error:
                    self.report({'ERROR'}, t('update_dictionary.error.cantAccess') + t('update_dictionary.error.catsTranslated'))
                    print('NO PERMISSION TO USE GOOGLE TRANSLATE!')
                    return

                self.report({'ERROR'}, t('update_dictionary.error.errorMsg') + t('update_dictionary.error.catsTranslated') + '\n' + '\nGoogle: ' + error)
            print('', 'You got an error message from Google:', error, '')
            return
        except AttributeError:
            # If the translator wasn't able to create a stable connection to Google, just retry it again
            # This is an issue with Google since Nov 2020: https://github.com/ssut/py-googletrans/issues/234
            token_tries += 1
            if token_tries < 3:
                print('RETRY', token_tries)
                translator = google_translator(url_suffix='com')
                continue

            # If it didn't work after 3 tries, just quit
            # The response from Google was printed into "cats/resources/google-response.txt"
            if self:
                self.report({'ERROR'}, t('update_dictionary.error.apiChanged'))
            print('ERROR: GOOGLE API CHANGED!')
            print(traceback.format_exc())
            return

    # Update the dictionaries
    for name, translation in zip(google_input, translations):
        if use_google_only:
            dictionary_google.setdefault(source_language, {}).setdefault('translations_full', {})[name] = translation
        else:
            # Capitalize words
            translation_words = translation.split(' ')
            translation_words = [word.capitalize() for word in translation_words]
            translation = ' '.join(translation_words)

            dictionary.setdefault(source_language, {})[name] = translation
            dictionary_google.setdefault(source_language, {}).setdefault('translations', {})[name] = translation

        print(name, '->', translation)

    # Sort dictionary
    temp_dict = dictionary.get(source_language, {}).copy()
    dictionary[source_language] = OrderedDict(sorted(temp_dict.items(), key=lambda x: len(x[0]), reverse=True))

    # Save the google dict locally
    save_google_dict()

    print('DICTIONARY UPDATE SUCCEEDED!')


def translate(to_translate, add_space=False, translating_shapes=False, source_language=selected_source_language):
    global dictionary

    pre_translation = to_translate
    length = len(to_translate)
    translated_count = 0

    # Figure out whether to use google only or not
    use_google_only = False
    if translating_shapes and bpy.context.scene.use_google_only:
        use_google_only = True

    # Add space for shape keys
    addition = ' ' if add_space else ''

    # Convert half chars into full chars
    to_translate = fix_jp_chars(to_translate)

    # Translate shape keys with Google Translator only, if the user chose this
    if use_google_only:
        for key, value in dictionary_google.get(source_language, {}).get('translations_full', {}).items():
            if to_translate == key and value:
                to_translate = value
                break

    # Translate with internal dictionary
    else:
        for key, value in dictionary.get(source_language, {}).items():
            if key in to_translate:
                # If string is empty, replace it with a default value
                if not value:
                    value = 'EMPTY_TRANSLATION'

                to_translate = to_translate.replace(key, addition + value)

                # Check if string is fully translated
                translated_count += len(key)
                if translated_count >= length:
                    break

    # Perform additional string replacements and stripping using regex
    to_translate = re.sub(r'\.L', '_L', to_translate)
    to_translate = re.sub(r'\.R', '_R', to_translate)
    to_translate = re.sub(r'\s+', ' ', to_translate)
    to_translate = re.sub(r'[しっ]', '', to_translate)
    to_translate = to_translate.strip()

    return to_translate, pre_translation != to_translate

def fix_jp_chars(name):
    for values in mmd_translations.jp_half_to_full_tuples:
        if values[0] in name:
            name = name.replace(values[0], values[1])
    return name


def reset_google_dict():
    global dictionary_google
    dictionary_google = OrderedDict()

    now_utc = datetime.now(timezone.utc).strftime(globs.time_format)

    dictionary_google['created'] = now_utc
    dictionary_google['translations'] = {}
    dictionary_google['translations_full'] = {}

    save_google_dict()
    print('GOOGLE DICT RESET')


def save_google_dict():
    with open(dictionary_google_file, 'w', encoding="utf8") as outfile:
        json.dump(dictionary_google, outfile, ensure_ascii=False, indent=4)
