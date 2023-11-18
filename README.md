# Cats Blender Plugin (0.30.1).

#### This version of Cats does allow Blender 4.0, however due to some issues with 4.0 and the current compatibility of cats and MMD tools I highly recommend you use 3.6 for now. Please do not report any issues relating to 4.0, If you hit any issues please downgrade to Blender 3.6 for the time being. This is because MMD Tools currently does not support Blender 4.0 and unto it does we can not fully support 4.0.
#### Cat's will no longer work in Blender versions older then 2.9.

The non official version of Cats Blender Plugin which is maintained by Yusarina, Cats is an tool designed to shorten steps needed to import and optimize models into VRChat.
Compatible models are: MMD, XNALara, Mixamo, Source Engine, Unreal Engine, DAZ/Poser, Blender Rigify, Sims 2, Motion Builder, 3DS Max and potentially more

With Cats it takes only a few minutes to upload your model into VRChat.
All the hours long processes of fixing your models are compressed into a few functions!

So if you enjoy how this plugin saves you countless hours of work consider supporting us through Patreon.
There are a lot of perks like having your name inside the plugin!

## Features (Click to Expand)
 - <details><summary>Creating lip syncing</summary>

   ## Visemes (Lip Sync)
   ![](https://i.imgur.com/SWjhe9y.png)

   **Mouth visemes are used to show more realistic mouth movement in-game when talking over the microphone.**
   The script generates 15 shape keys from the 3 shape keys you specified. It uses the mouth visemes A, OH and CH to generate this output.
   </details>

 - <details><summary>Automatic decimation (while keeping shapekeys)</summary>

   ## Decimation

   ![](https://i.imgur.com/5u3teLp.png)

   **Decimate your model automatically.**

   ##### Save Decimation
   - This will only decimate meshes with no shape keys.

   ##### Half Decimation
   - This will only decimate meshes with less than 4 shape keys as those are often not used.

   ##### Full Decimation
   - This will decimate your whole model deleting all shape keys in the process.

   ##### Custom Decimation
   - This lets you choose the meshes and shape keys that should not be decimated.

   </details>
 - <details><summary>Creating root bones for Dynamic Bones</summary>

   ## Bone parenting

   ![](https://i.imgur.com/lH8lNVa.png)

   **Useful for Dynamic Bones where it is ideal to have one root bone full of child bones.**
   This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then press 'Parent bones' and the child bones will be parented to a new bone named RootBone_xyz

   ##### To parent
   - List of bones that look like they could be parented together to a root bone. Select a group of bones from the list and press "Parent bones"

   ##### Refresh list
   - Clears the group bones list cache and rebuild it, useful if bones have changed or your model

   ##### Parent bones
   - Starts the parent process

 - <details><summary>Optimizing materials by creating an atlas</summary>

   ## Texture atlas

   ![](https://i.imgur.com/Mav3P9e.png)

   **Texture atlas is the process of combining multiple textures into one to drastically reduce draw calls and therefore make your model much more performant**

   ##### Create Atlas
   - Combines all selected materials into one texture. If no material list is generated it will combine all materials.

   ##### Generate Material List
   - Lists all materials of the current model and lets you select which ones you want to combine.

   ##### Useful Tips:
   - Split transparent and non-transparent textures into separate atlases to avoid transparency issues
   - Make sure that the created textures are not too big, because Unity will downscale them to 2048x2048.
     Split them across multiple atlases or reduce the individual texture sizes. This can be easily done in the MatCombiner tab.
   - You can tell Unity to use up to 8k textures.
     Do so by selecting the texture and then choose a different Max Size and/or Compression in the inspector:
     ![](https://i.imgur.com/o01T4Gb.png)

   </details>
 - <details><summary>Creating custom models easily</summary>

   ## Custom Model Creation

   ![](https://i.imgur.com/WZJybq1.png)
   ![](https://i.imgur.com/Ow8vvt1.png)

   **This makes creating custom avatars a breeze!**

   ##### Merge Armatures
   - Merges the selected armature into the selected base armature.
   - **How to use:**
     - Use "Fix Model" on both armatures
       - Select the armature you want to fix in the list above the Fix Model button
       - Ignore the "Bones are missing" warning if one of the armatures is incomplete (e.g hair only)
       - If you don't want to use "Fix Model" make sure that the armature follows the CATS bone structure (https://i.imgur.com/F5KEt0M.png)
       - DO NOT delete any main bones by yourself! CATS will merge them and delete all unused bones afterwards
     - Now you have two options:
       - Only move the mesh:
         - Uncheck the checkbox "Apply Transforms"
         - Move the mesh (and only the mesh!) of the merge armature to the desired position
           - You can use Move, Scale and Rotate
           - CATS will position the bones according to the mesh automatically
       - OR move the armature (and with it the mesh):
         - Check the checkbox "Apply Transforms"
         - Move the armature to the desired position
           - You can use Move, Scale and Rotate
           - Make sure that both meshes and armatures are at their correct positions as they will stay exactly like this
       - If you want to merge multiple objects from the same model it is often better to duplicate the armature for each of them and merge them individually
     - Select the base armature and the armature you want to merge into the base armature in the panel
     - If CATS can't detect the bone structure automatically: select a bone you want to attach the new armature to
       - E.g.: For a hair armature select "Head" as the bone
     - Press the "Merge Armatures" button -> Done!

   ##### Attach Mesh to Armature
   - Attaches the selected mesh to the selected armature.
   - **How to use:**
     - Move the mesh to the desired position
       - You can use Move, Scale and Rotate
       - INFO: The mesh will only be assigned to the selected bone
       - E.g.: A jacket won't work, because it requires multiple bones.
       - E.g.: A ring on a finger works perfectly, because the ring only needs one bone to move with (the finger bone)
     - Select the base armature and the mesh you want to attach to the base armature in the panel
     - Select the bone you want to attach the mesh to in the panel
     - Press the "Attach Mesh" button -> Done!

   </details>

 - <details><summary>Translating shape keys, bones, materials and meshes. Fixing and joining/separation of meshes.</summary>

   ## Model Options

   ![](https://i.imgur.com/y6e3oYS.png)

   ##### Translation
   - Translate certain entities from any japanese to english.
   This uses an internal dictionary and Google Translate.

   ##### Separate by material / loose parts / shapes
   - Separates a mesh by materials or loose parts or by whether or not the mesh is effected by a shape key

   ##### Join meshes
   - Joins all/selected meshes together

   ##### Merge Weights
   - Deletes the selected bones and adds their weight to their respective parents

   ##### Delete Zero Weight Bones
   - Cleans up the bones hierarchy, deleting all bones that don't directly affect any vertices

   ##### Delete Constraints
   - Removes constrains between bones causing specific bone movement as these are not used by VRChat

   ##### Recalculate Normals
   - Makes normals point inside of the selected mesh
   - Don't use this on good looking meshes as this can screw them up

   ##### Flip Normals
   - Flips the direction of the faces' normals of the selected mesh.

   ##### Apply Transformations
   - Applies the position, rotation and scale to the armature and its meshes.

   ##### Remove Doubles
   - Merges duplicated faces and vertices of the selected meshes.
   </details>
 - <details><summary> Merging bone groups to reduce overall bone count.</summary>

   ## Bone merging

   ![](https://i.imgur.com/PL8THn8.png)

   **Lets you reduce overall bone count in a group set of bones.**
   This works by checking all bones and trying to figure out if they can be grouped together, which will appear in a list for you to choose from. After satisfied with the selection of this group you can then set a percentage value how much bones you would like to merge together in itself and press 'Merge bones'

   ##### Refresh list
   - Clears the group bones list cache and rebuild it, useful if bones have changed or your model

   ##### Merge bones
   - Starts the merge process

   </details>
 - <details><summary>Auto updater and daily build of fixes from the dev</summary>

   ## Settings and Updates

   ![SettingsSection](https://i.imgur.com/mcRBg7W.png)

   **This plugin has an auto updater.**
   It checks for a new version automatically once every day.
   This is also where you can install dev version, a most recent build of bug fixes and beta features.
   Dev version is updated automatically to your machine. Dev version changes very often in response to bugs and issues reported in the issues page on github or on the cats discord server.
   </details>
 - <details><summary>Import a variety of models, test your model movements, and fix common model sources like SFM/Source and MMD</summary>

   ## Model
   ![](https://i.imgur.com/rfDIy6e.png)

   ##### Import/Export Model
   - Imports a model of the selected type with the optimal settings
   - Exports a model as an .fbx with the optimal settings

   ##### Fix Model
   - Fixes your model automatically by:
     - Reparenting bones
     - Removing unnecessary bones
     - Renaming and translating objects and bones
     - Mixing weight paints
     - Rotating the hips
     - Joining meshes
     - Removing rigidbodies, joints and bone groups
     - Removing bone constraints
     - Deleting unused vertex groups
     - Using the correct shading
     - Making it compatible with Full Body Tracking
     - Combining similar materials

   ##### Start Pose Mode
   - Lets you test how bones will move.

   ##### Pose to Shape Key
   - Saves your current pose as a new shape key.

   ##### Apply as Rest Pose
   - Applies the current pose position as the new rest position. This saves the shape keys and repairs ones that were broken due to scaling
   </details>
 - <details><summary>Applying shapekey to basis (ex: open mouth -> close mouth)</summary>

   ## Shape Key

   ![](https://i.imgur.com/zEnr1KA.png)

   **Apply Shape Key as Basis**
   - Applies the selected shape key as the new Basis and creates a reverted shape key from the selected one.
   </details>

 - <details><summary>Avatars 3.0 Eye Tracking Panel</summary>

   ## Avatars 3.0 Eye Tracking Panel
   ![](https://i.imgur.com/x5Hkmfi.png)

   **Rotate eye bones so they point straight up and have zero roll, simplifying the eye-tracking setup in Unity for VRChat.**
   This feature was a pull request by Mysteryem on the original Cats project so i ported it over.
   Original request https://github.com/absolute-quantum/cats-blender-plugin/pull/599
   </details>

## Requirements

- Blender 2.9 or above (run as administrator is recommended)
  - Blender 3.6 is Recommended as this is the latest LTS.
  - Though I have updated CATS to Blender 4.0, I do not currently recommend using 4.0 as there multiple issues with MDD Tools and Blender 4.0 which cats uses.
  - Anything older then 2.9 is not supported and no longer works.
  - In the future I won't be allowing anything older then Blender 3.3.
- If you have custom Python installed which Blender might use, you need to have Numpy installed

## Installation

- Download the plugin: [Cats Blender Plugin](https://github.com/Yusarina/Cats-Blender-Plugin-Unofficial-/archive/refs/heads/main.zip)
   - **Important: Do NOT extract the downloaded zip! You will need the zip file during installation!**
 - Install the addon in blender like so:
   - In Blender 2.80+ go to Edit > Preferences > Add-ons. Also you don't need to save the user settings there. Though this plugin may still work on Blender 2.79, it is no longer supported.

![](https://i.imgur.com/LsEDL6q.gif)

If installed correctly you should see cat's in your 3D View on your side bar (This appears when pressing the N Key on your keyboard). See image below.

![](https://i.imgur.com/WPoLbwK.png)

## Help

If you need help with Cat's you can check the wiki [here](https://github.com/Yusarina/Cats-Blender-Plugin-Unofficial-/wiki).
You can also see the the following video tutorials as well (Please note these videos may become outdated over time).

[![VRCHAT Avatar Setup - Blender CATS Plugin](https://i.ytimg.com/vi/2fJMaxbBewg/0.jpg)](https://www.youtube.com/watch?v=2fJMaxbBewg)

[![Full Blender Tutorial on how to create VRChat models](https://i.ytimg.com/vi/2NdPHW4_SOg/0.jpg)](https://www.youtube.com/watch?v=2NdPHW4_SOg)

## Acknowledgements

Maintained by Yusarina.

### Code contributors:
- Hotox
- Shotariya
- Neitri
- Kiraver
- Jordo
- Ruubick
- 989onan

Cats Blender Plugin was original developed by absolute quantum then maintained by the community, [click here](https://github.com/absolute-quantum/cats-blender-plugin) to see the original project.

### Cat's Uses the Following Plugins to Enhance it's features:

 - [MMD Tools](https://github.com/UuuNyaa/blender_mmd_tools)
 - [Immersive Scaler](https://github.com/triazo/immersive_scaler)
 - [Material Combiner](https://github.com/Grim-es/material-combiner-addon)

## Feedback

Please open an issue if you need to leave feedback.

## Change Log

<details><summary>0.30.1</summary>

   ## 0.30.1
   #### IMPORTANT! This will be the last version that supports Blender 2.8, 2.9 or 3.0. Next versions will only support 3.1 and above, this is due to MMD tools not working as well on older versions.

- Added Support for Blender 4.0.
- Updated Readme with newer text and pictures.
- Fixed Text in the dev build installtion confirmation not displaying.
- Fixed the quick decimation button lable and description not displaying.
- Fixed the "bpy.ops.mmd_tools.set_shadeless_glsl_shading" error.
</details>
<details><summary>0.30.0</summary>

   ## 0.30.0
   ###IMPORTANT: This will be the last version that supports Blender 2.79.

- Cats no longer supports blender versions older then 2.8, this means I dropped support for 2.79.
- Change to some internal classes which seem to conflict with Tuxedo, hopefully this fixes issues if you have both plugins.
- Bug fixes.
</details>
<details><summary>0.20.1</summary>

   ## 0.20.1

- Updated MMD Tools to latest version.
- Change patchlog link to correct github.
- Updated Wiki link.
- Removed all VRC SDK 2.0 stuff, SDK2 is now completely obsolete and should not be used anyway.
</details>
<details><summary>0.20.0</summary>

   ## 0.20.0

- Removed Patreon and removed supporters tab fully. I done this because the original project is dead.
- Change the discord link to go to the github wiki, i going to put up some basic things on there at somepoint.
- Added in credits that i maintaining this version.
- Added 3.0 Eye Tracking by Mysteryem
- Fix for Unselect all being called too many times.
</details>
<details><summary>0.19.3</summary>

   ## 0.19.3

- Fix for update loop.
</details>
<details><summary>0.19.2</summary>

   ## 0.19.2

- Updated for Blender 3.6
</details>
<details><summary>0.19.1</summary>

   ## 0.19.1

- Fixed Google Translate error (you aren't banned by Google)
</details>
<details><summary>0.19.0</summary>

   ## 0.19.0

- **Fully compatible with Blender 2.93**
- **Translations:**
  - **Added Korean translation!**
    - Cats is now translated into Korean by a large portion
    - To use it, simply change your Blender language to Korean and then restart Blender or select it in the Cats Settings
    - Thanks to **Siromori** for contributing the translation! <3
  - Added Cats Ui Language setting
    - This lets you choose in which language Cats should be displayed
    - Setting it to "auto" will choose the current Blender language
  - Added button to download the latest Cats Translations
    - This feature is for translators to test their translations in the plugin
    - If you want to help to translate Cats into any language, please let me (Hotox) know in our Discord
- **Model Options:**
  - Added "Connect Bones" button
  - Added options to keep merged bones and to merge the bones of visible meshes only
- **Custom Model Creation:**
  - Reworked "Attach Mesh" feature, it is much more reliable now
- **General:**
  - Fixed translation errors
  - Updated mmd_tools
- **Bake: (by feilen)**
  - Emission influence baking: fake realtime lighting based on your emissive channel, quest-compatible!
  - 'Manual' reprojection mode for Bake: creating new UV maps called 'Target' will allow you to re-bake to a specific layout.
  - 'Optimize static shapekeys' option
    - Splits your mesh into two skinned meshes, one with all shapekey-influenced geometry,
      one with the rest (and fixes the normals in place). Significantly improves GPU performance, especially when a lot of shapekeys are in effect.
      Needs the lighting anchor point in Unity to be set to the armature Hips on both, or you'll get lighting artifacts.
  - Introduce 'BakeFixer.cs', which is a run-time unity script that hopefully should do the lighting work for you.
  - 'Ignore hidden objects' option
    - When baking, this will ignore any objects you currently have hidden, making it easier to create different versions of your avatar.
  - Apply Current Shapekey Mix option
    - Sets your basis to whatever current mix of shapekeys you have. Always-on shapekeys are terrible for performance,
      so if you have some that are only intended to customize the character without updates, this will help with that.
  - '_bake' shapekeys: any shapekey with '_bake' at the end will be applied and completely removed, allowing the static shapekeys option to work better.
    If you're an avatar creator distributing bases, this is recommended for character customization keys!
  - Misc: Updated defaults to be in line with updated Quest limits.
</details>

Read the full changelog for the original Cat's here. [here](https://github.com/michaeldegroot/cats-blender-plugin/releases).

Read the full changelog for this version Cat's here. [here](https://github.com/Yusarina/Cats-Blender-Plugin-Unofficial-/releases).
