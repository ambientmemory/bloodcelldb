import os, sys, glob
from PIL import Image

size = 300, 300

i = 1

for infile in glob.glob("*.jpg")+glob.glob("*.JPG"):
	outfile, ext = os.path.splitext(infile)
	#print("Outfile name: ", outfile)
	try:
		im = Image.open(infile)
		im.thumbnail(size, Image.ANTIALIAS)
		im.save(outfile+".jpg", "JPEG")
		i = i+1
		#Debug: print(i)
	except IOError:
		print ("cannot create thumbnail for ", infile)