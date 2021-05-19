
## Description:
# This script will procedurally generate images of randomly shaped transparent vessels with random objects or simulated liquid inside the vessel. 

#Images, Depth maps, Normal maps, and material properties will be saved to the output folder. Images of the vessel content without vessel and vessel without content will also be saved. 


#### This was run with Blender 2.92 with no additional add-ons

### Where to start: 
#The best place to start is in the “Main” section in the last part of this script.

### What needed:  
#Objects Folder, HDRI background folder, and a folder of PBR materials (Example folders are supplied as: “HDRI_BackGround”, “PBRMaterials”, and “Objects”)

## How to use:
#1) Go to the “Main” section of the python script   (at the end of this file), in the “input parameter” subsection.
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
#There are two generation modes one mode will create liquid inside the vessel, and the other will put random objects inside the vessel. The ratio between the two is controlled by the parameter: "LiquidContentFractionOfCases". Setting this to zero means that only vessels with objects inside them will be generated. Setting this to 1 means that only vessels with liquids inside them will be generated.


###############################Dependcies######################################################################################3

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import json
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
###########################333#############################################################

# Create random slope curve  (r vs z) for vessel region 

#########################################################################################################
def CreateSlope(slope0):
    pr=np.random.rand();
 
    a=b=y=Rad=Drad=0
    print(pr)
    if pr<0.20:
        Mode="Linear"
        slope=0
        a=0
        b=0
        print("++++++++++++++++")
    elif pr<0.38:
        Mode="Linear"
        slope=np.random.rand()*3-1.5
        a=0
        b=0
    elif pr<0.56:
        Mode="Linear"
        slope=slope0
        a=np.random.rand()*0.3-0.15
        b=0
    elif pr<0.78:
        Mode="polynomial"
        slope=slope0
        a=np.random.rand()*0.3-0.15
        b=np.random.rand()*0.2-0.1
    elif pr<1.1:
        Mode="Sin"
        print("SIN")
        a=2*RandPow(2)
        Rad=np.random.rand()*3.14
        Drad=RandPow(2)#3
        slope=0
        b=0
    y=0
    
    return slope,a,b,y,Mode,Rad,Drad
    
###################################################################################################################

# CreateRadius Array for vessel profile (Curve that determine how the vessel radius change a long the Z axis)

##################################################################################################################
def CreateRadiusArray(MinH,MaxH,MinR,MaxR): 
        print("========================Creating Radius Array=====================================================")
        h=np.random.randint(MaxH-MinH)+MinH # Height of vessel (number of layers
        
        MaterialTopHeight=int((np.random.rand()*(h-1))+2)
        
        MaterialInitHeight=int(np.random.rand()*(MaterialTopHeight-1))
        if MaterialTopHeight>h: MaterialTopHeight=h
        if MaterialTopHeight<3: MaterialTopHeight=3
        if MaterialInitHeight<MaterialTopHeight: MaterialInitHeight = MaterialTopHeight - 2
        if MaterialInitHeight>MaterialTopHeight: MaterialInitHeight= MaterialTopHeight-1
        if MaterialInitHeight==MaterialTopHeight: MaterialInitHeight= MaterialTopHeight-1
     
    #------------------------------------------------------------------
        r=np.random.rand()*50+4 # Radius of the vessel at start
        r0=r
        rl=[r]# array of radiuses in each layer of  the vessel
#        dslop=np.random.rand()*0.4-0.2 # diffrential of slope
#        if np.random.rand()<-0.7: 
#             Mode="Linear"
#        else:
#             Mode="Sin"
#             Rad=np.random.rand()*3.14
#             Drad=np.random.rand()*0.3
#             
        slope,a,b,y,Mode,Rad,Drad=CreateSlope(0)
        dslop=0
        swp=np.random.rand()*3 # Probability for replacement
        for i in range(h): # go layer by layer and change vessel raius
            while(True):  
                 if Mode=="Linear":
                     dslop=a+b*y
                     slope+=dslop#-np.random.rand()*0.4
                     y+=1
                 if Mode=="Sin":
                     Rad+=Drad                 
                     #slope=a*np.sin(Rad)
                     slope=a*np.sin(Rad)
    #                  
