# Description:
 This script will procedurally generate images of randomly shaped transparent vessels with random objects or simulated liquid inside the vessel. 

Images, Depth maps, Normal maps, and material properties will be saved to the output folder. Images of the vessel content without vessel and vessel without content will also be saved. 


### This was run with Blender 2.92 with no additional add-ons

## Where to start: 
The best place to start is in the “Main” section in the last part of this script.

## What needed:  
Objects Folder, HDRI background folder, and a folder of PBR materials (Example folders are supplied as: “HDRI_BackGround”, “PBRMaterials”, and “Objects”)

# How to use:
1) Go to the “Main” section of the python script  (at the end of the script), in the “input parameter” subsection.
2) In the "OutFolder" parameter set path to where the generated images should be saved.
3) Set Path HDRI_BackGroundFolder," parameter set path to where the background HDRI (for a start, use the example HDRI_BackGround, supplied)
4) In the "PBRMaterialsFolder" parameter set path to where the PBR materials (for a start, use the example PBRMaterials folder supplied)
5) In the "ObjectsFolder" parameter, set the path to where the objects file are saved (for a start, use the example object folder supplied).
6) Run the script from Blender or run the script from the command line using: "blender DatasetGeneration.blend -b -P DatasetGeneration.py"
Images should start appearing in the OutFolder after few minutes (depending on the rendering file). 
Note that while running, Blender will be paralyzed.

# Additional parameters 
(in the “Input parameters” of "Main" python script (last section of the script)
"NumSimulationsToRun" determines how many different environments to render into images (How many different images will be created).

There are two generation modes one mode will create liquid inside the vessel, and the other will put random objects inside the vessel. The ratio between the two is controlled by the parameter: "LiquidContentFractionOfCases". Setting this to zero means that only vessels with objects inside them will be generated. Setting this to 1 means that only vessels with liquids inside them will be generated.

SaveObjects parameter: Determine if to save the vessel object and its context as  a 3d model gtlf file. These can be a little big.



# Creating the dataset
Given Blender’s tendency to crash, running this script alone is problematic for large datasets. To avoid the need to restart the program every time Blender crashes, use the shell script RunGeneration.sh. This script will run the blender file in a loop, so it will restart every time Blender crashes. This can be run from shell/cmd: using: sh Run.sh 



# Notes:
1) Try to avoid relative paths; Blender is not very good with those.
2) Running this script should paralyze Blender until the script is done, which can take a while.
3) The script refers to materials nodes and will only run as part of the blender file


# Sources for objects/HDRI/PBR materials
1) Objects were taken from [Shapenet](https://shapenet.org/). Blender has some issue with reading the  shapenet .obj filesdirectly, so it was converted to GTLF format using the ConvertShapeNet.py script supplied. See [https://github.com/CesiumGS/obj2gltf](https://github.com/CesiumGS/obj2gltf)
2) HDRI backgrounds were downloaded from [HdriHaven](https://hdrihaven.com/)
3) PBR materials textures were downloaded from [cc0textures](https://cc0textures.com/)


![](/GeneratedImages4.jpg)
![](/GeneratedImages2.jpg)

