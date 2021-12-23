# Loading resizing and positioning of objects (mainly in GTLF format) not include Vessel objects 
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
#####################################################################################3

# Random multiply

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r

 
#######################################################################################################3

#                        Load object and resize and postion in xyz and scale to rad scale

#############################################################################################################
#############################################################################################################
def LoadObject(xyz,RadScale,ObjDir,ObjFileName): #   
      #===========================load object file============================
    print("============Importing object "+ObjDir+"/"+ObjFileName+"=================")
    NameList=[]
    for ob  in bpy.data.objects: NameList.append(ob.name)
    if ".dae" in ObjFileName[-5:]:
        bpy.ops.wm.collada_import(filepath=ObjDir+"/"+ObjFileName)
    elif ".fbx" in ObjFileName[-5:]:
        bpy.ops.import_scene.fbx( filepath = ObjDir+"/"+ObjFileName)
    elif ".obj" in ObjFileName[-5:]:
        bpy.ops.import_scene.obj(filepath=ObjDir+"/"+ObjFileName)
    elif (".gltf" in ObjFileName[-6:]) or (".glb" in ObjFileName[-5:]):
        bpy.ops.import_scene.gltf(filepath=ObjDir+"/"+ObjFileName)
    Name=""    
 #=============Delete none mesh object that was loaded=================================================  
    bpy.ops.object.select_all(action="DESELECT")
    for ob1  in bpy.data.objects:
        ob1.select_set(False)    
        if (ob1.name not in NameList) and (ob1.type != 'MESH'):
                 ob1.select_set(True)    
     
   
    bpy.ops.object.delete()

#=====================Merge all objects that was loaded into one object==================================================    
    for ob1  in bpy.data.objects:
        ob1.select_set(False)
        if (ob1.name not in NameList) and  (ob1.type == 'MESH'):
                 ob1.select_set(True)    
                 bpy.context.view_layer.objects.active = ob1
                 Name=ob1.name
     
    bpy.ops.object.join()
###=============================Find center radius and height======================================.
    Obj=bpy.data.objects[Name]
  
#    Obj.scale=(0,0,0)
    
    bx=[]
    by=[]
    bz=[]

    for ff,vr in enumerate(Obj.bound_box):
        bx.append(vr[0])
        by.append(vr[1])
        bz.append(vr[2])

       # bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(vr[0]*0.3,vr[1]*0.3,vr[2]*0.3), scale=(10, 10, 10))

        
    rz=max(bz)-min(bz)
    ry=max(by)-min(by)
    rx=max(bx)-min(bx)
    cz=sum(bz)/len(bz)
    cy=sum(by)/len(by)
    cx=sum(bx)/len(bx)
    #if ry>rx: r=ry
    r=np.max([rx,ry,rz])
  
    Obj.rotation_euler=(0,0,0)    
    #===================Set object center to object center of mass====================================
        # store the location of current 3d cursor
    saved_location =  bpy.context.scene.cursor.location  # returns a vector

    # give 3dcursor new coordinates
    bpy.context.scene.cursor.location = (cx,cy,cz)

    # set the origin on the current object to the 3dcursor location
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    # set 3dcursor location back to the stored location
    bpy.context.scene.cursor.location = saved_location


    #bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=ry*2, enter_editmode=False, location=(cx, cz,cy))
    ##################Scale object to feet inside the cylinder################################
    Rat=RadScale/r #np.min([CR/r,CH/rz])#*(1-0.8*np.random.rand()**2)
    Obj.scale=(Rat,Rat,Rat)
    Obj.location=(xyz[0],xyz[1],xyz[2]+r*Rat/2*np.random.rand())#(-cx*Rat,-cy*Rat,-cz*Rat)
#    Obj.rotation_euler=(np.random.rand()*6.28,np.random.rand()*6.28,np.random.rand()*6.28)  
   
# ======================Apply random rotation======================
    for i in range(3):
       bpy.context.object.rotation_quaternion[i] =np.random.rand()*6.2831853

    return Obj.name

##########################################################################################

# Merge List of objects into one object

###########################################################################################
def  MergeObjects(ObjectNames,FinalName):
    bpy.ops.object.select_all(action="DESELECT")
    Name="NO_OBJECTS"
    for ob1  in bpy.data.objects:
        ob1.select_set(False)
        if (ob1.name in ObjectNames) and  (ob1.type == 'MESH'):
                 ob1.select_set(True)    
                 bpy.context.view_layer.objects.active = ob1
                 Name=ob1.name
    if Name!="NO_OBJECTS":
        bpy.ops.object.join()
        bpy.data.objects[Name].name=FinalName
        return [FinalName] # list have objects inside
    else: 
        return []  # list is empty



########################################################################################

#     Create object list for objects file in folder  for obj and dae 

###########################################################################################
def CreateObjectListDaeObj(MainObjectDir):
    ObjectList={} # list of object file names and folder
    for dr in os.listdir(MainObjectDir):
        
        ObjDir=MainObjectDir+"/"+dr
        if not os.path.isdir(ObjDir): continue
        #print(dr)
        for nm in os.listdir(ObjDir):
                if  (".obj" in nm)  or  (".dae" in nm):
                      ObjectList[nm]=ObjDir
                    #  break
         #             print(nm)
    print("================Object List================================")
    print(ObjectList)
    
    return ObjectList                    

########################################################################################

#   Create object list for objects files  in folder fbx//gtlf//glb

