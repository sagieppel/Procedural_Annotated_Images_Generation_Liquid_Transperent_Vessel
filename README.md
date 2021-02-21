# Procedural_Annotated_Images_Generation_Liquid_Transperent_Vessel
#Description: This script will procedurally generate images of randomly shaped  transparent vessel with simulated liquid of random material, and random background
#  This will be used to generate images that will be saved. This script will generate multiple images in multiple simulation


#Where to start: Best place to start is in the “Main” section in the last part of this script

#What needed:  Folder of HDRI and a folder  of pbr materials (Example folders are available in this script folder as: HDRI_BackGround, PBRMaterials

# How to use: 
Go to “main” section in the end of this file, in “input parameter” subsection
1) set Path to OutFolder where generated images should be saved
2) Set Path HDRI_BackGroundFolder which contain background HDRI (for start use the example HDRI_BackGround, supplied in this script folder)
3) Set Path to PBRMaterialsFolder to the folder contain PBR materials (for start use the example PBRMaterials folder supplied in this script folder)
4) Run script images should start appearing in the OutFolder  after few minutes (depending on rendering file)

# Notes:
1) Try to avoid relative paths Blender is not very good with those.
2) Running this script should paralyze blender until the script is done which can take a while
3) The script refers to materials nodes and will only run as part of the blender file
4) If you want to run script as stand alone without blender file, go to “Main” section and disable all the "assign material" functions
5) If you want to run script as stand alone without blender file or supporting Hdri and Pbr folders, go to main and disable all the "assign material" functions and also the "set background" function
6) This was run on ubuntu 20 with blender 2.91 (still crashes sometimes probably due memory problems)

# Running without Simulating liquids
For running the script withou generating and simulating liquids delete the following lines in the main section.
 CreateDomainCube(name="LiquidDomain",scale=(MaxXY*2, MaxXY*2, MaxZ*2)) 
 
 AssignMaterialToLiquid("LiquidDomain") 
 
 TurnToLiquid("Content") 
 
 TurnToEffector("Vessel") 
 
 TurnToDoman ...

# Running without producing Depth and Surface Normals
To prevent outputting EXR files for Depth and Surface Normals, simply set the `depth_normal_render` parameter in the `RenderImageAndSave(...)` method to False

For example: 
`RenderImageAndSave(FileNamePrefix,FramesToRender,OutputFolder,depth_normal_render = False)`

 
# ToDo:
1) Depth maps
2) Increase variability of materials add: smoke, suspension, powder, multiphase..
3) Add background objects and light source
4) Change camera angles

![](/GeneratedImages4.jpg)
![](/GeneratedImages2.jpg)

