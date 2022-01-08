# Load assign and generate materials (PBR/BSDF)

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
#####################################################################################3

# Random multiply

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r


###############################################################################################################################

###################################################################################################################################

# Transform BSDF Mateiral to dictionary (use to save materials properties)

####################################################################################################################################
def BSDFMaterialToDictionary(Mtr):
    bsdf=Mtr.node_tree.nodes["Principled BSDF"]
    dic={}
    dic["TYPE"]="Principled BSDF"
    dic["Name"]=Mtr.name
    dic["Base Color"]=(bsdf.inputs[0].default_value)[:]## = (0.0892693, 0.0446506, 0.137255, 1)
    dic["Subsurface"]=bsdf.inputs[1].default_value## = 0
    dic["Subsurface Radius"]=str(bsdf.inputs[2].default_value[:])
    dic["Subsurface Color"]=bsdf.inputs[3].default_value[:]# = (0.8, 0.642313, 0.521388, 1)
    dic["Metalic"]=bsdf.inputs[6].default_value# = 5
    dic["Specular"]=bsdf.inputs[7].default_value# = 0.804545
    dic["Specular Tint"]=bsdf.inputs[8].default_value# = 0.268182
    dic["Roughness"]=bsdf.inputs[9].default_value# = 0.64
    dic["Anisotropic"]=bsdf.inputs[10].default_value# = 0.15
    dic["Anisotropic Rotation"]=bsdf.inputs[11].default_value# = 0.236364
    dic["Sheen"]=bsdf.inputs[12].default_value# = 0.304545
    dic["Sheen tint"]=bsdf.inputs[13].default_value# = 0.304545
    dic["Clear Coat"]=bsdf.inputs[14].default_value# = 0.0136364
    dic["Clear Coat Roguhness"]=bsdf.inputs[15].default_value #= 0.0136364
    dic["IOR"]=bsdf.inputs[16].default_value# = 3.85
    dic["Transmission"]=bsdf.inputs[17].default_value# = 0.486364
    dic["Transmission Roguhness"]=bsdf.inputs[18].default_value# = 0.177273
    dic["Emission"]=bsdf.inputs[19].default_value[:]# = (0.170604, 0.150816, 0.220022, 1)
    dic["Emission Strengh"]=bsdf.inputs[20].default_value
    dic["Alpha"]=bsdf.inputs[21].default_value
   # dic["bsdf Blender"]=bsdf.inputs
    return dic

###################################################################################################################################

# Transform glosst transparent Mateiral to dictionary (use to save materials properties)

####################################################################################################################################
def GlassMaterialToDictionary(Mtr):
    print("Creating glass material dictionary")
    GlassBSDF = bpy.data.materials["TransparentLiquidMaterial"].node_tree.nodes["Glass BSDF"]
    VolumeAbsorbtion = bpy.data.materials["TransparentLiquidMaterial"].node_tree.nodes["Volume Absorption"]
    dic={}
    dic["TYPE"]="Glass Transparent"
    dic["Name"]=Mtr.name
    dic["Distribution"]=GlassBSDF.distribution# = 'BECKMANN'
    dic["Base Color"]=GlassBSDF.inputs[0].default_value[:]# = (1, 0.327541, 0.225648, 1)
    dic["Roughness"]=GlassBSDF.inputs[1].default_value
    dic["IOR"]=GlassBSDF.inputs[2].default_value
    
    dic["VolumeAbsorbtion Color"]=VolumeAbsorbtion.inputs[0].default_value[:]# = (1, 0.668496, 0.799081, 1)
    dic["Density"]=VolumeAbsorbtion.inputs[1].default_value
    
#    dic["GLASS bsdf Blender"] = GlassBSDF
 #   dic["VolumeAbsorbtion Blender"] = VolumeAbsorbtion
    return dic
###############################################################################################################################

##            #Assing  random tansperent material to vessel material ( assume material already exists in the blend file)

###############################################################################################################################
def AssignMaterialToVessel(name):  
  
    print("================= Assign material to vessel "+name+"=========================================================")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
#------------------------Assing material node to vessel----------------------------------------------------------
    if np.random.rand()<10.8:
       bpy.data.objects[name].data.materials.append(bpy.data.materials['Glass'])
   
