


## Description:
# This script will procedurally generate images of randomly shaped transparent vessels with random objects or simulated liquid inside the vessel. 

#Images, Depth maps, Normal maps, and material properties will be saved to the output folder. Images of the vessel content without vessel and vessel without content will also be saved. 


#### This was run with Blender 3.0 with no additional add-ons

### Where to start: 
#The best place to start is in the “Main” section in the last part of this script.

### What needed:  
#Objects Folder, HDRI background folder, and a folder of PBR materials (Example folders are supplied as: “HDRI_BackGround”, “PBRMaterials”, and “Objects”)

## How to use:
#1) Go to the “Main” section of the python script, in the “input parameter” subsection.
#2) In the "OutFolder" parameter set path to where the generated images should be saved.
#3) Set Path HDRI_BackGroundFolder," parameter set path to where the background HDRI (for a start, use the example HDRI_BackGround, supplied)
#4) In the "PBRMaterialsFolder" parameter set path to where the PBR materials (for a start, use the example PBRMaterials folder supplied)
#5) In the "ObjectsFolder" parameter, set the path to where the objects file are saved (for a start, use the example object folder supplied).
#6) Run the script from Blender or run the script from the command line using: "blender DatasetGeneration.blend -b -P DatasetGeneration.py"
#Images should start appearing in the OutFolder after few minutes (depending on the rendering file). 
#Note that while running, Blender will be paralyzed.

## Additional parameters 
#(in the “Input parameters” of "Main" python script  (near the end of this file)
#"NumSimulationsToRun" determines how many different environments to render into images (How many different images will be created).
# ContentMode  Will determine the type of content that will be generated insid the vessel 
#"Liquid": liquid simulation inside the vessel (simulation can be time consuming)
#"Objects":   objects inside the vessel (objects will be taken from the Objects folder)
#"FlatLiquid": will create simple liquid with flat surface that fill the bottum of the vessel (no liquid simulation will be performed)

## Once finished you need to use VirtualDataSetEditCleanAndAddMasks.py to on the output to actually generated the segmentation mask (this can run from any python)
###############################Dependcies######################################################################################3

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import json
import sys
filepath = bpy.data.filepath
directory = os.path.dirname(filepath)
#sys.path.append("/home/breakeroftime/Desktop/Simulations/ModularVesselContent")
sys.path.append(directory)
os.chdir(directory)
import VesselGeneration as VesselGen
import LiquidSimulation as LiquidSim
import MaterialsHandling as Materials
import ObjectsHandling as Objects
import RenderingAndSaving as RenderSave
import SetScene

################################################################################################################################################################

#                                    Main 

###################################################################################################################################################################
# generate scence with random vessel containing either a fluid or an object inside it and save to file

#------------------------Input parameters---------------------------------------------------------------------

# Example HDRI_BackGroundFolder and PBRMaterialsFolder  and ObjectsFolder folders should be in the same folder as the script. 
# Recomand nto use absolute and not relative paths  as blender is not good with these

HDRI_BackGroundFolder=r"HDRI_BackGround/" # Background Hdri folder
PBRMaterialsFolder=r"PBRMaterials/"#PBR materials folder
ObjectFolder=r"Objects/"  #Folder of objects that will be used for background 
OutFolder=r"Output/"# Where output images will be saved



#HDRI_BackGroundFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/4k/" # Background dri folder
#PBRMaterialsFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/2K_PBR/"
#ObjectFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/ObjectGTLF/" #Folder of objects that will be used for background 
#OutFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/LiquidFlatSurface_Blender3/"# Where output images will be saved








NumSimulationsToRun=100000000000              # Number of simulation to run

ContentMode= "Objects" # "Objects","Liquid" # Type of content that will be generated insid the vessel 
# "Liquid": liquid simulation inside the vessel
# "Objects":   objects inside the vessel
#"FlatLiquid": will create simple liquid with flat surface that fill the bottum of the vessel (no liquid simulation will be performed)

SaveObjects=True # Do you want to save vessel and content as objects, some of these filese can  be large
#==============Liquid simulation parameters==============================================================
SurfaceDisance=0.39 # Will also create buffer layer between vessel and wall that will reduce realisim, but will reduce leaks of liquids trough vessel surface  
MaxSubDivisionResolution=65
MinSubDivisionResolution=64