#                 if slope<-9 and dslop<0:
#                     slope,a,b,y,Mode,Rad,Drad=CreateSlope(slope)
#                     continue
#                 
#                 if slope>9  and dslop>0: 
#                     slope,a,b,y,Mode,Rad,Drad=CreateSlope(slope)
#                     continue
                 if (r+slope)>MaxR and dslop>0:
                     slope,a,b,y,Mode,Rad,Drad=CreateSlope(slope)
                     continue
                 if (r+slope)<MinR and dslop<0:
                        slope,a,b,y,Mode,Rad,Drad=CreateSlope(slope)
                        continue
                 if np.random.rand()<swp/h:
                     slope,a,b,y,Mode,Rad,Drad=CreateSlope(slope)
                     print("SwitcH")
                     print(Mode)
                 break
  
            r+=slope 
            if r>MaxR: r=MaxR
            if r<MinR: r=MinR      
            rl.append(r)  
           #print("h="+str(h))
           #print("MaterialInitHeight="+str(MaterialInitHeight))
           #print("MaterialTopHeight="+str(MaterialTopHeight))
        return rl, MaterialTopHeight, MaterialInitHeight,h   
##################################################################################################################333

#                          Create vessel Object 

####################################################################################################################
def AddVessel(VesselName="Vessel",ContentName="MaterialContent",MinH=4,MaxH=80,MinR=4,MaxR=40,ScaleFactor=0.1):   
    print("=================Create Vessel Mesh object and add to scene==================================")     
    #--------------------Create random shape Material assign parameters----------------------------------------- 
    if np.random.rand()<0.5: 
        ModeThikness="Solidify" # Mode in which vessel thikness will be generated solidify modifier
    else:
         ModeThikness="DoubleLayer"  # Mode in which vessel thikness will be generated double layer wall
#--------------------------------------------------------------------------------------
  
    #------------------------Create vessel random information---------------------------------------------------- 
    Vnum = np.random.randint(50)+3 #Number vertex in a layer/ring
    Vinc = (math.pi*2)/(Vnum) # difference of angle between vertex
    
    #--------------Generate information of vessel profile radius vs height---------------------------------
    rl, MaterialTopHeight, MaterialInitHeight,VesselHeight=CreateRadiusArray(MinH,MaxH,MinR,MaxR)      
     
     #----------------Set thiknesss for vessel wall/surface---------------------------------------
    VesselWallThikness=1000
    while(VesselWallThikness>np.max(rl)):
        if np.random.rand()<1:
              VesselWallThikness=(np.max(rl)/(11))*(np.random.rand()+0.1)
        else:
              VesselWallThikness=np.min(rl)*(np.random.rand()+0.1)/4# # Vessel thikness
    
    #-----------------------Set floor/bottum------------------------------------
    
    VesselFloorHeight=0
    if np.random.rand()<0.2:
           VesselFloorHeight= np.random.randint(np.max([1,np.min([int(MaterialInitHeight-VesselWallThikness),int(VesselHeight/9)])]))
           
           
               
           #VesselFloorHeight=int(VesselHeight/2)
           print("VesselFloorHeight"+str(VesselFloorHeight))
    
    #-------------------Scale Vessel-------------------------------------------------------
    VesselWallThikness*=ScaleFactor  
    VesselFloorHeight*=ScaleFactor      
    
    
    #-----------Strech deform of vessel out of cylindrical----------------------------------------------------------------------------------- 
    stx=sty=1   
    if np.random.rand()<0.04:
        if np.random.rand()<0.5:
             stx=np.random.rand()*0.8+0.2
        else: 
             sty=np.random.rand()*0.8+0.2
    #----------------------Content size this is the initial shape/mesh of the liquid inside the vessel------------------------------------------------------------
    if np.random.rand()<0.69:
        MatX_RadRatio=1-(np.random.rand()**1.3)*0.9
        MatY_RadRatio=1-(np.random.rand()**1.3)*0.9 # Ratio of the material radius compare to 
    else:
        MatX_RadRatio=0.97
        MatY_RadRatio=0.97 # Ratio of the material radius compare to \
        MaterialInitHeight = VesselFloorHeight+1
    if np.random.rand()<0.1:
         MaterialInitHeight = VesselFloorHeight+1

  #--------------------make sure material/content mesh is above vessel floor-------------------
    if MaterialInitHeight <= VesselFloorHeight: 
         MaterialInitHeight = VesselFloorHeight+1
    if MaterialTopHeight <= MaterialInitHeight+3:
         MaterialTopHeight=MaterialInitHeight+3
     
