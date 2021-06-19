
#---------------------------------------Delete large objet glb file that take too much space (object GLB files take too much space and are not very usefull) ------------------------------------------------------------------
import cv2
import numpy as np
import os
import shutil

#----------------------Input parameters--------------------------------------------------------------------------
#input folder where the generated dataset is
MainDir= r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/OutObjectSupportedGTB_OpeningFixed_NONECentarFullCameraParamters_ConvertedForTrain//"

MaxFileSize=1000000# in byte one mb=10000000
#--------------------------------Remove GLB object files which are too big (to save dataset space)--------------------------------------------------------------
SumSize=0
SumFiles=0
for InDir in os.listdir(MainDir):
    InDir= MainDir+"//"+InDir
    for nm in os.listdir(InDir):
            if ".glb" in nm:
                filesize=os.stat(InDir+"/"+nm).st_size
                if filesize>MaxFileSize:
                    print("removing",InDir+"/"+nm,filesize)
                    os.remove(InDir+"/"+nm)
                    SumFiles+=1
                    SumSize+=filesize

print("Size removed ",SumSize/1000000," file remove",SumFiles)