#Description: This script will procedurally generate images of randomly shaped  transparent vessel with simulated liquid of random material, and random background
#  This will be used to generate images that will be saved. This script will generate multiple images in multiple simulation


#Where to start: Best place to start is in the “Main” section in the last part of this script

#What needed:  Folder of HDRI and a folder  of pbr materials (Example folders are available in this script folder as: HDRI_BackGround, PBRMaterials

# What to do: Go to “main” section in the end of this file, in “input parameter” subsection
# 1) set Path to OutFolder where generated images should be saved
# 2) Set Path HDRI_BackGroundFolder which contain background HDRI (for start use the example HDRI_BackGround, supplied in this script folder)
# 3) Set Path to PBRMaterialsFolder to the folder contain PBR materials (for start use the example PBRMaterials folder supplied in this script folder)
# 4) Run script images should start appearing in the OutFolder  after few minutes (depending on rendering file)

# Notes:
# 1) Try to avoid relative paths Blender is not very good with those.
# 2) Running this script should paralyze blender until the script is done which can take a while
# 3) The script refers to materials nodes and will only run as part of the blender file
# 4) If you want to run script as stand alone without blender file, go to “Main” section and disable all the "assign material" functions
# 5) If you want to run script as stand alone without blender file or supporting Hdri and Pbr folders, go to main and disable all the "assign material" functions and also the "set background" function
# 6) This was on ubuntu 20 with blender 2.91

###############################Dependcies######################################################################################3

import bpy
import math
import numpy as np
import bmesh
import os
import shutil

###############################################################################################################################

##==============Clean secene remove  all objects currently on the schen============================================

###############################################################################################################################

def CleanScene():
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
##################################################################################################################333

    #                          Create vessel instance