#======================Add Vertex for vessel/ vessel opening/ and conenten meshes==================================   
    #---------------------------Vessel openining vertex-----------------------------------------------
    Openverts = [] # openning in vessel mouth
    Openfaces = []
    Openedges = []
    #---------------------------Material/content mesh---------------------------------------------------------------------
    Matverts = []
    Matfaces = []
    Matedges = []
    #-----------------------Create vertex object and faces arrays for vessel------------------------------------------------------------------
    verts = []
    faces = []
    edges = []
    
    
    
    
    #=============================Add vertexesx=======================================================
    
    MaxXY=0

    MaxZ=0
    for fz in range(len(rl)):
        for j in range(0,Vnum ):
            theta=j*Vinc
            r1=rl[fz]
            x = (r1 * math.cos(theta))*stx*ScaleFactor
            y = (r1 * math.sin(theta))*sty*ScaleFactor
            z = fz*ScaleFactor #scale * (r2 * math.sin(phi))
            MaxZ=np.max([z,MaxZ])
            MaxXY=np.max([x,y,MaxXY])
    
         #   print(x)
            vert = (x,y,z)  # Add Vertex
            verts.append(vert) # Add to vessel vertexes
            Mvert = (x* MatX_RadRatio,y* MatY_RadRatio,z)  # 
            if fz<=MaterialTopHeight and fz>=MaterialInitHeight: # Material/content inside vessel
                  Matverts.append(Mvert)
            if fz==len(rl)-1: # opening of vessel
                  Openverts.append(vert)
# ...................Inner walll if the vessel surface is double layered-----------------------------
    if  ModeThikness=="DoubleLayer":
        if VesselFloorHeight==0:  VesselFloorHeight=1
        for fz in range(len(rl)-1,np.max([int(VesselFloorHeight-1),1]),-1):
            for j in range(0,Vnum ):
                theta=j*Vinc
                r1=rl[fz]-VesselWallThikness
                x = (r1 * math.cos(theta))*stx*ScaleFactor
                y = (r1 * math.sin(theta))*sty*ScaleFactor
                z = fz*ScaleFactor #scale * (r2 * math.sin(phi))
                MaxZ=np.max([z,MaxZ])
                MaxXY=np.max([x,y,MaxXY])
                vert = (x,y,z)  # Add Vertex
                verts.append(vert)
    
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
    if np.random.rand()<0.85:
        face = (0,)
        faceTop=(VesselFloorHeight*Vnum,) # face of top floor
        for k in range(1,Vnum):
            face += (k,)
            faceTop += (k+VesselFloorHeight*Vnum,)
        if VesselFloorHeight>0: faces.append(faceTop) 
        faces.append(face) 
        Matfaces.append(face)
        Openfaces.append(face)
        
    #------------content top as as a single single face-------------------------------------------        
    face = (len(Matverts)-Vnum-1,)
    for k in range(len(Matverts)-Vnum,len(Matverts)):
        face += (k,)
    Matfaces.append(face) 
#***************************************************************************
                