MaxTimeStep=18 # To Avoid leaking
MinTimeStep=4 # Avoid leaking and improve precision

#==============Set Rendering engine parameters (for image creaion)==========================================

bpy.context.scene.render.engine = 'CYCLES' # Use this configuration if you want to be able to see the content of the vessel (eve does not support content)
#bpy.context.scene.cycles.device = 'GPU'
#bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL' # Not sure if this is really necessary but might help with sum surface textures
bpy.context.scene.cycles.samples = 120 #200, #900 # This work well for rtx 3090 for weaker hardware this can take lots of time
bpy.context.scene.cycles.preview_samples = 900 # This work well for rtx 3090 for weaker hardware this can take lots of time

bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 900

bpy.context.scene.eevee.use_ssr = True
bpy.context.scene.eevee.use_ssr_refraction = True
bpy.context.scene.cycles.caustics_refractive=True
bpy.context.scene.cycles.caustics_reflective=True
bpy.context.scene.cycles.use_preview_denoising = True
bpy.context.scene.cycles.use_denoising = True

MaterialList=["PbrMaterial","TransparentLiquidMaterial","BSDFMaterial","BSDFMaterialLiquid","Glass","PBRReplacement"] # Materials that will be used

#-------------------------Create delete folders--------------------------------------------------------------

#CountFolder=OutFolder+"/count/" # Folder for remembring image numbers (for restarting script without over running existing files)
CatcheFolder=OutFolder+"//Temp_cache//" # folder where liquid simulation will be saved (this will be deleted every simulation
if not os.path.exists(OutFolder): os.mkdir(OutFolder)

#----------------------------Create list of Objects that will be loaded during the simulation---------------------------------------------------------------
ObjectList={}
if os.path.isdir(ObjectFolder):
    ObjectList=Objects.CreateObjectList(ObjectFolder)

#----------------------------------------------------------------------

for cnt in range(1000000000000000000):
    
    print("Add material")
    SubDivResolution=MinSubDivisionResolution+np.random.randint(MaxSubDivisionResolution-MinSubDivisionResolution)
    if np.random.rand()<0.1: SubDivResolution=MaxSubDivisionResolution
    TimeStep=MinTimeStep+np.random.randint(MaxTimeStep-MinTimeStep) 
    if np.random.rand()<0.2: TimeStep=MinTimeStep
    
    
    if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation folder to free space
    if NumSimulationsToRun==0: break
    OutputFolder=OutFolder+"/"+str(cnt)
    if  os.path.exists(OutputFolder): continue # Dont over run existing folder continue from where you started
    os.mkdir(OutputFolder) 
    NumSimulationsToRun-=1

    ContentMaterial={"TYPE":"NONE"}

#    #================================Run simulation and rendering=============================================================================
    print("=========================Start====================================")
    print("Simulation number:"+str(cnt)+" Remaining:"+ str(NumSimulationsToRun))
    SetScene.CleanScene()  # Delete all objects in scence
  
#    #------------------------------Create random vessel object and assign  material to it---------------------------------
    MaxXY,MaxZ,MinZ,VesselWallThikness=VesselGen.AddVessel("Vessel","Content",ScaleFactor=1, SimpleLiquid=(ContentMode=="FlatLiquid")) # Create Vessel object named "Vessel" and add to scene also create mesh inside the vessel ("Content) which will be transformed to liquid
    VesselMaterial=Materials.AssignMaterialToVessel("Vessel") # assign random material to vessel object
    
   #-------------------------------------------Create ground plane and assign materials to it----------------------------------
    if np.random.rand()<0.8:
        PlaneSx,PlaneSy= SetScene.AddGroundPlane("Ground",x0=0,y0=0,z0=-VesselWallThikness*(np.random.rand()*0.75+0.25)-0.1,sx=MaxXY,sy=MaxXY) # Add plane for ground
        if np.random.rand()<0.95:
            Materials.AssignPBRMaterialForObject("Ground",PBRMaterialsFolder) # Assign PBR material to ground plane (Physics based material) from PBRMaterialsFolder
        else: 
            Materials.AssignMaterialBSDFtoObject(ObjectName="Ground",MaterialName="BSDFMaterial") 
    else: 
        with open(OutputFolder+'/NoGroundPlane.txt', 'w'): print("No Ground Plane")
        PlaneSx,PlaneSy=MaxXY*(np.random.rand()*4+2), MaxXY*(np.random.rand()*4+2)
