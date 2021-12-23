
# Set Scene create and set camera, set background, set ground plane, clean scene

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
#####################################################################################3

# Random multiply

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r


###############################################################################################################################

##==============Clean secene remove  all objects currently on the schen============================================

###############################################################################################################################

def CleanScene():
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)
    print("=================Cleaning scene deleting all objects==================================")     
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    allMeshes=[]
    for mes in bpy.data.meshes:
       allMeshes.append(mes)
       print("Deleting Mesh:")
       print(mes)
    for mes in allMeshes:
        bpy.data.meshes.remove(mes)

################################################################################################################################3


#            Set random background HDRI from the HDRI Folder (note this function use existing node structure in the blender file)


#####################################################################################################################################3
def AddBackground(hdr_dir): 
    print("=================Load random background hdri from "+hdr_dir+" to scene==================================")     
   
    names=[]
    import os
#------------------------------------Create list with all hdri files in the folder-------------------------------------
    for hname in os.listdir(hdr_dir): 
       if ".hdr" in hname:
             names.append(hname)
             print(hname)
             bpy.ops.image.open(filepath=hdr_dir+"/"+hname, directory=hdr_dir, files=[{"name":hname, "name":hname}], show_multiview=False)
            # bpy.ops.image.open(filepath="C:\\Users\\Sagi\\Documents\\BLENDER_HDRI\\flower_hillside_2k.hdr", directory="C:\\Users\\Sagi\\Documents\\BLENDER_HDRI\\", files=[{"name":"flower_hillside_2k.hdr", "name":"flower_hillside_2k.hdr"}], show_multiview=False)

#-------------------------------Load random hdri from the list----------------------------------------------------
    u=np.random.randint(len(names))
    print("Background picked:"+names[u])
    bpy.data.worlds["World"].node_tree.nodes["Environment Texture"].image=bpy.data.images[names[u]]
    
#===================================Set random rotation scale/Intensitiy properties for the hdri==========================    
    
#---------------------------Set uniform or hdri background--------------------------------------------    
    bpy.data.worlds["World"].node_tree.nodes["Background.002"].inputs[0].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), 1)

    bpy.data.worlds["World"].node_tree.nodes["Mix Shader.001"].inputs[0].default_value = 1
    if np.random.rand()<0.09:
        bpy.data.worlds["World"].node_tree.nodes["Mix Shader.001"].inputs[0].default_value = np.random.rand()
        bpy.data.worlds["World"].node_tree.nodes["Background.002"].inputs[0].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), 1)
    if np.random.rand()<0.02:
        bpy.data.worlds["World"].node_tree.nodes["Mix Shader.001"].inputs[0].default_value = 0
   
#----------------------Set Background intensity---------------------------------------------------------    
    if np.random.rand()<0.8:
       bpy.data.worlds["World"].node_tree.nodes["Background.001"].inputs[1].default_value = 5*RandPow(3)+1
    else:
       bpy.data.worlds["World"].node_tree.nodes["Background.001"].inputs[1].default_value = 1/(5*RandPow(3)+1)
  
#--------------Rotation-----------------------------------------------   
    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value=(0,3.14,0)# Rotating
    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[2] = np.random.rand()*6.28
    if np.random.rand()<0.30:
       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[0] = +(np.random.rand()/4-1/8)*6.28
       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[1] = +(np.random.rand()/4-1/8)*6.28

    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[3].default_value=(1,1,1)
#--------------Scale--------------------------    
    Scale=5*np.random.rand()**2+1
    if np.random.rand()<0.15:
        bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[3].default_value=(Scale,Scale,Scale)
    if np.random.rand()<0.15:
        bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[3].default_value=(1/Scale,1/Scale,1/Scale)
    



#############################################################################################################

#                    Create ground plane 

####################Add Ground/floor Plane######################################################################################
def AddGroundPlane(name="Ground",x0=0,y0=0,z0=0,sx=10,sy=10): # sz x0,y0 are cordinates sx,sy are scale
    print("================= Creating Ground Plane "+name+"=========================================================")
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False,scale=(sx,sy,0), location=(x0, y0, z0))
    bpy.context.object.location[0] = x0
    bpy.context.object.location[1] = y0
    bpy.context.object.location[2] = z0

    bpy.context.object.scale[0] = sx*(np.random.rand()*4+2)
    bpy.context.object.scale[1] = sy*(np.random.rand()*4+2)
    bpy.context.object.rotation_euler[2] = np.random.rand()*3.144

    OriginName=bpy.context.object.name
    bpy.context.object.name = name
    bpy.data.meshes[OriginName].name = name
    bpy.context.object.cycles.use_adaptive_subdivision = True# Allow bumpiness only work at experimental setting optional
    bpy.ops.object.modifier_add(type='SOLIDIFY')

    return bpy.context.object.scale[0], bpy.context.object.scale[1]
    
