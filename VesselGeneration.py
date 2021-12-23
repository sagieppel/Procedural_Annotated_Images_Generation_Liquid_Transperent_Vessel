# Gennerate vessel mesh

#####################################################################

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import json
#####################################################################################3

# Random multiply

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r


###############################################################################################################################

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
        VesselHeight=np.random.randint(MaxH-MinH)+MinH # Height of vessel (number of layers
        
        MaterialTopHeight=int((np.random.rand()*(VesselHeight-1))+2) # Height og thec content material inside the vessel
        
        MaterialInitHeight=int(np.random.rand()*(MaterialTopHeight-1))
        if MaterialTopHeight>VesselHeight: MaterialTopHeight=VesselHeight
        if MaterialTopHeight<3: MaterialTopHeight=3
     
        if MaterialInitHeight>=MaterialTopHeight: MaterialInitHeight= MaterialTopHeight-1
       
     
    #------------------------------------------------------------------
        r=np.random.rand()*50+8 # Radius of the vessel at start
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
        for i in range(VesselHeight): # go layer by layer and change vessel raius
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
                 if np.random.rand()<swp/VesselHeight:
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
        return rl, MaterialTopHeight, MaterialInitHeight,VesselHeight   
##################################################################################################################333

#                          Create vessel Object 

####################################################################################################################
def AddVessel(VesselName="Vessel",ContentName="MaterialContent",MinH=4,MaxH=80,MinR=4,MaxR=40,ScaleFactor=0.1,SimpleLiquid=True):   
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
    if np.random.rand()<0.12:
        if np.random.rand()<0.5:
             stx=np.random.rand()*0.8+0.2
        else: 
             sty=np.random.rand()*0.8+0.2
    #----------------------Content size this is the initial shape/mesh of the liquid inside the vessel------------------------------------------------------------
    if np.random.rand()<0.68 and SimpleLiquid==False:  
        MatX_RadRatio=1-(np.random.rand()**1.3) # this will create small liqui blob that will squash inside the vessel
        MatY_RadRatio=1-(np.random.rand()**1.3) # Ratio of the material radius compare to 
    else:
        MatX_RadRatio=1
        MatY_RadRatio=1 # Ratio of the material radius compare to \
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
            Mvert = (x* MatX_RadRatio-VesselWallThikness* math.cos(theta),y* MatY_RadRatio-VesselWallThikness* math.sin(theta),z)  # 
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
    #######if np.random.rand()<0.85:
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
    face = (len(Matverts)-Vnum,)
    for k in range(len(Matverts)-Vnum+1,len(Matverts)):
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