#-----------Set random properties for material-----------------------------------------------------
    if np.random.rand()<0.02: # Color
        bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand())
    else:
        rnd=1-np.random.rand()*0.3
        bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (rnd, rnd, rnd, rnd)

    bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[3].default_value = bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[0].default_value 


    if np.random.rand()<0.1: # Subsurface
        bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[1].default_value = np.random.rand()
    else:
        bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[1].default_value = 0
   
    if np.random.rand()<0.15: #Transmission
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[17].default_value = 1-0.2*RandPow(3) # Transmission
    else:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[17].default_value = 1 #Transmission
       
       
    if np.random.rand()<0.2: # Roughnesss
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0.2*RandPow(3) # Roughness
    else: 
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0# Roughness
  
 
   
       
    if np.random.rand()<0.6:# ior index refraction
         bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 1.45+np.random.rand()*0.55 #ior index of reflection for transparen objects  
    
    else:
        bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 1.415+np.random.rand()*0.115 #ior index of reflection for transparen objects  
    #https://pixelandpoly.com/ior.html

     

    if np.random.rand()<0.12: # Metalic
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[6].default_value = 0.3*RandPow(3)# metalic
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[6].default_value =0# meralic
      
      
    if np.random.rand()<0.12: # specular
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = np.random.rand()# specular
    elif np.random.rand()<0.6:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value =0.5# specular
    else:
      ior=bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value# specular
      specular=((ior-1)/(ior+1))**2/0.08
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value=specular
      
    if np.random.rand()<0.12: # specular tint
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[8].default_value = np.random.rand()# tint specular
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[8].default_value =0.0# specular tint
  
    if np.random.rand()<0.12: # anisotropic
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[10].default_value = np.random.rand()# unisotropic
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[10].default_value =0.0# unisotropic
  
    if np.random.rand()<0.12: # anisotropic rotation
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[11].default_value = np.random.rand()# unisotropic rotation
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[11].default_value =0.0# unisotropic
    
    if np.random.rand()<0.6: #Transmission Roughness
         bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0.25*RandPow(3) # transmission rouighness
    else:
         bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0 # transmission rouighness
    
      
    if np.random.rand()<0.1: # Clear  coat
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = np.random.rand()
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value =0# 

    if np.random.rand()<0.1: # Clear  coat
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = np.random.rand()
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value =0.03# 
    bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[12].default_value = 0 # Sheen 
    bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[13].default_value = 0.5 # Sheen tint
    bpy.data.materials["BSDFMaterial"].node_tree.nodes["Principled BSDF"].inputs[19].default_value = (0, 0, 0, 1) # Emission
    bpy.data.materials["BSDFMaterial"].node_tree.nodes["Principled BSDF"].inputs[20].default_value = 0 # Emission stength
    bpy.data.materials["BSDFMaterial"].node_tree.nodes["Principled BSDF"].inputs[21].default_value = 1 # alpha


    return BSDFMaterialToDictionary(bpy.data.materials["Glass"]) # turn material propeties into dictionary (for saving)

#############################################################################################################################################

#                       Assign  bsdf Material for object and set random properties (assume material already exist in the blend file)

