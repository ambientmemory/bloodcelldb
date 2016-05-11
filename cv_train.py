"""
Author : Piyali Mukherjee pm2678@columbia.edu
Date: 04/21/2016
This program sequentially finds all files that end with jpg, JPG, jpeg and JPEG filename extensions, then proceeds to
load the image and display it, then read in the file name and identify its training label, read its metadata to identify
its dimensions, and then ask the user whether this is RBC styained or WBC stained - or something else stained.
Once this data row is accumulated, this information is written down into source_info.txt database.
"""

import os, sys, glob, random, cv2, numpy

def merge_contour(i,j,i_x,i_y,j_x,j_y):
	'''
	This is a very critical and potentially time consuming step. We need to find the nearest point of the two contours, and then splice in the
	smaller area contour into larger area contour
	'''
	c_d = contours[i]
	c_s = contours[j]
	min_dist = numpy.Infinity
	min_i = 0
	min_j = 0
	for i in range(0,len(c_d)):
		for j in range(0,len(c_s)):
			dist = numpy.sqrt(numpy.square(c_d[i][0][0] - c_s[j][0][0]) + numpy.square(c_d[i][0][1] - c_s[j][0][1]))
			if dist < min_dist:
				min_dist = dist
				min_i = i
				min_j = j
	# Now that we have identified the point of insertion into destination the source, we create a new contour list, by copying all elements upto 'i'
	# from destination, then copying all elements from 'j' till end from source, then from '0' to 'j-1' of source, and finally the i+1th to end of destination
	new_c = []
	for k in range(0,min_i):
		new_c.append(c_d[k])
	for k in range(min_j,len(c_s)):
		new_c.append(c_s[k])
	for k in range (0,min_j):
		new_c.append(c_s[k])
	for k in range(min_i,len(c_d)):
		new_c.append(c_d[k])
	# Finally, we replace the contour 'i' with new_c, recompute the circle equivalent of new_c, and replace the data in contours_circles for index 'i'
	contours[i] = numpy.asarray(new_c)
	(new_x, new_y), new_radius = cv2.minEnclosingCircle(contours[i])
	new_circle_data_list = [new_x,new_y,new_radius]
	contours_circles[i] = new_circle_data_list
	return

def	overlap_contours(i,j):
	# Take the 'j'th contour, from the contours_sorted array, and the for every point of the 'j' check if its inside 'i' or on 'i' or outside 'i'
	# If we find that the contour 'j' is conpletely outside, we return -1, else if partially overlapped, we return 0, and if completely subsumed, we return +1
	completely_outside = True
	completely_subsumed = True
	for k in contours[j][0]: #for every point in contour 'j'
		k_loc = cv2.pointPolygonTest(contours[i],(k[0],k[1]),False)
		if k_loc == 0: #Its on the contour[i]
			completely_outside = False
			completely_subsumed = False
			break
		elif k_loc == -1: #Its not subsumed
			completely_subsumed = False
	# end of for
	if completely_subsumed == True:
		return(j)
	if completely_outside == False and completely_subsumed == False:
		return(-1) #on the border
	if completely_outside == True: # we test the reverse condition, thats the object 'i' might be subsumed completely within object 'i'
		completely_subsumed = True
		for k in contours[i][0]:  # for every point in contour 'i'
			if cv2.pointPolygonTest(contours[j], (k[0], k[1]), False) < 1:  # Its on or outside the contour[j]
				completely_subsumed = False
				break
		if completely_subsumed == True:
			return(i)
		else:
			return(-2)
	return(-1)

if __name__ == "__main__":
	for infile in glob.glob("images/*.[jJ][pP][gG]")+glob.glob("images/*.[jJ][pP][eE][gG]"):
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
		cv2.waitKey(1000)                   # wait for the user to press a key
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
		edges = cv2.Canny(an_image, 25.0, 30.0,3,L2gradient=True)
		#edges = cv2.dilate(edges,numpy.ones((1,1)),iterations=2)
		edges = cv2.erode(edges,numpy.ones((1,1)),iterations=2)
		_,contours,_ = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		contours = numpy.asarray(contours)
		#The generated image will show a very large number of sub countours representing the main object.
		#We now run a clustering algorithm that combines all contours that are located proximally. But we first delete all those
		#that are not convex shapes, or are too small to represent a blood cell
		contours_area = []
		i = 0
		while i < len(contours):
			ar = cv2.contourArea(contours[i])
			if ar < 20.0 :
				contours = numpy.delete(contours, i,0)
				continue
			else:
				contours_area.append(ar)
				contours[i] = cv2.convexHull(contours[i]) # replace the contour with its convext hull
			i += 1
		# Next we delete all the contours that are overlapping another contour - if we have a partial overlap, we remove the smaller area one
		sort_indices = numpy.argsort(contours_area)
		sort_indices = sort_indices[::-1] # reverse the sorting order
		contours = contours[sort_indices] #create a new view of sorted contours
		#Next we form the list of all enclosing circle data
		contours_circles = []
		for i in range(0, len(contours)):
			(x, y), radius = cv2.minEnclosingCircle(contours[i])
			circle_data_list = [x, y, radius]
			contours_circles.append(circle_data_list)  # stores as list of three floating point numbers
		# Now we detect overlaps
		i = 0
		while i < len(contours)-1:
			j = len(contours)-1
			while j > i:
				overlap = overlap_contours(i,j)
				if  overlap > -1: #completely subsumed
					contours = numpy.delete(contours,overlap,0)	#the function returns the index of the completely subsumed one
					contours_circles = numpy.delete(contours_circles,overlap,0)
					if overlap == i:
						break
				elif overlap == -1:
					merge_contour(i, j, contours_circles[i][0], contours_circles[i][1], contours_circles[j][0],
								  contours_circles[j][1])  # merges the contour j into i
					contours = numpy.delete(contours, j, 0)
					contours_circles = numpy.delete(contours_circles, j, 0)
				j -= 1
			if overlap != i:
				i += 1
		#end of outer while
		# We now draw the contours. We first identify if the mean colour intensity is towards the red, and if so we fill it with red, else green
		count_of_rbc = 0
		count_of_stained_rbc = 0
		for i in range(0,len(contours)):
			rect = cv2.minAreaRect(contours[i])
			center_color = an_image[int(rect[0][1]),int(rect[0][0])] #returns the colour of the center of the rectangular box containing the contour, the rect returns Y,X
			if center_color[1] < 30: # stained (G < 30
				cv2.drawContours(an_image,contours,i,(255,0,255),-1)
				count_of_stained_rbc += 1
			else:
				cv2.drawContours(an_image, contours, i, (0, 255, 0), -1)
				count_of_rbc += 1
		cv2.namedWindow("circles", cv2.WINDOW_NORMAL)
		cv2.imshow("circles", an_image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		height_width = an_image.size  #get the image height and width
		f.write(infile+" "+str(label_val)+" "+stain_type+" "+str(height_width)+" "+str(count_of_rbc)+" "+str(count_of_stained_rbc)+"\n")
		#print ("debug : wrote "+infile+" "+str(label_val)+" "+stain_type+" "+str(height_width)+"\n")
	#end of for loop for each image in training data directory
	f.close()
#end of main()