####################################################################################################################
def AddVessel(VesselName="Vessel",ContentName="MaterialContent",MinH=10,MaxH=60,MinR=5,MaxR=60):   
    print("=================Create Vessel Mesh object and add to scene==================================")     
    #--------------------Create random shape vessel assign parameters----------------------------------------- 
    
    MatX_RadRatio=MatY_RadRatio=np.random.rand()*0.66+0.3 # Ratio of the material radius compare to 
    MatZ_RadRatio=np.random.rand()
    
    Vnum = np.random.randint(36)+4 #Number vertex in a layer/ring
    h=np.random.randint(MaxH-MinH)+MinH # Height of vessel (number of layers
    
    MaterialTopHeight=int((np.random.rand()*(h-1))+2)
    
    MaterialInitHeight=int(np.random.rand()*(MaterialTopHeight-1))
    if MaterialTopHeight>h: MaterialTopHeight=h
    if MaterialTopHeight==0: MaterialTopHeight=1
    if MaterialInitHeight<0: MaterialInitHeight=0
    if MaterialInitHeight>MaterialTopHeight: MaterialInitHeight= MaterialTopHeight-1
    if MaterialInitHeight==MaterialTopHeight: MaterialInitHeight= MaterialTopHeight-1
    
  
    print("h="+str(h))
    print("MaterialInitHeight="+str(MaterialInitHeight))
    print("MaterialTopHeight="+str(MaterialTopHeight))
    #------------------------Create vessel random information---------------------------------------------------- 

    Vinc = (math.pi*2)/(Vnum) # difference of angle between vertex
    # Generate
    slop=np.random.rand()*8-4 # Slioe of the  vessel  at start
    r=np.random.rand()*50+10 # Radius of the vessel at start
    r0=r
    rl=[r]# array of radiuses in each layer of  the vessel
    dslop=np.random.rand()*0.4-0.2 # diffrential of slope
    if np.random.rand()<-0.7: 
         Mode="Linear"
    else:
         Mode="Sin"
         Rad=np.random.rand()*3.14
         Drad=np.random.rand()*0.3
         
    for i in range(h): # go layer by layer and change vessel raius
       if Mode=="Linear":
             slop+=dslop#-np.random.rand()*0.4
             if slop<-7:
                 dslop=np.random.rand()*0.4
             if slop>7: 
                 dslop=-np.random.rand()*0.4
             if np.random.rand()<1/h:
                 slop=np.random.rand()*8-4
             if np.random.rand()<2/h:
                 dslop=np.random.rand()*0.4-0.2
             if np.random.rand()<1/h:
                 slop=0
                 dslop=0
             if slop==0 and np.random.rand()<4/h:
                 slop=0
                 dslop=0
             if r>MaxR:   
                  slop=-np.random.rand()*4
             if r<MinR:
                 if np.random.rand()<0.8: 
                    slop=np.random.rand()*4         
                    r+=slop
                 else:
                    r=8
                    slop=0
             if np.random.rand()<1/h:
                 Mode="Sin"
       elif Mode=="Sin":
             Rad+=Drad
             slop=np.sin(Rad)
             r+=slop
             if np.random.rand()<1/h:
                 Mode="Linear"
             
             
       rl.append(r)         
    thk=np.min(rl)*(np.random.rand()+0.1)/4# # Vessel thikness    
    #-----------Strech----------------------------------------------------------------------------------- 
    stx=sty=1   
    if np.random.rand()<0.2:
        stx=np.random.rand()*0.8+0.2
        sty=np.random.rand()*0.8+0.2
    #----------------------------------------------------------------------------------------------------   
    #---------------------------Add vertexes to create vessel-----------------------------------------------
    #------------------------------------------------------------------------------------------------
    Matverts = []
    Matfaces = []
    Matedges = []
    #-----------------------Create vertex object and faces arrays------------------------------------------------------------------
    verts = []
    faces = []
    edges = []
    #----------------------------------------Add vertex---------------------------------------
    
    MaxXY=0
    MaxZ=0
    for fz in range(len(rl)):
        for j in range(0,Vnum ):
            theta=j*Vinc
            r1=rl[fz]
            x = (r1 * math.cos(theta))*stx
            y = (r1 * math.sin(theta))*sty
            z = fz #scale * (r2 * math.sin(phi))
            MaxZ=np.max([z,MaxZ])
            MaxXY=np.max([x,y,MaxXY])
         #   print(x)
            vert = (x,y,z)  # Add Vertex
            verts.append(vert)
            Mvert = (x* MatX_RadRatio,y* MatY_RadRatio,z)  # Note there factor of 10  in size
            if fz<=MaterialTopHeight and fz>=MaterialInitHeight: 
                  Matverts.append(Mvert)
    
    #---------------------------------------------------------------------------------------------------------------
    #        Add faces / combine vertex into faces
    #----------------------------------------------------------------------------------------------------------------
    #----------------------------vessel wall----------------------------------    
    for k in range(len(verts)-Vnum):
        if not k%Vnum==(Vnum-1): 
            face = (k,k+1,k+Vnum+1,k+Vnum)
        else: # the last point in the ring is connected to the first point in the ring
            face = (k,k-Vnum+1,k+1,k+Vnum)
        faces.append(face) 
        if k+Vnum<len(Matverts):
             Matfaces.append(face) 
    #    #print(k)
    #------------Vessel floor as single face-------------------------------------------        
    face = (0,)
    for k in range(1,Vnum):
        face += (k,)
    #    print(k)
    faces.append(face) 
    Matfaces.append(face)
    #------------Vessel open as as a sing single face-------------------------------------------        
    face = (len(Matverts)-Vnum-1,)
    for k in range(len(Matverts)-Vnum,len(Matverts)):
        face += (k,)
      
      #  print(k)
    Matfaces.append(face) 


    #---------------------------------------------------------------------------------------------------------------
    #  Create vessel mesh and object and add to scene
    #----------------------------------------------------------------------------------------------------------------
    #create mesh and object
    mymesh = bpy.data.meshes.new(VesselName)
    myobject = bpy.data.objects.new(VesselName,mymesh)
     
    #set mesh location
    myobject.location=(0,0,0)
    bpy.context.collection.objects.link(myobject)
    #bpy.context.scene.objects.link(myobject)
     
    #create mesh from python data
    mymesh.from_pydata(verts,edges,faces)
    mymesh.update(calc_edges=True)

    bpy.data.objects[VesselName].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["Vessel"]
    bpy.context.view_layer.objects.active = bpy.data.objects[VesselName]
    #bpy.context.object=bpy.data.objects['supershape'
    #-----------------------------------------------------------------------------------------------------------------
    #              Add modifier to vessel
    #----------------------Add modifiers to vessel to smooth and i----------------------------------------------------------
    bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
    SubdivisionLevel=np.random.randint(4)
    SubdivisionRenderLevel=np.random.randint(4)
    bpy.context.object.modifiers["Subdivision"].levels = SubdivisionLevel
    bpy.context.object.modifiers["Subdivision"].render_levels = SubdivisionRenderLevel
    bpy.ops.object.shade_smooth() # smooth 
    #if np.random.rand()<10.7:  
    bpy.ops.object.modifier_add(type='SOLIDIFY')# Set Vessel thikness 
    bpy.context.object.modifiers["Solidify"].thickness = (MaxXY/(10))#*np.random.rand()+0.1) #thk/10
    #    if np.random.rand()<0.5:
    #        bpy.context.object.modifiers["Solidify"].use_even_offset = True
    #    else:
    #         bpy.context.object.modifiers["Solidify"].use_even_offset = False

    #-------------------------------------------------------------------------------------------------------------------------     
    #create mesh and object
    mymesh = bpy.data.meshes.new(ContentName)
    myobject = bpy.data.objects.new(ContentName,mymesh)
     
    #set mesh location
    myobject.location=(0,0,0)
    bpy.context.collection.objects.link(myobject)
    #bpy.context.scene.objects.link(myobject)
     
    #create mesh from python data


    mymesh.from_pydata(Matverts,Matedges,Matfaces)
    mymesh.update(calc_edges=True)

    bpy.data.objects[ContentName].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["Vessel"]
    bpy.context.view_layer.objects.active = bpy.data.objects[ContentName]
    #bpy.context.object=bpy.data.objects['supershape'] 
    bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
    bpy.context.object.modifiers["Subdivision"].levels = SubdivisionLevel
    bpy.context.object.modifiers["Subdivision"].render_levels = SubdivisionRenderLevel
    bpy.ops.object.shade_smooth() # smooth   
    return MaxXY,MaxZ
