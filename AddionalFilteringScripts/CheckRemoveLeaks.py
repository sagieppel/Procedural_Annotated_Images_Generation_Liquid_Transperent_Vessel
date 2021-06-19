
#---------------------------------------Delete cases where the object/liquid content is leaking outside the vessel-----------------------------------------------------------------
import cv2
import numpy as np
import os
import shutil
import vis
#----------------------Input parameters--------------------------------------------------------------------------
#input folder where the generated dataset is
MainDir= r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet//UnifiedLiquidDir/"
#------------------Remove incomplete---------------------------------------------------------------
count=0
for InDir in os.listdir(MainDir):
    InDir = MainDir + "//" + InDir
    if os.path.isdir(InDir) and not os.path.exists(InDir + "//Finished.txt"):
            shutil.rmtree(InDir)
            count+=1
print("Remove ", count, 'incomplete folders ')
#----------------------------------------------------------------------------------------------
kk=0
ff=0
for ff,InDir in enumerate(os.listdir(MainDir)):
    InDir= MainDir+"//"+InDir

#-------------------------Check for content mask that is mostly outside vessel----------------------------------------------
    rat=[]
    for nm in os.listdir(InDir):
            if ("Mask.png" in nm) and ("Content_"==nm[:len("Content_")]):

                ContenMap = cv2.imread(InDir + "//" + nm)

                BeyondWall =  ContenMap[:,:,0]# any part of the content that is viewed trough the vessel wall
                TroughOpening=ContenMap[:,:,1]
                UndistortedMask=ContenMap[:,:,2]
                CorrectSum=BeyondWall.sum()+TroughOpening.sum()
                TotalSum=UndistortedMask.sum()+BeyondWall.sum()

                rat.append((CorrectSum+0.0002)/(TotalSum+0.0001))
    if  np.max(rat)<0.3:
        print(InDir + "//" + nm.replace("Mask.png", "RGB.jpg"))
        im = cv2.imread(InDir + "//VesselWith" + nm.replace("Mask.png", "RGB.jpg"))
        shutil.rmtree(InDir)
        #im=cv2.imread(InDir + "//VesselWithContent_Frame_150_RGB.jpg")
        #
        # vis.show(np.hstack([im,ContenMap]),str(rat))
        # break
        kk+=1


    print(kk,ff,kk/(ff+1))