#------------------------Load background hdri---------------------------------------------------------------   
    SetScene.AddBackground(HDRI_BackGroundFolder) # Add randonm Background hdri from hdri folder

#..............................Create load objects into scene background....................................................
    Objects.LoadNObjectsToScene(ObjectList,AvoidPos=[0,0,0],AvoidRad=MaxXY,NumObjects=np.random.randint(11),MnPos=[-PlaneSx,-PlaneSy,-5],MxPos=[PlaneSx,PlaneSy,0],MnScale=(np.random.rand()*0.8+0.2)*MaxXY,MxScale=np.max([MaxXY,MaxZ])*(1+np.random.rand()*4))    

##################################Create vessel content could be a liquid or object##########################################
   
    if  ContentMode=="FlatLiquid": # mesh that fill the bottum part of the vessel with flat surface, kind of a liquid in a glass, no liquid simulation will be performed
           if np.random.rand()<0.35:
              ContentMaterial=Materials.AssignMaterialBSDFtoObject(ObjectName="Content", MaterialName="BSDFMaterialLiquid")  # assign material to liquid
           else: 
              ContentMaterial=Materials.AssignTransparentMaterial(ObjectName="Content", MaterialName="TransparentLiquidMaterial") #Assign material for the object domain (basically the material of the liquid)
          
           ContentNames=["Content"] # names of all meshes/objects inside vessels
           FramesToRender=[0]  # Frames in the animation to render 
#------------------Put random objects in the vessel-----------------------------------------------------------------
    elif   ContentMode=="Objects":
       
      

            ContentNames=Objects.LoadNObjectsInsideVessel(ObjectList,MaxXY-VesselWallThikness,MinZ,MaxZ,NumObjects=np.random.randint(np.random.randint(8)+1)) # Put random objects in vessel
         
            if  np.random.rand()<0.5:
                if np.random.rand()<0.8:
                     for nm in ContentNames: # names of all meshes/objects inside vessels
                           print(nm)
                           ContentMaterial=Materials.AssignMaterialBSDFtoObject(ObjectName=nm, MaterialName="BSDFMaterialLiquid")  # Assign single bsdf material to all object in the vessel
                else: 
                     for nm in ContentNames: 
                           ContentMaterial=Materials.AssignTransparentMaterial(ObjectName=nm, MaterialName="TransparentLiquidMaterial") # assign transparent material to all object in the vesssel
            FramesToRender=[0] # Frames in the animation to render
            
  
#..............................Create scene with liquid in vessels actually simulate liwuiud.....................................................
    elif    ContentMode=="Liquid":
        ContentNames=["LiquidDomain"] # names of all meshes/objects inside vessels
        LiquidSim.CreateDomainCube(name="LiquidDomain",scale=(MaxXY*2, MaxXY*2, MaxZ)) # Create Cube that will act as liquid domain
        if np.random.rand()<0.5:
              ContentMaterial=Materials.AssignMaterialBSDFtoObject(ObjectName="LiquidDomain", MaterialName="BSDFMaterialLiquid")  # assign material to liquid
        else: 
              ContentMaterial=Materials.AssignTransparentMaterial(ObjectName="LiquidDomain", MaterialName="TransparentLiquidMaterial") #Assign material for the object domain (basically the material of the liquid)
    #    print("Create simulation")
        LiquidSim.TurnToLiquid("Content",VesselThinkness=VesselWallThikness) # Turn Content mesh into liquid
        LiquidSim.TurnToEffector("Vessel",SurfaceDisance) # Turn Vessel into liquid effector (will interact with liquid as solid object)
        LiquidSim.TurnToDoman("LiquidDomain",CatcheFolder=CatcheFolder,Bake=True,EndFrame=151,resolution=SubDivResolution,MaxTimeStep=TimeStep,MinTimeStep=MinTimeStep, Smooth=True) # Turn domain Cube into domain and bake simulation (Time consuming)
        FramesToRender=[30,65,100,150] # Liquid is dynamic so several frames will be rendered
        # Frames in the animation to render
    
