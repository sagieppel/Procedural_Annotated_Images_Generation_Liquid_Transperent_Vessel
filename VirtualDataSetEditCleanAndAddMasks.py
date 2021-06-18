
#---------------------------------------Finalized dataset add segmentation masks ------------------------------------------------------------------
import cv2
import numpy as np
import os
import shutil

#----------------------Input parameters--------------------------------------------------------------------------
#input folder where the generated dataset is
MainDir= r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/OutObjectSupportedGTB_OpeningFixed_NONECentarFullCameraParamters//"

#------------------Remove incomplete---------------------------------------------------------------
count=0
for InDir in os.listdir(MainDir):
    InDir = MainDir + "//" + InDir
    if os.path.isdir(InDir) and not os.path.exists(InDir + "//Finished.txt"):
            shutil.rmtree(InDir)
            count+=1
print("Remove ", count, 'incomplete folders ')
#--------------------------------Create masks and additional data--------------------------------------------------------------
for InDir in os.listdir(MainDir):
    InDir= MainDir+"//"+InDir
    if os.path.isdir(InDir) and os.path.exists(InDir+"//Finished.txt"):
        print(InDir)
    #----------------------------------------Create PNG depth map---------------------------------------------------------------------------------
        fl=open(InDir+"/DepthNormalizationForPNG.txt","w")
        fl.write("File_Name\tScale\tMin_Dist\t(Real_Depth=PNG_Depth*Scale+Min_Dist)\n")

        for nm in os.listdir(InDir):
            if "Depth.exr" in nm:
                I =cv2.imread(InDir + "//"+ nm,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH )

                OutNm= nm.replace("Depth.exr","Depth.png")


                MinDist=I.min()-2

                I-= MinDist
                I[I>10000]=0
                Scale=I.max()/255.0
                I=(I/Scale)
                I=I[:,:,0].astype(np.uint8)
                fl.write(OutNm+"\t"+str(Scale)+"\t"+str(MinDist)+"\n")
                cv2.imwrite(InDir+"//"+OutNm,I)
                # cv2.imshow(OutNm,I)
                # cv2.waitKey()
        fl.close()

        #----------------------------Find Vessel Mask-------------------------------------------------------------------------
        VesselDepth =cv2.imread(InDir + "//EmptyVessel_Frame_0_Depth.exr",  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH )[:,:,0]
        PlaneDepth =cv2.imread(InDir + "//Plane_Frame_0_Depth.exr",  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH )[:,:,0]
        VesMask=(PlaneDepth>VesselDepth).astype(np.uint8)*255
        cv2.imwrite(InDir+"//VesselMask.png",VesMask)



        VesselOpeningDepth =cv2.imread(InDir + "//VesselOpening_Depth.exr",  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH )[:,:,0]

        #-------------------------Create Content Map (inside, Outside, All)----------------------------------------------
        for nm in os.listdir(InDir):
            if ("Depth.exr" in nm) and ("Content_"==nm[:len("Content_")]):
                OutNm = nm.replace("Depth.exr", "Mask.png")
                ContentDepth = cv2.imread(InDir + "//" + nm, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[:,:,0]
                ContentMaskAll = (PlaneDepth > ContentDepth).astype(np.uint8) * 255 # All content even if outside vessel
                UndistortedContentMask = (VesselDepth > ContentDepth).astype(np.uint8) * 255 # any part of the content that is not viewed trough the vessel wall

                BeyondVesslWallContent = ContentMaskAll - UndistortedContentMask# any part of the content that is viewed trough the vessel wall
                TroughVesselOpening=UndistortedContentMask.copy()
                TroughVesselOpening[VesselOpeningDepth>10000] = 0
                # ContentMaskInsideVessel = ContentMaskAll.copy()
                # ContentMaskInsideVessel[VesMask==0]=0
                # ContentMaskInsideVessel[((UndistortedContentMask>0)*(VesselOpeningMask==0))>0]=0 # Every part of the content that is beyond the vessel wall or on the vessel cover
                BeyondVesslWallContent=np.expand_dims(BeyondVesslWallContent,axis=2)
                TroughVesselOpening=np.expand_dims(TroughVesselOpening,axis=2)
                UndistortedContentMask=np.expand_dims(UndistortedContentMask,axis=2)


                ContentMask=np.concatenate([BeyondVesslWallContent,TroughVesselOpening,UndistortedContentMask],axis=2)
                cv2.imwrite(InDir+"//"+OutNm,ContentMask)