#*******************************************************************************
  
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
    #"create mesh from python data"
    print("create mesh from python data")
    mymesh.from_pydata(verts,edges,faces)
    mymesh.update(calc_edges=True)

    bpy.data.objects[VesselName].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["Vessel"]
    bpy.context.view_layer.objects.active = bpy.data.objects[VesselName]
    #bpy.context.object=bpy.data.objects['supershape'
    #-----------------------------------------------------------------------------------------------------------------
    #              Add modifiers to vessel
    #----------------------Add modifiers to vessel to smooth and i----------------------------------------------------------
    SubdivisionLevel=-1
    Smooth=False   
    if np.random.rand()<0.9:
        bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
        SubdivisionLevel=np.random.randint(4)
        SubdivisionRenderLevel=np.random.randint(4)
        bpy.context.object.modifiers["Subdivision"].levels = SubdivisionLevel
        bpy.context.object.modifiers["Subdivision"].render_levels = SubdivisionRenderLevel
    if np.random.rand()<0.9:    
        bpy.ops.object.shade_smooth() # smooth 
        Smooth=True
    if  ModeThikness=="Solidify": # Add vessel thikness usiing solidify modifier
         bpy.ops.object.modifier_add(type='SOLIDIFY')# Set Vessel thikness 
         bpy.context.object.modifiers["Solidify"].thickness = VesselWallThikness
     
    #===================================================================================
    #-------------------------------------Add content object------------------------------------------------------------------------------------     
    #create mesh and object
    mymesh = bpy.data.meshes.new(ContentName)
    myobject = bpy.data.objects.new(ContentName,mymesh)
     
    #set mesh location
    myobject.location=(0,0,0)
    bpy.context.collection.objects.link(myobject)
    #bpy.context.scene.objects.link(myobject)
     
    #create material mesh from python data

    print("create material mesh from python data")
    mymesh.from_pydata(Matverts,Matedges,Matfaces)
    mymesh.update(calc_edges=True)

    bpy.data.objects[ContentName].select_set(True)
    #...............................Add modifier to content object........................................
    #bpy.context.scene.objects.active = bpy.data.objects["Vessel"]
    bpy.context.view_layer.objects.active = bpy.data.objects[ContentName]
    if SubdivisionLevel>0: # Smooth
        bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
        bpy.context.object.modifiers["Subdivision"].levels = SubdivisionLevel
        bpy.context.object.modifiers["Subdivision"].render_levels = SubdivisionRenderLevel
    if Smooth: bpy.ops.object.shade_smooth() # smooth 
    #===================================================================================
    #-------------------------------------Add Vessel opening plate as an object------------------------------------------------------------------------------------     
    mymesh = bpy.data.meshes.new("VesselOpenning")
    myobject = bpy.data.objects.new("VesselOpenning",mymesh)
     
    #set mesh location
    myobject.location=(0,0,0)
    bpy.context.collection.objects.link(myobject)
    #bpy.context.scene.objects.link(myobject)
     
    #create mesh from python data


    mymesh.from_pydata(Openverts,Openedges,Openfaces)
    mymesh.update(calc_edges=True)

    bpy.data.objects[ContentName].select_set(True)
    #bpy.context.scene.objects.active = bpy.data.objects["Vessel"]
    bpy.context.view_layer.objects.active = bpy.data.objects["VesselOpenning"]
    if SubdivisionLevel>0:
        bpy.ops.object.modifier_add(type='SUBSURF') # add more polygos (kind of smothing
        bpy.context.object.modifiers["Subdivision"].levels = SubdivisionLevel
        bpy.context.object.modifiers["Subdivision"].render_levels = SubdivisionRenderLevel
    if Smooth: bpy.ops.object.shade_smooth() # smooth 
    #===================================================================================

    return MaxXY,MaxZ,VesselFloorHeight,VesselWallThikness
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
    dic["Metalic"]=bsdf.inputs[4].default_value# = 5
    dic["Specular"]=bsdf.inputs[5].default_value# = 0.804545
    dic["Specular Tint"]=bsdf.inputs[6].default_value# = 0.268182
    dic["Roughness"]=bsdf.inputs[7].default_value# = 0.64
    dic["Anisotropic"]=bsdf.inputs[8].default_value# = 0.15
    dic["Anisotropic Rotation"]=bsdf.inputs[9].default_value# = 0.236364
    dic["Sheen"]=bsdf.inputs[10].default_value# = 0.304545
    dic["Sheen tint"]=bsdf.inputs[11].default_value# = 0.304545
    dic["Clear Coat"]=bsdf.inputs[12].default_value# = 0.0136364
    dic["Clear Coat Roguhness"]=bsdf.inputs[13].default_value #= 0.0136364
    dic["IOR"]=bsdf.inputs[14].default_value# = 3.85
    dic["Transmission"]=bsdf.inputs[15].default_value# = 0.486364
    dic["Transmission Roguhness"]=bsdf.inputs[16].default_value# = 0.177273
    dic["Emission"]=bsdf.inputs[17].default_value[:]# = (0.170604, 0.150816, 0.220022, 1)
    dic["Emission Strengh"]=bsdf.inputs[18].default_value
    dic["Alpha"]=bsdf.inputs[19].default_value
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

