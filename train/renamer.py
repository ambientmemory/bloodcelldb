import os, sys, glob, random
from PIL import Image

f= open('train_labels.txt', 'w')

for infile in glob.glob("*.jpg")+glob.glob("*.JPG"):
	
	print("Debug: infile:", infile)
	im = Image.open(infile)
	outfilename = str(random.randint(100000, 200000))
	newname = outfilename
	if infile.startswith('N'):
		outfilename = outfilename+" "+ "0" +"\n"
		print("Debug: outfilename: ", outfilename)
		f.write(outfilename)
	else:
		outfilename = outfilename+" "+ "1"+"\n"
		print("Debug: outfilename: ", outfilename)
		f.write(outfilename)
	im.save(newname+".jpg", "JPEG")		

f.close()