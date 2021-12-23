# Functions for setting liquid simulation using manta flow 

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
sys.path.append("/home/breakeroftime/Desktop/Simulations/ModularVesselContent")
sys.path.append(os.getcwd())
import VesselGeneration as VesselGen
import LiquidSimulation as LiquidSim

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r


###############################################################################################################################

###############################################################################################################################

#             Turn Object into Liquid  (apply for vessel content)

###############################################################################################################################
###############################################################################################################################
def TurnToLiquid(name,VesselThinkness):
    print("================= Turning object "+name+" into liquid flow==================================") 

    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["supershape"]
    bpy.context.view_layer.objects.active = bpy.data.objects[name]
    bpy.ops.object.modifier_add(type='FLUID')
    bpy.context.object.modifiers["Fluid"].fluid_type = 'FLOW'
    bpy.context.object.modifiers["Fluid"].flow_settings.flow_type = 'LIQUID'
    #bpy.context.object.modifiers["Fluid"].flow_settings.flow_behavior = 'INFLOW' # Constant flow
    bpy.context.object.modifiers["Fluid"].flow_settings.flow_behavior = 'GEOMETRY' # Object turn to fluid
    #-------------------------Set random velcity---------------------------------------------------------------
    if np.random.rand()<0.85:
        bpy.context.object.modifiers["Fluid"].flow_settings.use_initial_velocity = True
    else:
         bpy.context.object.modifiers["Fluid"].flow_settings.use_initial_velocity = False
    if np.random.rand()<0.75: # Set Random velcocity
        bpy.context.object.modifiers["Fluid"].flow_settings.velocity_normal = 12*np.random.rand()*VesselThinkness
    if np.random.rand()<0.4: # Set randmo ve;lcity
        bpy.context.object.modifiers["Fluid"].flow_settings.velocity_coord[0] = (6*np.random.rand()-3)*VesselThinkness # Use vessel thinkness to limit velocity otherwise particles will diffuse trough vessel walls
        bpy.context.object.modifiers["Fluid"].flow_settings.velocity_coord[1] = (6*np.random.rand()-3)*VesselThinkness
        bpy.context.object.modifiers["Fluid"].flow_settings.velocity_coord[2] = np.random.rand()*2*VesselThinkness
###############################################################################################################################

#                        Create Liquid Domain set liquid parameters

###############################################################################################################################
def TurnToDoman(name,CatcheFolder,Bake,EndFrame,resolution=48,MaxTimeStep=15,MinTimeStep=4,Smooth=True):
    print("================= Turning object "+name+" into liquid domain==================================")     
    if os.path.exists(CatcheFolder):
         shutil.rmtree(CatcheFolder)# Clean catche data
         
#----------------------Select object----------------------------------------------------------------------------
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["supershape"]
    bpy.context.view_layer.objects.active = bpy.data.objects[name]
#------------------Turn to liquid domain---------------------------------------------------------
    bpy.ops.object.modifier_add(type='FLUID')
    bpy.context.object.modifiers["Fluid"].fluid_type = 'DOMAIN'
    bpy.context.object.modifiers["Fluid"].domain_settings.domain_type = 'LIQUID'
    #bpy.context.object.modifiers["Fluid"].flow_settings.flow_type = 'SMOKE'
#----------------------------Set liquid parameters------------------------------------------------------
    bpy.context.object.modifiers["Fluid"].domain_settings.use_diffusion = True
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_type = 'ALL'
    #bpy.ops.fluid.free_all() # Free all data
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_frame_start = 0
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_frame_end = EndFrame
    bpy.context.object.modifiers["Fluid"].domain_settings.resolution_max = resolution
    bpy.context.object.modifiers["Fluid"].domain_settings.timesteps_max = MaxTimeStep
    bpy.context.object.modifiers["Fluid"].domain_settings.timesteps_min = MinTimeStep

    bpy.context.object.modifiers["Fluid"].domain_settings.use_mesh = True
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_directory = CatcheFolder
    if np.random.rand()<0.4:
          bpy.context.object.modifiers["Fluid"].domain_settings.viscosity_base = 1
          bpy.context.object.modifiers["Fluid"].domain_settings.viscosity_exponent = 6 # water
    else:
          bpy.context.object.modifiers["Fluid"].domain_settings.viscosity_exponent = np.random.randint(6)+2
          bpy.context.object.modifiers["Fluid"].domain_settings.viscosity_base = 1+np.random.rand()*5
    if np.random.rand()<0.11:
         bpy.context.object.modifiers["Fluid"].domain_settings.surface_tension = np.random.rand()*10

        
    bpy.context.object.modifiers["Fluid"].domain_settings.mesh_particle_radius = 1+np.random.rand()*1.3

    if np.random.rand()<0.12:
        bpy.context.object.modifiers["Fluid"].domain_settings.mesh_smoothen_pos = np.random.rand()*2
        bpy.context.object.modifiers["Fluid"].domain_settings.mesh_smoothen_neg = np.random.rand()*2
        
    if np.random.rand()<0.06:
        bpy.context.object.modifiers["Fluid"].domain_settings.mesh_concave_upper = np.random.rand()*1 + 0.2 #***************************
        bpy.context.object.modifiers["Fluid"].domain_settings.mesh_concave_lower = np.random.rand()*1 + 0.2 #*****************************
    if np.random.rand()<0.14:
          bpy.context.object.modifiers["Fluid"].domain_settings.use_foam_particles = True
    if np.random.rand()<0.14:
            bpy.context.object.modifiers["Fluid"].domain_settings.use_bubble_particles = True
    if np.random.rand()<0.14:
           bpy.context.object.modifiers["Fluid"].domain_settings.use_spray_particles = True




    
    if np.random.rand()<0.4:
         bpy.context.object.modifiers["Fluid"].domain_settings.flip_ratio = np.random.rand()
    else:
        bpy.context.object.modifiers["Fluid"].domain_settings.flip_ratio = 0.97
        
#================Bake flow start simulation (this can take a long time and cause crash===============================        
    print("Baking Fluid")
    if Bake==True: bpy.ops.fluid.bake_all() 
    print("Done Baking")
    
#==================Smooth liquid mesh==============================================================================    
    if Smooth:
        print("Smoothing liquid")
        bpy.ops.object.modifier_add(type='SUBSURF')
        if np.random.rand()<0.8:
             print("Smoothing liquid mode 2")
        bpy.ops.object.shade_smooth() # smooth 
#    bpy.ops.object.modifier_add(type='SUBSURF')
#    bpy.ops.object.shade_smooth() # smooth 
#    #py.context.object.hide_viewport = True
###############################################################################################################################

#              Turn object to liquid effector (apply for vessel)

###############################################################################################################################
def TurnToEffector(name,SurfaceDisance):
     print("================= Turning object "+name+"  into liquid effector (vessel)==================================") 

     bpy.ops.object.select_all(action="DESELECT")
     bpy.data.objects[name].select_set(True)
     bpy.context.view_layer.objects.active = bpy.data.objects[name]
     bpy.ops.object.modifier_add(type='FLUID')
     bpy.context.object.modifiers["Fluid"].fluid_type = 'EFFECTOR'
     bpy.context.object.modifiers["Fluid"].effector_settings.surface_distance = SurfaceDisance#0.101
#############################################################################################################

#         Create cube for the liquid domain

##############################################################################################################

def CreateDomainCube(name,scale):
       print("================= Creating liquid domain CUBE: "+name+"=========================================================")
       bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, int(scale[2]/2)), scale=scale)
       OriginName=bpy.context.object.name
       bpy.context.object.name = name
       bpy.data.meshes[OriginName].name = name