#                     Delete object 

###############################################################################################################################
def DeleteObject(name):
     print("================= Deleting object "+name+"=========================================================") 
     bpy.data.meshes.remove(bpy.data.meshes[name])
###################################################################################################################
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
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1-0.2*RandPow(3) # Transmission
    else:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1 #Transmission
       
       
    if np.random.rand()<0.2: # Roughnesss
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.2*RandPow(3) # Roughness
    else: 
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0# Roughness
  
 
   
       
    if np.random.rand()<0.6:# ior index refraction
         bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 1.45+np.random.rand()*0.55 #ior index of reflection for transparen objects  
    
    else:
        bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 1.415+np.random.rand()*0.115 #ior index of reflection for transparen objects  
    #https://pixelandpoly.com/ior.html

    if np.random.rand()<0.3:# transmission rouighness
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0.22*RandPow(3) # transmission rouighness
    else: 
        bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0 # transmission rouighness
    

    if np.random.rand()<0.12: # Metalic
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[4].default_value = 0.3*RandPow(3)# metalic
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[4].default_value =0# meralic
      
      
    if np.random.rand()<0.12: # specular
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[5].default_value = np.random.rand()# specular
    elif np.random.rand()<0.6:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[5].default_value =0.5# specular
    else:
      ior=bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[14].default_value# specular
      specular=((ior-1)/(ior+1))**2/0.08
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[5].default_value=specular
      
    if np.random.rand()<0.12: # specular tint
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[6].default_value = np.random.rand()# tint specular
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[6].default_value =0.0# specular tint
  
    if np.random.rand()<0.12: # unisotropic
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[8].default_value = np.random.rand()# unisotropic
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[8].default_value =0.0# unisotropic
  
    if np.random.rand()<0.12: # unisotropic
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[9].default_value = np.random.rand()# unisotropic rotation
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[9].default_value =0.0# unisotropic
    
    if np.random.rand()<10.15:
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0.25*RandPow(3) # transmission rouighness
    else: 
        bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0 # transmission rouighness
    

    if np.random.rand()<0.1: # Clear  coat
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[12].default_value = np.random.rand()
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[12].default_value =0# 

    if np.random.rand()<0.1: # Clear  coat
       bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[13].default_value = np.random.rand()
    else:
      bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"].inputs[13].default_value =0.03# 
    bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[10].default_value = 0
    bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"].inputs[11].default_value = 0.5

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
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[15].default_value = np.random.rand() # Transmission
    else:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1 #Transmission
    if np.random.rand()<0.8:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[7].default_value = np.random.rand()*np.random.rand()# Roughness
    else: 
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0# Roughness

    if np.random.rand()<0.9: # color
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1) # random color hsv
    else:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1,1, 1) # white color
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[4].default_value = np.random.rand() # metalic
    elif np.random.rand()<0.5:
      bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[4].default_value =0# metalic
    else:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[4].default_value =1# metalic


    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[8].default_value = np.random.rand()# unisotropic
    else:
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[8].default_value = 0# unisotropic
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[9].default_value = np.random.rand()# unisotropic rotation
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0# unisotropic rotation
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[10].default_value = np.random.rand()# sheen
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[10].default_value = 0# sheen
    if np.random.rand()<0.4:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[11].default_value = np.random.rand()# sheen tint
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[11].default_value = 0.5# sheen tint
    
 
  
    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 1+np.random.rand()*2.5 #ior index of reflection for transparen objects  
    #https://pixelandpoly.com/ior.html
    
    
    if np.random.rand()<0.2:
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[16].default_value = np.random.rand()**2*0.4# transmission rouighness
    else: 
        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0 # transmission rouighness
    
    if np.random.rand()<0.015: # Emission
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[17].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1)# Emission
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[18].default_value = (np.random.rand()**2)*100 # Transmission strengh
    else: 
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[17].default_value = (0, 0,0, 1)## transmission rouighness
       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 1# Transmission strengh
      
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


