
#---------------------------------------Finalized dataset add segmentation masks ------------------------------------------------------------------
import cv2
import numpy as np
import os
import shutil
import shutil
#----------------------Input parameters--------------------------------------------------------------------------
#input folder where the generated dataset is
BaseDir=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet///"
indir=[]
indir.append(BaseDir+r"/OutputLiquidSupportedWithObject_CameraParametesFixed_CollisionDistance03//")
indir.append(BaseDir+r"/OutputLiquidSupportedWithObject_CameraParametesFixed//")
outdir=BaseDir+"/UnifiedLiquidDir/"
os.mkdir(outdir)

#--------------------------------Remove GLB object files which are too big (to save dataset space)--------------------------------------------------------------
i=1
for dr in indir:
    for sbDir in os.listdir(dr):
         pth=dr+"/"+sbDir
         if os.path.isdir(pth):
             print(pth,outdir+"/"+str(i))
             shutil.move(pth,outdir+"/"+str(i))
             i+=1
             print(i)

