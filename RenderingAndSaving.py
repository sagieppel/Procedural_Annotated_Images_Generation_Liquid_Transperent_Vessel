# Rendering and saving images depth maps and normal maps
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
########################################################################################################

# Render scene as RGB + Depth Map + Normal map

#################################################################################################
def RenderDepthNormalAndImageToFiles(OutputFolder,FileName, RenderImage=True,RenderDepth=True,RenderNormal=True):
    if not os.path.exists(OutputFolder): os.mkdir(OutputFolder)
   # else: print("Warning output folder: "+ OutputFolder+ " Already exists")



    #=========================Get Scene compostion tree=======================================
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    #================remove/clear existing composition node tree======================================
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)
    #===========================Create new composition tree=====================================================
    scene = bpy.context.scene
    scene.render.use_multiview = False  #True # Use stereo
    #scene.render.views_format = 'STEREO_3D'
    r1 = tree.nodes.new(type="CompositorNodeRLayers") # Add node
    composite = tree.nodes.new(type = "CompositorNodeComposite") # Add another node
    composite.location = 200,0 # panel location on the board meaningles

    # Add passes for computing surface normals
    scene.view_layers['View Layer'].use_pass_normal = True
    #scene.render.image_settings.color_depth = '16'


    scene.render.image_settings.file_format = "JPEG"#'OPEN_EXR' # output format
  
    #============Render image=============================================================
    if  RenderImage:
        bpy.context.scene.render.engine = 'CYCLES' # Rendering engine
        links.new(r1.outputs['Image'],composite.inputs['Image']) # link image node to output
        scene = bpy.context.scene  # Initialize scene
        scene.render.use_multiview = False # multiview stereo features #https://docs.blender.org/manual/en/2.79/render/workflows/multiview/usage.html
        scene.render.filepath=OutputFolder+"/"+FileName+"_RGB" # rgb image file name        
        bpy.ops.render.render(write_still=True) # render scene
    #============Render Normal map=============================================================
    
    if  RenderNormal:
        Objects.ReplacePBRbyBSDFMaterials() # PBR material doesnt give good normals replace them
        #scene.render.image_settings.file_format = "PNG"#'OPEN_EXR' # File format
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'  # Rendering engine
        links.new(r1.outputs['Normal'], composite.inputs['Image']) # Link the nORmal mode to the output node
        scene.render.use_multiview = False # Disable  stereo/displacement images 
        scene.view_layers['View Layer'].use_pass_normal = True
        scene.render.filepath=OutputFolder+"/"+FileName+"_Normal" # set save file name
        bpy.ops.render.render(write_still=True) # Save file 
        
        scene.render.image_settings.file_format = 'OPEN_EXR' # File format with higher depth
        scene.render.image_settings.color_depth = '16'#'16'# depth of image (number of bytes)    
        scene.render.filepath=OutputFolder+"/"+FileName+"_Normal" # Save Again as exr
        bpy.ops.render.render(write_still=True) # Save file
        
        Objects.ReplacePBRbyBSDFMaterials(Inverse=True) # Replace back to the original PBR material
    #===========Render Depth EXR Image=============================================================
    if  RenderDepth:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'  # Rendering engine
        scene.render.image_settings.file_format = 'OPEN_EXR' # File format with higher depth
        scene.render.image_settings.color_depth = '32'#'16'# depth of image (number of bytes)    
        scene = bpy.context.scene
        links.new(r1.outputs['Depth'],composite.inputs['Image']) # link depth node to vfile output node
        scene.render.use_multiview = False # Disable  stereo/displacement images 
        scene.render.filepath = OutputFolder+"/"+FileName+"_Depth" # set depth file path
        bpy.ops.render.render(write_still=True) # save depth file

###############################################################################################################   
############################################################################################################

#                 Render image and save to file

###########################################################################################
def RenderImageAndSave(FileNamePrefix,FramesToRender,OutputFolder):
    if not os.path.exists(OutputFolder): os.mkdir(OutputFolder)
    else: print("Warining output folder: "+ OutputFolder+ " Already exists")
    #================set render  need to be done once======================================
  #  bpy.ops.object.select_all(action="DESELECT")
    render=bpy.context.scene.render
    #==================go over Selected frames========================================================
    for k in FramesToRender:
        bpy.context.scene.frame_set(k)
        #============Render image+depth map + normal=============================================================
        RenderDepthNormalAndImageToFiles(OutputFolder,FileNamePrefix+"_Frame_"+str(k)) # render scene
#        render.filepath=OutputFolder+"/"+FileNamePrefix+"_Frame_"+str(k)+".jpg"
#        
#        bpy.ops.render.render(write_still=True)
        print(OutputFolder+"/"+FileNamePrefix+"_Frame_"+str(k)+" Saved")

