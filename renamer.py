import os, sys, glob, random, cv2, numpy

def merge_contour(i,j,i_x,i_y,j_x,j_y):
	'''
	This is a very critical and potentially time consuming step. We need to find the nearest point of the two contours, and then splice in the
	smaller area contour into larger area contour
	'''
	ar_1 = cv2.contourArea(contours_sorted[i])
	ar_2 = cv2.contourArea(contours_sorted[j])
	if ar_1 > ar_2:
		d = i
		d_x = i_x
		d_y = i_y
		s = j
		s_x = j_x
		s_y = j_y
		ret_val = j
	else :
		d = j
		d_x = j_x
		d_y = j_y
		s = i
		s_x = i_x
		s_y = i_y
		ret_val = i
	# end of if
	c_d = contours_sorted[d]
	c_s = contours_sorted[s]
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
	# Finally, we replace the contour 'd' with new_c, recompute the circle equivalent of new_c, and replace the data in contours_circles for index 'd'
	#print("Debug : type of contours[d] "+str(type(contours[d]))+" and type of new_c is : "+str(type(new_c)))
	contours_sorted[d] = numpy.asarray(new_c)
	#print("Debug : type of contours[d] " + str(type(contours_sorted[d])))
	(new_x, new_y), new_radius = cv2.minEnclosingCircle(contours_sorted[d])
	new_circle_data_list = [new_x,new_y,new_radius]
	contours_circles[d] = new_circle_data_list
	return(ret_val)
"""
Author : Piyali Mikherjee pm2678@columbia.edu
Date: 04/21/2016
This program sequentially finds all files that end with jpg, JPG, jpeg and JPEG filename extensions, then proceeds to
load the image and display it, then read in the file name and identify its training label, read its metadata to identify
its dimensions, and then ask the user whether this is RBC styained or WBC stained - or something else stained.
Once this data row is accumulated, this information is written down into source_info.txt database.
"""
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
		blur_image = cv2.medianBlur(an_image, 5)
		edges = cv2.Canny(blur_image, 25, 60)
		_,contours,_ = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
		contours = numpy.asarray(contours)
		#The generated image will show a very large number of sub countours representing the main object.
		#We now run a clustering algorithm that combines all contours that are located proximally
		at_least_one_merger = False
		debug_pass_counter = 1
		while at_least_one_merger:
			at_least_one_merger = False
			print("Starting pass ",debug_pass_counter)
			contours_area = []
			for i in contours:
				contours_area.append(cv2.contourArea(i))
			sort_indices = numpy.argsort(contours_area)
			contours_sorted = contours[sort_indices]
			print(" count of contours : ",len(contours_sorted))
			# Next, for each contour, we create a list of enclosing circles, and corresponding radius
			contours_circles = []
			for i in range(0, len(contours_sorted)):
				(x, y), radius = cv2.minEnclosingCircle(contours_sorted[i])
				circle_data_list = [x, y, radius]
				contours_circles.append(circle_data_list)  # stores as list of three floating point numbers
			# Now we generate the proximity matrix of the (remaining) contours and identify those that can be merged. We keep this doing iteratively (a very slow process)
			# We genertate all intra contour distances
			proximal_array = numpy.zeros((len(contours_sorted),len(contours_sorted)))
			for i in range(0,len(contours_sorted)):
				for j in range(0,len(contours_sorted)):
					if (numpy.sqrt(numpy.square(contours_circles[i][0]- contours_circles[j][0]) + numpy.square(contours_circles[i][1] - contours_circles[j][1])) < 5) and (i != j):
						proximal_array[i][j] = 1
			# Now we scan this proximal array to find those that have a proximal entry, and once found, we "merge" the two contours, and delete the smaller one (lower index)
			row = 0  #We do this for every row, however, cannot be a for loop as the count of rowsd will reduce as we keep merging and deleting row/columns
			while row < proximal_array.shape[0]:    # For each row in proximal array
				#print("In pass ",debug_pass_counter," processing row no : ",row," out of max row size of : ",proximal_array.shape[0],"\n")
				if numpy.sum(proximal_array,axis=1)[row] == 0:  # There exists no element that is proximal to another element in this row
					row += 1
					continue
				index_of_non_zero = numpy.nonzero(proximal_array[row])
				col = index_of_non_zero[0][0]   # find the column number of the first non_zero element
				#We prepare to merge the element at index row to element at index col
				smaller = merge_contour(row,col,contours_circles[row][0],contours_circles[row][1],contours_circles[col][0],contours_circles[col][1]) # subsumes the smaller contour between i and j, and then accordingly replaces circle data
				proximal_array = numpy.delete(proximal_array,smaller,0) # delete row that is smaller in area between row 'row' and col 'col'
				proximal_array = numpy.delete(proximal_array,smaller,1) # and delete the corresponding column as well
				contours_circles = numpy.delete(contours_circles,smaller,0)
				contours_sorted = numpy.delete(contours_sorted, smaller,0)
				contours_area = numpy.delete(contours_area, smaller,0)
				contours = numpy.delete(contours, smaller,0)
				at_least_one_merger = True #the moment there is a single merger, we restart as the contours would have changed in size and alignment
			# end of while row < proximal_array.shape[0]
			debug_pass_counter += 1
			# end of while at_least_one_merger
		# We now draw the contours
		cv2.drawContours(an_image,contours,-1,(0,255,0),2)
		cv2.namedWindow("circles", cv2.WINDOW_NORMAL)
		cv2.imshow("circles", an_image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		height_width = an_image.size  #get the image height and width
		f.write(infile+" "+str(label_val)+" "+stain_type+" "+str(height_width)+"\n")
		#print ("debug : wrote "+infile+" "+str(label_val)+" "+stain_type+" "+str(height_width)+"\n")
	#end of for loop for each image in training data directory
	f.close()
#end of main()