#############################################################################################################################################
def AssignMaterialBSDFtoObject(ObjectName, MaterialName):  
    
    

    print("================= Assign bsdf material to object "+ObjectName+" Material "+MaterialName+"=========================================================")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[ObjectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[ObjectName] 
     # Basically pick existing node and assign it to the material and set random properties (this will not work if the node doesnt already exist)          

#-------------------------------Add BSDF material to object============================================
  
    print(bpy.data.objects[ObjectName].data.materials)
    if len(bpy.data.objects[ObjectName].data.materials)==0:
         bpy.data.objects[ObjectName].data.materials.append(bpy.data.materials[MaterialName])
    else: # if object already have material replace them
         for i in range(len(bpy.data.objects[ObjectName].data.materials)):
                bpy.data.objects[ObjectName].data.materials[i]=bpy.data.materials[MaterialName]
           
        

# ----------------------------------Select random property for material --------------------------------------------------------------------------------------      
      
    if np.random.rand()<0.9:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[17].default_value = np.random.rand() # Transmission
    else:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[17].default_value = 1 #Transmission
    if np.random.rand()<0.8:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[9].default_value = np.random.rand()*np.random.rand()# Roughness
    else: 
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0# Roughness

    if np.random.rand()<0.9: # color
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1) # random color hsv
    else:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1,1, 1) # white color
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[6].default_value = np.random.rand() # metalic
    elif np.random.rand()<0.7:
      bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[6].default_value =0# metalic
    else:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[6].default_value =1# metalic
    if np.random.rand()<0.12: # specular
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = np.random.rand()# specular
    elif np.random.rand()<0.6:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value =0.5# specular
    else:
      ior=bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value# specular
      specular=((ior-1)/(ior+1))**2/0.08
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value=specular
      
    if np.random.rand()<0.12: # specular tint
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[8].default_value = np.random.rand()# tint specular
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[8].default_value =0.0# specular tint

    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[10].default_value = np.random.rand()# unisotropic
    else:
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[10].default_value = 0# unisotropic
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[11].default_value = np.random.rand()# unisotropic rotation
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[11].default_value = 0# unisotropic rotation
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[12].default_value = np.random.rand()# sheen
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[12].default_value = 0# sheen
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[13].default_value = np.random.rand()# sheen tint
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[13].default_value = 0.5# sheen tint
    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[14].default_value =0 #Clear Coat
    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 0.03# Clear coat
 
  
    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 1+np.random.rand()*2.5 #ior index of reflection for transparen objects  
    #https://pixelandpoly.com/ior.html
    
    
    if np.random.rand()<0.2:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[18].default_value = np.random.rand()**2*0.4# transmission rouighness
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0 # transmission rouighness
    
    if np.random.rand()<0.02: # Emission
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[19].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1)# Emission
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[20].default_value = (np.random.rand()**2)*100 # emission strengh
    else: 
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[19].default_value = (0, 0,0, 1)## transmission rouighness
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[20].default_value = 0# Transmission strengh
      
    bpy.context.object.active_material.use_screen_refraction = True
    return BSDFMaterialToDictionary(bpy.data.materials[MaterialName])
##############################################################################################################

#                                    Assign tranparent material to object

######################################################################################################