#-----------------Save materials properties as json files------------------------------------------------------------
    if not  os.path.exists(OutputFolder): os.mkdir(OutputFolder)
    print("+++++++++++++++++++++Content material++++++++++++++++++++++++++++++")
    print(ContentMaterial)
    if ContentMaterial["TYPE"]!="NONE":
              with open(OutputFolder+'/ContentMaterial.json', 'w') as fp: json.dump(ContentMaterial, fp)
    print("+++++++++++++++++++++vessel material++++++++++++++++++++++++++++++")
    print(VesselMaterial)
    with open(OutputFolder+'/VesselMaterial.json', 'w') as fp: json.dump(VesselMaterial, fp)
    
#....................Delete uneeded parts---------------------------------------------------------------------
    if ContentMode!="FlatLiquid": Objects.DeleteObject("Content") # Delete the liquid  object (The liquid that was generated in the simulation is attached to the LiquidDomain and will not be effected, if you use simple liquid the Content is the liquid and will not be deleted
    Objects.HideObject("VesselOpenning",Hide=True)
    
    
    SetScene.RandomlySetCameraPos(name="Camera",VesWidth = MaxXY,VesHeight = MaxZ)
    with open(OutputFolder+'/CameraParameters.json', 'w') as fp: json.dump( SetScene.CameraParamtersToDictionary(), fp)
    
#------------------------------------------------------Save Objects to file-----------------------------------------------------
    if SaveObjects:
        Objects.ExportObjectAsGTLF("Vessel",OutputFolder+"/Vessel",Frame=0) # Save vessel as object
        for indx, ObjectName in enumerate(ContentNames): # Save Vessel Content as object
              for frm in FramesToRender:
                   Objects.ExportObjectAsGTLF(ObjectName,OutputFolder+"/ContentObject"+str(indx)+"_Frame_"+str(frm),Frame=frm)
#-------------------------------------------------------Save images--------------------------------------------------------------    
   
    print("Saving Images")
    print(OutputFolder)
    RenderSave.RenderImageAndSave(FileNamePrefix="VesselWithContent",FramesToRender=FramesToRender,OutputFolder=OutputFolder) # 
    Objects.HideObject("Vessel",Hide=True)
    RenderSave.RenderImageAndSave(FileNamePrefix="Content",FramesToRender=FramesToRender,OutputFolder=OutputFolder) # Render images and Save vessel content with no vessel
    
    Objects.HideObject("Vessel",Hide=False)
    for nm in ContentNames:  Objects.HideObject(nm,Hide=True)
    RenderSave.RenderImageAndSave(FileNamePrefix="EmptyVessel",FramesToRender=[0],OutputFolder=OutputFolder) # Render images and Save abd scene
    
    Objects.HideObject("Vessel",Hide=True)
    RenderSave.RenderImageAndSave(FileNamePrefix="Plane",FramesToRender=[0],OutputFolder=OutputFolder) # Render images and Save Plane and scene with no vessel or image 
    
    #------------------------Save vessel opening plane----------------------------------------------------------------------------------------------
    # Save Vessel opening
    print("Saving Vessel Opening")
    Objects.HideObject("VesselOpenning",Hide=False)
    objs=[]
    for nm in bpy.data.objects: objs.append(nm)
    for nm in objs: 
        if nm.name!='VesselOpenning' and nm.name!='Camera': 
            bpy.data.objects.remove(nm)
    RenderSave.RenderDepthNormalAndImageToFiles(OutputFolder,"VesselOpening", RenderImage=False,RenderDepth=True,RenderNormal=True)
#------------------------------Finish and clean data--------------------------------------------------
   
    print("Cleaning")

    f=open(OutputFolder+"/Finished.txt","w")
    # Clean images
    imlist=[]
    for nm in bpy.data.images: imlist.append(nm) 
    for nm in imlist:
        bpy.data.images.remove(nm)
    # Clean materials
    mtlist=[]
    for nm in bpy.data.materials: 
        if nm.name not in MaterialList: mtlist.append(nm)
    for nm in mtlist:
        bpy.data.materials.remove(nm)
    if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation catche folder to free space
    print("========================Finished==================================")