###########################################################################################
def CreateObjectList(ObjectDir):
    print("=================Making FBX object list=============================")
    ObjectList={} # list of object file names and folder        
    for nm in os.listdir(ObjectDir):
                if os.path.isfile(ObjectDir+"/"+nm) and ((".fbx" in nm) or (".gltf" in nm) or (".glb" in nm)): 
                    
                      ObjectList[nm]=ObjectDir
                    #  break
         #             print(nm)
    print("================Object List================================")
    print(ObjectList)
    
    return ObjectList    


################################################################################################

#        Load  random object from objectlist and put in position xyz and scale to Radscale

################################################################################################
def LoadRandomObject(ObjectList,RadScale,xyz): 
           print("=============Loading random object==========================================")
           ObjFileName=random.choice(list(ObjectList.keys()))
           print(ObjFileName)   
           ObjDir=ObjectList[ObjFileName]
           print(ObjDir)
           return LoadObject(xyz,RadScale,ObjDir,ObjFileName)
################################################################################################

# Set NumObject random object to scene avoiding location in AvoidPos  With radius of AvoidRad
#  object size and postion will be limited by MnScale and MxScale (loaded objects can overlap each other)

###################################################################################################
def LoadNObjectsToScene(ObjectList,AvoidPos,AvoidRad,NumObjects,MnPos,MxPos,MnScale,MxScale):
    print("==================Set "+str(NumObjects)+" objects in given region in image in radnom scale and postions=================")
    for i in range(NumObjects):
       
       while (True):
           RadScale=MnScale+np.random.rand()*(MxScale-MnScale)
           xyz=[0,0,0]
           dst=0
           for k in range(len(xyz)):
               xyz[k]=MnPos[k]+np.random.rand()*(MxPos[k]-MnPos[k])
               dst+=(xyz[k]-AvoidPos[k])**2
           print("RadScale"+str(RadScale))
           print("dst"+str(dst))
           print("Avoid"+str(AvoidRad))
           print("rad+scale"+str((AvoidRad+RadScale)**2))
           if dst>(AvoidRad+RadScale)**2: 
                 break
       LoadRandomObject(ObjectList,RadScale,xyz)
    
######################################################################################################
################################################################################################

# Set NumObjects random object to scene inside vessel
# The objects will be limited to x=0, y=0 with Minz and MaxZ position + and to radius R

###################################################################################################
def LoadNObjectsInsideVessel(ObjectList,R,MinZ,MaxZ,NumObjects):

    print("==================Set N objects inside Vessel=================")
    ContentNames=[]
    for i in range(NumObjects):
    
       RadScale=R/4+np.random.rand()*R*3/4
       xyz=[0,0,0]
       dst=0
       xyz[2] = MinZ+np.random.rand()*((MaxZ-MinZ)-RadScale/2)  #MinZ+np.random.rand()*(MaxZ-MinZ)-RadScale/2
       xyz[1]=2*(R-RadScale)*np.random.rand()-(R-RadScale)
       xyz[0]=2*(R-RadScale)*np.random.rand()-(R-RadScale)
       ContentNames.append(LoadRandomObject(ObjectList,RadScale,xyz))
       
       
    ContentNames=MergeObjects(ContentNames,"MeshInsideVessel") # Merge all objects in the vessel into one object

    return ContentNames
###############################################################################################################################

#####################################Hide object from view (doesnt work )############################################################### 

###############################################################################################################################
def HideObject(name,Hide=True): # Doesnt work Hide object *use this after making all the changes to the object. Hidden object cannot be selected or modified
     print("================= Hiding object "+name+"=========================================================") 

     bpy.ops.object.select_all(action="DESELECT")
     bpy.data.objects[name].select_set(True)
     bpy.context.view_layer.objects.active = bpy.data.objects[name]
  #   print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
#     print(bpy.context.view_layer.objects.active)
#     print("llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll")
     print("HIDING "+ name)
     bpy.context.object.hide_viewport = Hide
     bpy.context.object.hide_render = Hide
     bpy.context.object.hide_set(Hide)
     
#     if Hide: 
#          for i in range(3): bpy.context.object.location[0] += 1000
#     else:
#          for i in range(3): bpy.context.object.location[0] -= 1000


###############################################################################################################################

#                     Delete object 

###############################################################################################################################
def DeleteObject(name):
     print("================= Deleting object "+name+"=========================================================") 
     bpy.data.meshes.remove(bpy.data.meshes[name])
###################################################################################################################
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
#################################################################################################################################

#                          Export object as GTLF

#################################################################################################################################
def ExportObjectAsGTLF(ObjectName,FileName,Frame=0):
    print("--------------------------Saving Object as GTLF   "+str(Frame)+"----------------------------------------------") 
    bpy.context.scene.frame_set(Frame)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[ObjectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[ObjectName] 
    # bpy.ops.export_scene.gltf(export_format='GLTF_EMBEDDED',filepath=FileName, use_selection =True, export_apply=True,export_current_frame=True)
    bpy.ops.export_scene.gltf(export_format='GLB',filepath=FileName, use_selection =True, export_apply=True,export_current_frame=True)
    #https://docs.blender.org/api/current/bpy.ops.export_scene.html
    bpy.context.scene.frame_set(0)


##################################################################################################################################

#                           Export object as BLEND

##################################################################################################################################
def ExportObjectAsBlend(ObjectName,FileName,Frame=0):
        bpy.context.scene.frame_set(Frame)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[ObjectName].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[ObjectName] 
        bpy.data.libraries.write(FileName, set([bpy.data.objects[ObjectName]]), fake_user=True)
        bpy.context.scene.frame_set(0)