################################################################################################################################3


#            Set random background HDRI from the HDRI Folder


###############################################################################################################################

######################################Set Background HDRI###############################################################################

#####################################################################################################################################3
def AddBackground(hdr_dir): 
    print("=================Load random background hdri from "+hdr_dir+" to scene==================================")     
   
    names=[]
    import os

    for hname in os.listdir(hdr_dir): 
       if ".hdr" in hname:
             names.append(hname)
             print(hname)
             bpy.ops.image.open(filepath=hdr_dir+"/"+hname, directory=hdr_dir, files=[{"name":hname, "name":hname}], show_multiview=False)
            # bpy.ops.image.open(filepath="C:\\Users\\Sagi\\Documents\\BLENDER_HDRI\\flower_hillside_2k.hdr", directory="C:\\Users\\Sagi\\Documents\\BLENDER_HDRI\\", files=[{"name":"flower_hillside_2k.hdr", "name":"flower_hillside_2k.hdr"}], show_multiview=False)

    u=np.random.randint(len(names))
    print("Background picked:"+names[u])
    bpy.data.worlds["World"].node_tree.nodes["Environment Texture"].image=bpy.data.images[names[u]]
    bpy.data.worlds["World"].node_tree.nodes["Background.001"].inputs[1].default_value = np.random.rand()*1.5+0.1


###############################################################################################################################

##################################Turn Object into Liquid##############################################################################

###############################################################################################################################
def TurnToLiquid(name):
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
    bpy.context.object.modifiers["Fluid"].flow_settings.use_initial_velocity = True
    bpy.context.object.modifiers["Fluid"].flow_settings.velocity_coord[0] = np.random.rand()*3
    bpy.context.object.modifiers["Fluid"].flow_settings.velocity_coord[1] = np.random.rand()*3
    bpy.context.object.modifiers["Fluid"].flow_settings.velocity_coord[2] = np.random.rand()*20
###############################################################################################################################

################################Create Liquid Domain###############################################################################

