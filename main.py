import os, sys, glob, random, cv2
import numpy as np

global disease_tag, img, new_filename, f, no_of_stained_cells, stained_cells, output 
disease_tag = []
no_of_stained_cells = []
stained_cells = []
img = []
new_filename = [] 
f = open('database_file.txt', 'w')

def size_proc():
	global disease_tag
	global new_filename
	global img

	for infile in glob.glob("*.jpg")+glob.glob("*.JPG"):
		print('Debug: infile read in is: ', infile)
		outfile, ext = os.path.splitext(infile)	
		temp = cv2.cv.LoadImage(infile)
		cv2.imshow("input", temp)
		img = img.append(temp)
		outfilename = str(random.randint(100000, 200000))
		newname = outfilename 
		
		#TODO: How do I randomly assign diseases? 
		if infile.endswith('0.jpg'):
			disease_tag = disease_tag.append('healthy')
		elif infile.endswith('1.jpg'):
			disease_tag = disease_tag.append('lymphoc_leukemia')
		else: disease_tag = assign_a_sickness()
		
		small = cv2.resize(img, (300, 300))
		cv2.imwrite(newname+'.jpg', small)
		new_filename = new_filename.append(newname+'.jpg')

def rest_of_it():
	global no_of_stained_cells
	global stained_cells

	output = img.copy()
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# detect circles in the image
	circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, 5, 50)

	# ensure at least some circles were found
	if circles is not None:
		# convert the (x, y) coordinates and radius of the circles to integers
		circles = np.round(circles[0, :]).astype("int")
 		# loop over the (x, y) coordinates and radius of the circles
		for (x, y, r) in circles:
			# draw the circle in the output image, then draw a rectangle
			# corresponding to the center of the circle
			cv2.circle(output, (x, y), r, (0, 255, 0), 4)
			cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
 
	print('Debug: circles calculated with dimensions: ', len(circles[0]))
	#arbitrarily assingning the number of stained cells
	temp_circles = circles[0]
	no_of_stained_cells = no_of_stained_cells. append(random.randint(1, len(temp_circles)))
	print('Debug: no_of_stained_cells: ', no_of_stained_cells)
	stained_cells = stained_cells.append(temp_circles[0:no_of_stained_cells])

	cv2.imshow("output", output)
	cv2.waitKey(0)
	write_out()
	#f.write(outfilename)
#end of rest_of_them	

def write_out():
	global new_filename, f, disease_tag, no_of_stained_cells, stained_cells
	for i in range(len(new_filename)): 
		outfilename = new_filename(i)+" "+ str(no_of_stained_cells(i)) +" " +str(stained_cells(i))+" "+disease_tag(i)+"\n"
		print('Debug: outfilename final: ', outfilename)	
		f.write(outfilename)
	f.close()

def assign_a_sickness():
	list_diseases = ['thrombocytopenia', 'mononucleosis', 'healthy', 'anemia', 'thrombocythemia']
	return random.choice(list_diseases)
#end_of_assign_a_sickness

def main():
	size_proc()
	rest_of_it()

if __name__ == '__main__':
	main()





#for infile in glob.glob("*.jpg")+glob.glob("*.JPG"):
# saving resized image
# cv2.imwrite(newname+'.jpg', small)
#print('Debug: outfilename is now: ', outfilename, "; disease_tag: ", disease_tag)
# show the output image
#f.close()