##############################################################################################################################

#                   Write camera parameters to dicitonary (for saving to file)

##############################################################################################################################   
def CameraParamtersToDictionary():
   # https://mcarletti.github.io/articles/blenderintrinsicparams/
   #https://www.rojtberg.net/1601/from-blender-to-opencv-camera-and-back/
    dic={}
    dic['name']=bpy.context.object.name #= name    
    dic['Focal Length']=bpy.context.object.data.lens #= lens
    dic['Location']=bpy.context.scene.camera.location[:]#=location
    dic['Rotation']=bpy.context.scene.camera.rotation_euler[:]#=rotation
    dic['Perseption']=bpy.context.scene.camera.data.type #= 'PERSP'
    dic['shift_x']=bpy.context.scene.camera.data.shift_x#=shift_x
    dic['shift_y']=bpy.context.scene.camera.data.shift_y#=shift_y
    dic['sensor_width']=bpy.context.object.data.sensor_width 
    dic['sensor_height']=bpy.context.object.data.sensor_height
    dic['sensor_fit']=bpy.context.object.data.sensor_fit
    dic['resolution_y']=bpy.context.scene.render.resolution_y 
    dic['resolution_x']=bpy.context.scene.render.resolution_x 
    dic['pixel_aspect_x']=bpy.context.scene.render.pixel_aspect_x
    dic['pixel_aspect_y']=bpy.context.scene.render.pixel_aspect_y  
    dic['resolution_percentage']=bpy.context.scene.render.resolution_percentage
    dic['scale']=bpy.context.object.scale[:]

    return dic

        
##############################################################################################################################

#                   Add Camera to scene

##############################################################################################################################   
def SetCamera(name="Camera", lens = 32, location=(0,0,0),rotation=(0, 0, 0),shift_x=0,shift_y=0):
    
    #=================Set Camera================================
    
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=location, rotation=rotation)
    bpy.context.object.name = name    
    bpy.context.object.data.lens = lens

    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.camera.location=location
    bpy.context.scene.camera.rotation_euler=rotation
    bpy.context.scene.camera.data.type = 'PERSP'
    bpy.context.scene.camera.data.shift_x=shift_x
    bpy.context.scene.camera.data.shift_y=shift_y

##############################################################################
   
#    Change Camera properties location and angle

########################################################################################
def ChangeCamera(name="Camera", lens = 32, location=(0,0,0),rotation=(0, 0, 0),shift_x=0,shift_y=0):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
    
    bpy.context.object.data.lens = lens
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.camera.location=location
    bpy.context.scene.camera.rotation_euler=rotation
    bpy.context.scene.camera.data.type = 'PERSP'
    bpy.context.scene.camera.data.shift_x=shift_x
    bpy.context.scene.camera.data.shift_y=shift_y
########################################################################################################

# Randomly set camera position (so it will look at the vessel)

#################################################################
def RandomlySetCameraPos(name,VesWidth,VesHeight):
     print("Randomly set camera position")
     MinDist=np.max([VesWidth,VesHeight])
     R=np.random.rand()*MinDist*4+MinDist*3 
  #   R=np.random.rand()*MinDist*3.5+MinDist*2.5
     print('R='+str(R)+"  MinDist="+str(MinDist))
     Ang=(1.0-1.1*np.random.rand()*np.random.rand())*3.14/2 
     x=0
     y=np.sin(Ang)*R+np.random.rand()*VesWidth-VesWidth/2
     z=np.cos(Ang)*R+VesHeight*np.random.rand()
     rotx=Ang
     rotz=3.14159
     roty=(0.5*np.random.rand()-0.5*np.random.rand())*np.random.rand()
    
     Focal=50 #(np.random.rand()*5+2)*R/np.max([VesWidth,VesHeight])
     shift_x=0#0.2-np.random.rand()*0.4
     shift_y=0#0.2-np.random.rand()*0.4
     SetCamera(name="Camera", lens = Focal, location=(x,y,z),rotation=(rotx, roty, rotz),shift_x=shift_x,shift_y=shift_y)