###############################################################################################################################
def TurnToDoman(name,CatcheFolder,Bake,EndFrame):
    print("================= Turning object "+name+" into liquid domain==================================") 
    if os.path.exists(CatcheFolder):
         shutil.rmtree(CatcheFolder)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["supershape"]
    bpy.context.view_layer.objects.active = bpy.data.objects[name]

    bpy.ops.object.modifier_add(type='FLUID')
    bpy.context.object.modifiers["Fluid"].fluid_type = 'DOMAIN'
    bpy.context.object.modifiers["Fluid"].domain_settings.domain_type = 'LIQUID'
    #bpy.context.object.modifiers["Fluid"].flow_settings.flow_type = 'SMOKE'

    bpy.context.object.modifiers["Fluid"].domain_settings.use_diffusion = True
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_type = 'ALL'
    #bpy.ops.fluid.free_all() # Free all data
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_frame_start = 0
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_frame_end = EndFrame
    bpy.context.object.modifiers["Fluid"].domain_settings.resolution_max = 64
    bpy.context.object.modifiers["Fluid"].domain_settings.use_mesh = True
    bpy.context.object.modifiers["Fluid"].domain_settings.cache_directory = CatcheFolder
    if Bake==True: bpy.ops.fluid.bake_all() 
    #py.context.object.hide_viewport = True
###############################################################################################################################

####################################Turn object to liquid effector################################################################ 

###############################################################################################################################
def TurnToEffector(name):
     print("================= Turning object "+name+"  into liquid effector (vessel)==================================") 

     bpy.ops.object.select_all(action="DESELECT")
     bpy.data.objects[name].select_set(True)
     bpy.context.view_layer.objects.active = bpy.data.objects[name]
     bpy.ops.object.modifier_add(type='FLUID')
     bpy.context.object.modifiers["Fluid"].fluid_type = 'EFFECTOR'
     bpy.context.object.modifiers["Fluid"].effector_settings.surface_distance = 0.101
###############################################################################################################################

#####################################Hide object from view (doesnt work in most caseS)############################################################### 

###############################################################################################################################
def HideObject(name): # Dont work Hide object *use this after making all the changes to the object. Hidden object cannot be selected or modified
     print("================= Hiding object "+name+"=========================================================") 

     bpy.ops.object.select_all(action="DESELECT")
     bpy.data.objects[name].select_set(True)
     bpy.context.view_layer.objects.active = bpy.data.objects[name]
  #   print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
#     print(bpy.context.view_layer.objects.active)
#     print("llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll")
     py.context.object.hide_viewport = True
     
###############################################################################################################################

##############################Delete object###############################################################

###############################################################################################################################
def DeleteObject(name):
     print("================= Deleting object "+name+"=========================================================") 
     bpy.data.meshes.remove(bpy.data.meshes[name])
###################################################################################################################
###############################################################################################################################

###################Assing vessel material#################################################################

###############################################################################################################################
def AssignMaterialToVessel(name):  
    print("================= Assign material to vessel "+name+"=========================================================")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
#------------------------Assing material node----------------------------------------------------------
    if np.random.rand()<10.8:
       bpy.data.objects[name].data.materials.append(bpy.data.materials['Glass'])
   
#-----------Set random properties for material-----------------------------------------------------

    if np.random.rand()<0.3:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1-np.random.rand()**3*0.3 # Transmission
    else:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1 #Transmission
    if np.random.rand()<0.3:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = np.random.rand()**3*0.3 # Roughness
    else: 
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0# Roughness

    print(bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value)
    if np.random.rand()<0.2:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1) # random color hsv
    else:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1,1, 1) # white color
    if np.random.rand()<0.2:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = np.random.rand()*4+0.1# ior index of reflection for transparen objects
    else: 
        bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 1.45 #ior index of reflection for transparen objects  

    if np.random.rand()<0.2:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = np.random.rand()**3*0.3 # transmission rouighness
    else: 
        bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0 # transmission rouighness

    if np.random.rand()<0.25:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[4].default_value = np.random.rand()**3# metalic
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[4].default_value =0# metalic  
#############################################################################################################################################

##############################Assign Liquid material#################################################################################################

#############################################################################################################################################
def AssignMaterialToLiquid(name):  
    print("================= Assign material to vessel "+name+"=========================================================")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
     # Basically pick existing node and assign it to the material and set random properties (this will not work if the node doesnt already exist)          
  #  if len(bpy.data.objects["Vessel"].data.materials)==0:
    if np.random.rand()<10.8:
       bpy.data.objects[name].data.materials.append(bpy.data.materials['LiquidMaterial'])

