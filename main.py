import os, sys, glob, random, cv2, numpy


for infile in glob.glob("public/images/*.[jJ][pP][gG]")+glob.glob("public/images/*.[jJ][pP][eE][gG]"):
	f = open('source_info.txt', 'a')
	#We first process the filename and determine the label value
	label_val = 0
	if infile[infile.rfind('.')-1] == '0':
		label_val = 0
	else:
		label_val = 1
	#Next we read the image and display it
	an_image = cv2.imread(infile, 1)  # read the image
	cv2.namedWindow(infile,cv2.WINDOW_NORMAL)
	cv2.imshow(infile,an_image) # display the image in the window already declared
	cv2.waitKey(3000)                   # wait for the user to press a key
	cv2.destroyAllWindows()
	'''
	while True:
		stain_type = raw_input("Please enter the stain type for "+infile+" : RBC or WBC or none : ... ")
		if stain_type == "RBC" :
			break
		if stain_type == "rbc" :
			stain_type = "RBC"
			break
		if stain_type == "WBC":
			break
		if stain_type == "wbc":
			stain_type = "WBC"
			break
		if stain_type == "none":
			break
		print("Invalid input ..",stain_type," Please enter the stain type again (RBC/WBC/none)... ")
	# end of while loop
	if stain_type == "none":
		continue
	# end of if
	'''
	stain_type = "WBC" #for debugging we have shorted it out
	# We start the actual processing of the image to extract data from it
	blur_image = cv2.medianBlur(an_image, 5)
	edges = cv2.Canny(blur_image, 25, 60)
	ret,thresh = cv2.threshold(edges,127,255,0)
	_,contours,_ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	#The generated image will show a very large number of sub countours representing the main object.
	#We now run a clustering algorithm that combines all contours with following logic : (Thanks to Will Stewart post in OpenCV forum)

	for i in range(0,len(contours)):
		area = cv2.contourArea(contours[i])
		if area < 30:
			cv2.drawContours(an_image,contours,i,(0,255,0),1)
		else :
			cv2.drawContours(an_image, contours, i, (0, 255, 0), 2)

	cv2.namedWindow("circles", cv2.WINDOW_NORMAL)
	cv2.imshow("circles", an_image)

	cv2.waitKey(7000)
	cv2.destroyAllWindows()

	height_width = an_image.size  #get the image height and width
	f.write(infile+" "+str(label_val)+" "+stain_type+" "+str(height_width)+"\n")
	#print ("debug : wrote "+infile+" "+str(label_val)+" "+stain_type+" "+str(height_width)+"\n")
f.close()