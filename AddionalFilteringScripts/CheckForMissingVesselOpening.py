#   checl if  the surface map of  the vessel opening is missing
import cv2
import numpy as np
import os
import shutil
MainDir=   r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/GeneratedLiquids/"
tr=0
import shutil
for ff,InDir in enumerate(os.listdir(MainDir)):

    InDir= MainDir+"//"+InDir
    if os.path.isdir(InDir) and os.path.exists(InDir+"//Finished.txt"):
        print(InDir)
    else:
        print("Error")
        break
    op=cv2.imread(InDir+"/VesselOpening_Depth.png")
    o = cv2.imread(InDir + "/VesselOpening_Depth.png",0)
    if len(np.unique(op))==1:
        # im = cv2.imread(InDir + "/EmptyVessel_Frame_0_RGB.jpg")
        # cv2.destroyAllWindows()
        # im[:,:,0][o>0]=0
        # cv2.imshow("Remove/Keep "+str(ff),np.hstack((op,im)))
        # x=cv2.waitKey()
        shutil.rmtree(InDir)
        print(InDir)
        tr+=1
    print(str(tr/(ff+0.00001))+"   "+str(ff))