# ----------------------------------Select random property for material
#    #bpy.ops.object.modifier_add(type='SUBSURF')

    if np.random.rand()<0.9:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = np.random.rand() # Transmission
    else:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1 #Transmission
    if np.random.rand()<0.9:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = np.random.rand()# Roughness
    else: 
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0# Roughness

    if np.random.rand()<0.9:
       bpy.data.materials["LiquidMaterial"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1) # random color hsv
    else:
       bpy.data.materials["LiquidMaterial"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1,1, 1) # white color
    if np.random.rand()<0.4:
       bpy.data.materials["LiquidMaterial"].node_tree.nodes["Principled BSDF"].inputs[4].default_value = np.random.rand() # metalic
    elif np.random.rand()<0.5:
      bpy.data.materials["LiquidMaterial"].node_tree.nodes["Principled BSDF"].inputs[4].default_value =0# metalic
    else:
       bpy.data.materials["LiquidMaterial"].node_tree.nodes["Principled BSDF"].inputs[4].default_value =1# metalic


    if np.random.rand()<0.4:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[8].default_value = np.random.rand()# unisotropic
    else:
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[8].default_value = 0# unisotropic
    if np.random.rand()<0.4:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[9].default_value = np.random.rand()# unisotropic rotation
    else: 
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0# unisotropic rotation
    if np.random.rand()<0.4:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[10].default_value = np.random.rand()# sheen
    else: 
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[10].default_value = 0# sheen
    if np.random.rand()<0.4:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[11].default_value = np.random.rand()# sheen tint
    else: 
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[11].default_value = 0.5# sheen tint
    if np.random.rand()<0.5:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = np.random.rand()*4+0.1# ior index of reflection for transparen objects
    else: 
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 1.45 #ior index of reflection for transparen objects  
    if np.random.rand()<0.5:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = np.random.rand()*4+0.1# ior index of reflection for transparen objects
    else: 
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 1.45 #ior index of reflection for transparen objects  
    
    
    
    if np.random.rand()<0.2:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = np.random.rand()**2*0.4# transmission rouighness
    else: 
        bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0 # transmission rouighness
    if np.random.rand()<0.2:
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[17].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1)# Emission
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[18].default_value = (np.random.rand()**2)*100 # Transmission strengh
    else: 
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[17].default_value = (0, 0,0, 1)## transmission rouighness
       bpy.data.materials['LiquidMaterial'].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 1# Transmission strengh
      

#############################################################################################################################################################

#               Assign a random PBR material into object

