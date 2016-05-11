import os, sys, glob, random, numpy
from sklearn import svm
from sklearn.externals import joblib

y = numpy.zeros(10) #put label_vals in here
stain_type_list =numpy.zeros(10)
count_of_cells = numpy.zeros(10)
count_of_stained = numpy.zeros(10)
line_no = 0

h = 0.02 #set the step size in the mesh
C = 1.0 #regularization parameter

if __name__ == "__main__":
    y, cell_type, count_of_cells, count_of_stained = numpy.loadtxt('source_info.txt',delimiter=' ', usecols=(1,2,4,5), unpack=True)
    y = numpy.asarray(y) #.reshape((len(y),1))
    count_of_cells = numpy.asarray(count_of_cells).reshape((len(count_of_cells),1))
    count_of_stained = numpy.asarray(count_of_stained).reshape((len(count_of_stained),1))
    cell_type = numpy.asarray(cell_type).reshape((len(cell_type),1))
    #Combining all the features together
    X = numpy.concatenate((count_of_cells, count_of_stained, cell_type), axis=1)
    #Calling SVMs
    svc = svm.SVC(kernel='linear',C=C).fit(X,y)
    #rbf_svc = svm.SVC(kernel='rbf', gamma=0.7, C=C).fit(X,y)
    #poly_svc=svm.SVC(kernel='poly', degree=3, C=C).fit(X,y)
    #lin_svc= svm.LinearSVC(C=C).fit(X,y)
    #  should be predicting the new things here
    svc_prediction = y-svc.predict(X)

    # should also be in testing
    svc_err = numpy.count_nonzero(svc_prediction)/svc_prediction.size
    print(svc_err)
    joblib.dump(svc,"svm_model.pkl")
