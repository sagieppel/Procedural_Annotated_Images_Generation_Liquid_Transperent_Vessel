# Description:
 This script will procedurally generate images of randomly shaped transparent vessels with random objects or simulated liquid inside the vessel, in random procedurally generated enviroments. 

## What this generate?

Procedurally generated images of transparent vessels containing liquid and objects. The data for each image includes segmentation maps, 3d depth maps, and normal maps of the transparent vessel, the liquid or object inside the vessel, and the environment. In addition, the properties of the vessel and materials inside it are given(color/transparency/roughness/metalness). 3d models of the objects (GTLF) are also supplied. Camera parameters and position are also included.



### This was run with Blender 2.93 with no additional add-ons

## Where to start: 
The best place to start is in the “Main” section in the last part of the DatasetGeneration script.
Note that the script refer to nodes in the blend file and can only be run with the DatasetGeneration.blend 

## What needed:  
Objects Folder, HDRI background folder, and a folder of PBR materials (Example folders are supplied as: “HDRI_BackGround”, “PBRMaterials”, and “Objects”).
However, if you want to create truely diverse images you need large number of backgrounds, objects, and PBR materials. This can be download for free at:
[HdriHaven](https://hdrihaven.com/), [cc0textures](https://cc0textures.com/), [Shapenet](https://shapenet.org/)

# How to use:
1) Go to the “Main” section of the DatasetGeneration.py script  (at the end of the script), in the “input parameter” subsection.
2) In the "OutFolder" parameter set path to where the generated images should be saved.
3) In the "HDRI_BackGroundFolder" parameter set path to where the background HDRI (for a start, use the example HDRI_BackGround, supplied)
4) In the "PBRMaterialsFolder" parameter set path to where the PBR materials (for a start, use the example PBRMaterials folder supplied)
5) In the "ObjectsFolder" parameter, set the path to where the objects file are saved (for a start, use the example object folder supplied).
6) Run the script from Blender or run the script from the command line using: "blender DatasetGeneration.blend -b -P DatasetGeneration.py"
Images should start appearing in the OutFolder after few minutes (depending on the rendering file). 
Note that while running, Blender will be paralyzed, and will not respond.

7. Once done, open the "VirtualDataSetEditCleanAndAddMasks.py" script. In the "MainDir" parameter set the path to the data folder you just generated (the OutFolder from 2). Run the script. This will add segmentation masks to the dataset.

# Additional parameters 
In the “Input parameters” of "Main" DatasetGeneration  script (last section of the script)
"NumSimulationsToRun" determines how many different environments to render into images (How many different images will be created).

The "ContentMode" prameter  Will determine the type of content that will be generated insid the vessel, this parameter have three states: 
1)"Liquid": liquid simulation inside the vessel (simulation can be time consuming)
2)"Objects":   objects inside the vessel (objects will be taken from the Objects folder)
3)"FlatLiquid": will create simple liquid with flat surface that fill the bottum of the vessel (no liquid simulation will be performed)


# Creating the dataset
Given Blender’s tendency to crash, running this script alone is problematic for large datasets creation. To avoid the need to restart the program every time Blender crashes, use the shell script RunGeneration.sh. This script will run the blender file in a loop, so it will restart every time Blender crashes. This can be run from shell/cmd/terminal: using: sh Run.sh 



# Notes:
1) Try to avoid relative paths; Blender is not very good with those.
2) Running this script should paralyze Blender until the script is done, which can take a while.
3) The script refers to materials nodes and will only run as part of the blender file


# Sources for objects/HDRI/PBR materials
1) Objects were taken from [Shapenet](https://shapenet.org/). Blender has some issue with reading the  shapenet ".obj" files directly, so it was converted to GTLF format using the ConvertShapeNet.py script supplied. See [https://github.com/CesiumGS/obj2gltf](https://github.com/CesiumGS/obj2gltf)
2) HDRI backgrounds were downloaded from [HdriHaven](https://hdrihaven.com/)
3) PBR materials textures were downloaded from [cc0textures](https://cc0textures.com/)

The dataset Created using this script can be download:[Full Dataset 1](https://e.pcloud.link/publink/show?code=kZfx55Zx1GOrl4aUwXDrifAHUPSt7QUAIfV),  [Full DataSet Link2](https://icedrive.net/1/6cZbP5dkNG), [Subset](https://zenodo.org/record/5508261#.YUGsd3tE1H4)

![](/Figure1.jpg)
![](/VesselWithContent_Frame_0_RGB.jpg)