#############################################################################################################

#         Create cube for the liquid domain

##############################################################################################################

def CreateDomainCube(name,scale):
       print("================= Creating liquid domain CUBE: "+name+"=========================================================")
       bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, int(scale[2]/2)), scale=scale)
       OriginName=bpy.context.object.name
       bpy.context.object.name = name
       bpy.data.meshes[OriginName].name = name
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
       xyz[2]=MinZ+np.random.rand()*((MaxZ-MinZ)-RadScale/2)  #MinZ+np.random.rand()*(MaxZ-MinZ)-RadScale/2
       xyz[1]=0#(R-RadScale)*np.random.rand()-(R-RadScale)
       xyz[0]=0#(R-RadScale)*np.random.rand()-(R-RadScale)
       ContentNames.append(LoadRandomObject(ObjectList,RadScale,xyz))
       
       
    ContentNames=MergeObjects(ContentNames,"MeshInsideVessel") # Merge all objects in the vessel into one object

    return ContentNames
    
##############################################################################################################################

#                   Write camera parameters to dicitonary (for saving to file)

##############################################################################################################################   
def CameraParamtersToDictionary():
    dic={}
    dic['name']=bpy.context.object.name #= name    
    dic['Focal Length']=bpy.context.object.data.lens #= lens
    dic['Location']=bpy.context.scene.camera.location[:]#=location
    dic['Rotation']=bpy.context.scene.camera.rotation_euler[:]#=rotation
    dic['Perseption']=bpy.context.scene.camera.data.type #= 'PERSP'
    dic['shift_x']=bpy.context.scene.camera.data.shift_x#=shift_x
    dic['shift_y']=bpy.context.scene.camera.data.shift_y#=shift_y
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
     shift_x=0.2-np.random.rand()*0.4
     shift_y=0.2-np.random.rand()*0.4
     SetCamera(name="Camera", lens = Focal, location=(x,y,z),rotation=(rotx, roty, rotz),shift_x=shift_x,shift_y=shift_y)
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
        ReplacePBRbyBSDFMaterials() # PBR material doesnt give good normals replace them
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
        
        ReplacePBRbyBSDFMaterials(Inverse=True) # Replace back to the original PBR material
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

#################################################################################################################################

#                          Export object as GTLF