#########################################################################################################################################################################
def AssignPBRMaterialForObject(name,PbrMainDir):
    bpy.data.objects[name].data.materials.append(bpy.data.materials['PbrMaterial'])
    
    bpy.data.materials['PbrMaterial'].cycles.displacement_method = 'BOTH'
    ##############################Add displacement to make the ground not flat######################################################
    if np.random.rand()<0.5: # This will add topolgy/displacement but only if cycle/experimental rendring is active
       bpy.data.materials["PbrMaterial"].node_tree.nodes["Displacement"].inputs[2].default_value =  np.random.rand()
       bpy.ops.object.modifier_add(type='SUBSURF')
       bpy.context.object.modifiers["Subdivision"].render_levels = bpy.context.object.modifiers["Subdivision"].levels =6#np.random.randint(7)
    #-------------------------------------------------------------------------------------------
    #                   Select random material from the PbrDir for the ground
    #--------------------------------------------------------------------------------------------

    AllPbrDirs=[]
    for sdir in os.listdir(PbrMainDir):
        if os.path.isdir(PbrMainDir+"/"+sdir): AllPbrDirs.append(PbrMainDir+"/"+sdir)

    PbrDir=AllPbrDirs[np.random.randint(len(AllPbrDirs))]

    bpy.ops.image.open(filepath=PbrMainDir+"/black.jpg", directory=PbrMainDir, files=[{"name":"black.jpg", "name":"black.jpg"}], show_multiview=False)
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.004"].image=bpy.data.images["black.jpg"]

    for Fname in os.listdir(PbrDir):
       if ("olor." in Fname)  or ("COLOR." in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.001"].image=bpy.data.images[Fname]
          print("Color "+ Fname)
       if ("oughness." in Fname) or ("ROUGH." in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.002"].image=bpy.data.images[Fname]
          print("Roughness "+ Fname)
       if ("ormal." in Fname)  or ("NORM." in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.003"].image=bpy.data.images[Fname]
          print("Normal "+ Fname)
       if ("eight." in Fname) or ("DISP." in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture"].image=bpy.data.images[Fname]
          print("Height "+ Fname)
       if ("etallic." in Fname):
          bpy.ops.image.open(filepath=PbrDir+"/"+Fname, directory=PbrDir, files=[{"name":Fname, "name":Fname}], show_multiview=False)
          bpy.data.materials["PbrMaterial"].node_tree.nodes["Image Texture.004"].image=bpy.data.images[Fname]
          print("Metallic "+ Fname)
    Sc=np.random.rand()*2+0.2 #Scale
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Mapping"].inputs[3].default_value[0] = Sc 
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Mapping"].inputs[3].default_value[1] = Sc
    bpy.data.materials["PbrMaterial"].node_tree.nodes["Mapping"].inputs[3].default_value[2] = Sc 
#############################################################################################################

#         Create cube for the liquid domain

##############################################################################################################

def CreateDomainCube(name,scale):
       print("================= Creating liquid domain CUBE: "+name+"=========================================================")
       bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=scale)
       OriginName=bpy.context.object.name
       bpy.context.object.name = name
       bpy.data.meshes[OriginName].name = name
#############################################################################################################

#                    Create ground plane 

####################Add Ground/floor Plane######################################################################################
def AddGroundPlane(name="Ground",x0=0,y0=0,z0=0,sx=10,sy=10): # sz x0,y0 are cordinates sx,sy are scale
    print("================= Creating Ground Plane "+name+"=========================================================")
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False,scale=(sx,sy,0), location=(x0, y0, z0))
    bpy.context.object.scale[0] = sx*(np.random.rand()*1+2)
    bpy.context.object.scale[1] = sy*(np.random.rand()*1+2)
    bpy.context.object.rotation_euler[2] = np.random.rand()*3.144
    bpy.context.object.location[2] = -1
    OriginName=bpy.context.object.name
    bpy.context.object.name = name
    bpy.data.meshes[OriginName].name = name
    
##############################################################################################################################

#                   Add Camera to scene

##############################################################################################################################   
def SetCamera(name="Camera", lens = 32, location=(0,0,0),rotation=(0, 0, 0)):
    
    #=================Set Camera================================
    
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=location, rotation=rotation)
    bpy.context.object.name = name    
    bpy.context.object.data.lens = lens

    bpy.context.scene.camera = bpy.context.object
#    bpy.context.scene.camera.location=location
#    bpy.context.scene.camera.rotation_euler=rotation
##############################################################################
   
#    Change Camera properties location and angle

########################################################################################
def ChangeCamera(name="Camera", lens = 32, location=(0,0,0),rotation=(0, 0, 0)):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
    
    bpy.context.object.data.lens = lens
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.camera.location=location
    bpy.context.scene.camera.rotation_euler=rotation
    
   
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
        #============Render image=============================================================
        #bpy.ops.import_scene.obj(filepath="C:/Users/Sagi/Documents/BlenderObjects/IronMan/IronMan.obj")
        render.filepath=OutputFolder+"/"+FileNamePrefix+"_Frame_"+str(k)+".jpg"
        # render scene
        bpy.ops.render.render(write_still=True)
        print(render.filepath+" Saved")


################################################################################################################################################################

#               Main 

###################################################################################################################################################################
#  Main loop generate create vessel and liquid simulate liquid and save image

#------------------------Input parameters---------------------------------------------------------------------

# Example HDRI_BackGroundFolder and PBRMaterialsFolder folders should be in the same folder as the script. Recomand not to use relative locations as blender is not good with this 
OutFolder="/home/chemargos/Desktop/BlenderLiquidScripting_DataSetCreating/Procedural_Data_Generation_Liquid_Transperent_Vessel/Out/"# Where output images will be saved
HDRI_BackGroundFolder="/home/chemargos/Desktop/BlenderLiquidScripting_DataSetCreating/Procedural_Data_Generation_Liquid_Transperent_Vessel/HDRI_BackGround//" # Background dri folder
PBRMaterialsFolder="/home/chemargos/Desktop/BlenderLiquidScripting_DataSetCreating/Procedural_Data_Generation_Liquid_Transperent_Vessel/PBRMaterials/" #folder of pbr materials
NumSimulationsToRun=3 # Number of simulation to run
#==============Set Rendering engine (for image creaion==========================================

bpy.context.scene.render.engine = 'CYCLES' # Use this configuration if you want to be able to see the content of the vessel (eve does not support content)
#bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL' # Not sure if this is really necessary but might help with sum surface textures
bpy.context.scene.cycles.samples = 90 # This work well for rtx 3090 for weaker hardware this can take lots of time
bpy.context.scene.cycles.preview_samples = 900 # This work well for rtx 3090 for weaker hardware this can take lots of time

#-------------------------Create delete folders--------------------------------------------------------------

#CountFolder=OutFolder+"/count/" # Folder for remembring image numbers (for restarting script without over running existing files)
CatcheFolder=OutFolder+"//Temp_cache//" # folder where liquid simulation will be saved (this will be deleted every simulation
if not os.path.exists(OutFolder): os.mkdir(OutFolder)
#if not os.path.exists(CountFolder): os.mkdir(CountFolder) # To avoid repition keep the numbers of all frames


for cnt in range(10000000000000):
    if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation folder to free space
    if NumSimulationsToRun==0: break
    OutputFolder=OutFolder+"/"+str(cnt)
    if  os.path.exists(OutputFolder): continue # Dont over run existing folder # 
    NumSimulationsToRun-=1



    #================================Run simulation and rendering=============================================================================
    print("=========================Start====================================")
    print("Simulation number:"+str(cnt)+" Remaining:"+ str(NumSimulationsToRun))
    CleanScene()  

    #------------------------------Create object meshes and assign materials and background---------------------------------
    MaxXY,MaxZ=AddVessel("Vessel","Content") # Create Vessel object named "Vessel" and add to scene also create mesh inside the vessel ("Content) which will be transformed to liquid
    AssignMaterialToVessel("Vessel") # assign random material to vessel object

    AddGroundPlane("Ground",x0=0,y0=0,z0=0,sx=MaxXY,sy=MaxXY) # Add plane for ground
    AssignPBRMaterialForObject("Ground",PBRMaterialsFolder) # Assign PBR material to ground plane (Physics based material) from PBRMaterialsFolder

    AddBackground(HDRI_BackGroundFolder) # Add randonm Background hdri from hdri folder

    CreateDomainCube(name="LiquidDomain",scale=(MaxXY*2, MaxXY*2, MaxZ*2)) # Create Cube that will act as liquid domain
    AssignMaterialToLiquid("LiquidDomain") # Assign material for the liquid domain (basically the material of the liquid)

    #-----------------------------Create and bake liquid simulation-----------------------------------

    TurnToLiquid("Content") # Turn Content mesh into liquid
    TurnToEffector("Vessel") # Turn Vessel into liquid effector (will interact with liquid as solid object)
    TurnToDoman("LiquidDomain",CatcheFolder=CatcheFolder,Bake=True,EndFrame=100) # Turn domain Cube into domain and bake simulation (Time consuming)

    DeleteObject("Content") # Delete the liquid  object (The liquid that was generated in the simulation is attached to the LiquidDomain and will not be effected

    #-----------------------------Render and save pictures--------------------------------------------

    SetCamera(name="Camera", lens=32, location=(113,149,128),rotation=(1.03, 0, 2.493)) # Set Camera
    RenderImageAndSave(FileNamePrefix="VesslContent",FramesToRender=[20,50,80],OutputFolder=OutputFolder) # Render images and Save

    DeleteObject("Vessel") #Delete vessel
    RenderImageAndSave(FileNamePrefix="OnlyMaterial",FramesToRender=[20,50,80],OutputFolder=OutputFolder) # Render images of only material
 
    f=open(OutputFolder+"/Finishe.txt","w")
    if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation catche folder to free space
    print("========================Finished==================================")