def AssignTransparentMaterial(ObjectName="LiquidDomain", MaterialName="TransparentLiquidMaterial"):
    print("================= Assign transparent material to object "+ObjectName+" Material "+MaterialName+"=========================================================")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[ObjectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[ObjectName] 
     # Basically pick existing node and assign it to the material and set random properties (this will not work if the node doesnt already exist)          
  #  if len(bpy.data.objects["Vessel"].data.materials)==0:

    #bpy.data.objects[ObjectName].data.materials.append(bpy.data.materials[MaterialName])
    if len(bpy.data.objects[ObjectName].data.materials)==0:
         bpy.data.objects[ObjectName].data.materials.append(bpy.data.materials[MaterialName])
    else: # if object already have material replace them
         for i in range(len(bpy.data.objects[ObjectName].data.materials)):
                bpy.data.objects[ObjectName].data.materials[i]=bpy.data.materials[MaterialName]
           

# ----------------------------------Select random property for material
#    #bpy.ops.object.modifier_add(type='SUBSURF')
      # Color  
    if np.random.rand()<0.5:
            Color= (np.random.rand(), np.random.rand(), np.random.rand(), 1)
    else:
            Color= (1, 1, 1, 1)
    bpy.data.materials[ MaterialName].node_tree.nodes["Volume Absorption"].inputs[0].default_value = Color
    bpy.data.materials[ MaterialName].node_tree.nodes["Glass BSDF"].inputs[0].default_value = Color
    if np.random.rand()<0.5: #Roughnress
         bpy.data.materials[MaterialName].node_tree.nodes["Glass BSDF"].inputs[1].default_value=0
    else:
         bpy.data.materials[MaterialName].node_tree.nodes["Glass BSDF"].inputs[1].default_value = 0.2*np.random.rand() # roughness
    #IOR
    bpy.data.materials[MaterialName].node_tree.nodes["Glass BSDF"].inputs[2].default_value = 1+np.random.rand()*1.2
    # Density
    bpy.data.materials[MaterialName].node_tree.nodes["Volume Absorption"].inputs[1].default_value = 0.5+np.random.rand()

    return GlassMaterialToDictionary(bpy.data.materials[MaterialName])
#############################################################################################################################################################

#               Assign a random PBR material into object

#########################################################################################################################################################################
def AssignPBRMaterialForObject(name,PbrMainDir):
    print("-------------------Assigning pbr materials to object------------------------------------")
    bpy.data.objects[name].data.materials.append(bpy.data.materials['PbrMaterial'])
    
    bpy.data.materials['PbrMaterial'].cycles.displacement_method = 'BOTH'
  
    ##############################Add displacement to make the ground not flat######################################################
 
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Displacement"].inputs[2].default_value =  1#np.random.rand()*10 # The scale of the displacemnrn
    if np.random.rand()<0.5: # This will add topolgy/displacement but only if cycle/experimental rendring is active
       bpy.ops.object.modifier_add(type='SUBSURF')
       bpy.context.object.modifiers["Subdivision"].render_levels = bpy.context.object.modifiers["Subdivision"].levels =np.random.randint(8)+1
    #-------------------------------------------------------------------------------------------
    #                   Select random material from the PbrDir for the ground
    #--------------------------------------------------------------------------------------------

    AllPbrDirs=[]
    for sdir in os.listdir(PbrMainDir):
        if os.path.isdir(PbrMainDir+"/"+sdir): AllPbrDirs.append(PbrMainDir+"/"+sdir)
        print(PbrMainDir+"/"+sdir)

    PbrDir=AllPbrDirs[np.random.randint(len(AllPbrDirs))]
#    print(PbrMainDir+"/black.jpg")
   # bpy.ops.image.open(filepath=PbrMainDir+"/black.jpg", directory=PbrMainDir, files=[{"name":"black.jpg", "name":"black.jpg"}], show_multiview=False)
 #   bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.004"].image=bpy.data.images["black.jpg"]

    for Fname in os.listdir(PbrDir):
       if ("olor." in Fname)  or ("COLOR." in Fname) or ("ao." in Fname)  or ("AO." in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.001"].image=bpy.data.images[Fname]
          print("Color "+ Fname)
       if ("oughness." in Fname) or ("ROUGH." in Fname) or ("roughness" in Fname) or ("ROUGHNESS" in Fname) or ("roughnness" in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.002"].image=bpy.data.images[Fname]
          print("Roughness "+ Fname)
       if ("ormal." in Fname)  or ("NORM." in Fname) or ("normal" in Fname)  or ("NORMAL" in Fname) or ("Normal" in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.003"].image=bpy.data.images[Fname]
          print("Normal "+ Fname)
       if ("eight." in Fname) or ("DISP." in Fname) or ("height" in Fname) or ("displacement" in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture"].image=bpy.data.images[Fname]
          print("Height "+ Fname)
       if ("etallic." in Fname) or ("etalness." in Fname)  or ("etal." in Fname) or ("etalic." in Fname) :
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.004"].image=bpy.data.images[Fname]
          print("Metallic "+ Fname)
    Sc=np.random.rand()*2+0.2 #Scale
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Mapping"].inputs[3].default_value[0] = Sc 
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Mapping"].inputs[3].default_value[1] = Sc
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Mapping"].inputs[3].default_value[2] = Sc

##################################################################################################

# Replace pbr materials by bsdf materials (this is solve the problem of normals in PBR materials which can be very bad)

#####################################################################################################  
def ReplacePBRbyBSDFMaterials(Inverse=False):
    for obj in bpy.data.objects:
        if obj.type=='MESH':
            for f,mt in enumerate(obj.data.materials):
                if Inverse and mt.name=="PBRReplacement":
                       obj.data.materials[f]=bpy.data.materials["PbrMaterial"]
                if not Inverse and mt.name=="PbrMaterial":
                       obj.data.materials[f]=bpy.data.materials["PBRReplacement"]
     
       
#################################################################################################     
