# Convert shapenet objects to gtlf in one folder
# Using https://github.com/CesiumGS/obj2gltf
# (note you need to install node.js before)
#npm install -g npm
#nvm install 12.18.3 
#npm install -g obj2gltf
# (Most be installed before)
# Shapenet: https://shapenet.org/ 

import os
MainDir=r"/home/chemargos/Downloads/ShapeNetCore.v2//" # input original shapenet
OutDir=r"/home/chemargos/Documents/ObjectGTLF//" # Output gtlf
if not os.path.exists(OutDir): os.mkdir(OutDir)
NumFile=0
for path, subdirs, files in os.walk(MainDir):
    for name in files:
        if ".obj" in name[-4:]:

            inPath=os.path.join(path, name)
            os.chdir(path)
            OutPath = os.path.join(OutDir, str(NumFile)+".gltf")
            NumFile+=1
            if os.path.exists(OutPath):continue
            CommandTxt='obj2gltf -i '+inPath+" -o "+OutPath
            print(CommandTxt)
            os.system(CommandTxt)

#os.system('ls -l')
