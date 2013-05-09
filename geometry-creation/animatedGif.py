from PIL import Image, ImageSequence
import os, sys

frames = []

folderPath = sys.argv[1]

for i in range(50):

	curImage = folderPath + "\\image" + str(i) + ".png"

	im = Image.open(curImage)

	im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)

	frames.append(im)

from images2gif import writeGif

writeGif(folderPath + "animatedOutput.gif",frames,.1,0)