#################################################################################################################################
def ExportObjectAsGTLF(ObjectName,FileName,Frame=0):
    print("--------------------------Saving Object as GTLF   "+str(Frame)+"----------------------------------------------") 
    bpy.context.scene.frame_set(Frame)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[ObjectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[ObjectName] 
    bpy.ops.export_scene.gltf(export_format='GLTF_EMBEDDED',filepath=FileName, export_selected=True, export_apply=True)
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
OutFolder=r"OutPut/"# Where output images will be saved

LiquidContentFractionOfCases=0.3 # Fraction of images that will be generated with liquid simulation inside the vessel, the rest will be created with objects inside the vessel
NumSimulationsToRun=1              # Number of simulation to run

SaveObjects=True # Do you want to save vessel and content as objects, some of these filese can  be large
#==============Liquid simulation parameters==============================================================
SurfaceDisance=0.7 # Increase to avoid leaks
MaxSubDivisionResolution=65
MinSubDivisionResolution=64

MaxTimeStep=18 # To Avoid leaking
MinTimeStep=4 # Avoid leaking and improve precision

#==============Set Rendering engine parameters (for image creaion)==========================================

bpy.context.scene.render.engine = 'CYCLES' # Use this configuration if you want to be able to see the content of the vessel (eve does not support content)
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
    ObjectList=CreateObjectList(ObjectFolder)

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
    CleanScene()  # Delete all objects in scence
  
#    #------------------------------Create random vessel object and assign  material to it---------------------------------
    MaxXY,MaxZ,MinZ,VesselWallThikness=AddVessel("Vessel","Content",ScaleFactor=1)#np.random.rand()+0.1) # Create Vessel object named "Vessel" and add to scene also create mesh inside the vessel ("Content) which will be transformed to liquid
    VesselMaterial=AssignMaterialToVessel("Vessel") # assign random material to vessel object

   #-------------------------------------------Create ground plane and assign materials to it----------------------------------
    if np.random.rand()<0.8:
        PlaneSx,PlaneSy=AddGroundPlane("Ground",x0=0,y0=0,z0=-VesselWallThikness*(np.random.rand()*0.75+0.25)-0.1,sx=MaxXY,sy=MaxXY) # Add plane for ground
        if np.random.rand()<0.95:
            AssignPBRMaterialForObject("Ground",PBRMaterialsFolder) # Assign PBR material to ground plane (Physics based material) from PBRMaterialsFolder
        else: 
            AssignMaterialBSDFtoObject(ObjectName="Ground",MaterialName="BSDFMaterial") 
    else: 
        with open(OutputFolder+'/NoGroundPlane.txt', 'w'): print("No Ground Plane")
        PlaneSx,PlaneSy=MaxXY*(np.random.rand()*4+2), MaxXY*(np.random.rand()*4+2)
#------------------------Load background hdri---------------------------------------------------------------   
    AddBackground(HDRI_BackGroundFolder) # Add randonm Background hdri from hdri folder

#..............................Create load objects into scene background....................................................
    LoadNObjectsToScene(ObjectList,AvoidPos=[0,0,0],AvoidRad=MaxXY,NumObjects=np.random.randint(11),MnPos=[-PlaneSx,-PlaneSy,-5],MxPos=[PlaneSx,PlaneSy,0],MnScale=(np.random.rand()*0.8+0.2)*MaxXY,MxScale=np.max([MaxXY,MaxZ])*(1+np.random.rand()*4))    

##################################Create vessel content could be a liquid or object##########################################
#------------------Put random objects in the vessel-----------------------------------------------------------------
    if np.random.rand()<1-LiquidContentFractionOfCases:
            ContentMode="Objects"
      

            ContentNames=LoadNObjectsInsideVessel(ObjectList,MaxXY-VesselWallThikness,MinZ,MaxZ,NumObjects=np.random.randint(10)) # Put random objects in vessel
         
            if  np.random.rand()<0.5:
                if np.random.rand()<0.8:
                     for nm in ContentNames:
                           print(nm)
                           ContentMaterial=AssignMaterialBSDFtoObject(ObjectName=nm, MaterialName="BSDFMaterialLiquid")  # Assign single bsdf material to all object in the vessel
                else: 
                     for nm in ContentNames: 
                           ContentMaterial=AssignTransparentMaterial(ObjectName=nm, MaterialName="TransparentLiquidMaterial") # assign transparent material to all object in the vesssel
            FramesToRender=[0] 
  
#..............................Create scene with liquid in vessels.....................................................
    else:
        ContentNames=["LiquidDomain"]
        CreateDomainCube(name="LiquidDomain",scale=(MaxXY*2, MaxXY*2, MaxZ)) # Create Cube that will act as liquid domain
        if np.random.rand()<0.5:
              ContentMaterial=AssignMaterialBSDFtoObject(ObjectName="LiquidDomain", MaterialName="BSDFMaterialLiquid")  # assign material to liquid
        else: 
              ContentMaterial=AssignTransparentMaterial(ObjectName="LiquidDomain", MaterialName="TransparentLiquidMaterial") #Assign material for the object domain (basically the material of the liquid)
    #    print("Create simulation")
        TurnToLiquid("Content",VesselThinkness=VesselWallThikness) # Turn Content mesh into liquid
        TurnToEffector("Vessel",SurfaceDisance) # Turn Vessel into liquid effector (will interact with liquid as solid object)
        TurnToDoman("LiquidDomain",CatcheFolder=CatcheFolder,Bake=True,EndFrame=151,resolution=SubDivResolution,MaxTimeStep=TimeStep,MinTimeStep=MinTimeStep, Smooth=True) # Turn domain Cube into domain and bake simulation (Time consuming)
        FramesToRender=[30,65,100,150] # Liquid is dynamic so several frames will be rendered
        ContentMode="Liquid"
    #break
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
    DeleteObject("Content") # Delete the liquid  object (The liquid that was generated in the simulation is attached to the LiquidDomain and will not be effected
    HideObject("VesselOpenning",Hide=True)
    
    RandomlySetCameraPos(name="Camera",VesWidth = MaxXY,VesHeight = MaxZ)
    with open(OutputFolder+'/CameraParameters.json', 'w') as fp: json.dump(CameraParamtersToDictionary(), fp)
    
#------------------------------------------------------Save Objects to file-----------------------------------------------------
    if SaveObjects:
        ExportObjectAsGTLF("Vessel",OutputFolder+"/Vessel",Frame=0) # Save vessel as object
        for indx, ObjectName in enumerate(ContentNames): # Save Vessel Content as object
              for frm in FramesToRender:
                   ExportObjectAsGTLF(ObjectName,OutputFolder+"/ContentObject"+str(indx)+"_Frame_"+str(frm),Frame=frm)
#-------------------------------------------------------Save images--------------------------------------------------------------    
 
    print("Saving Images")
    print(OutputFolder)
    RenderImageAndSave(FileNamePrefix="VesselWithContent",FramesToRender=FramesToRender,OutputFolder=OutputFolder) # 
    HideObject("Vessel",Hide=True)
    RenderImageAndSave(FileNamePrefix="Content",FramesToRender=FramesToRender,OutputFolder=OutputFolder) # Render images and Save vessel content with no vessel
    
    HideObject("Vessel",Hide=False)
    for nm in ContentNames:  HideObject(nm,Hide=True)
    RenderImageAndSave(FileNamePrefix="EmptyVessel",FramesToRender=[0],OutputFolder=OutputFolder) # Render images and Save abd scene
    
    HideObject("Vessel",Hide=True)
    RenderImageAndSave(FileNamePrefix="Plane",FramesToRender=[0],OutputFolder=OutputFolder) # Render images and Save Plane and scene with no vessel or image 
    
    #------------------------Save vessel opening plane----------------------------------------------------------------------------------------------
    # Save Vessel opening
    print("Saving Vessel Opening")
    HideObject("VesselOpenning",Hide=False)
    objs=[]
    for nm in bpy.data.objects: objs.append(nm)
    for nm in objs: 
        if nm.name!='VesselOpenning' and nm.name!='Camera': 
            bpy.data.objects.remove(nm)
    RenderDepthNormalAndImageToFiles(OutputFolder,"VesselOpening", RenderImage=False,RenderDepth=True,RenderNormal=True)
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