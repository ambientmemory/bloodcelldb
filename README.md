# bloodcelldb
Visual Databases project that uses machine learning to identify whether images of blood slides contain acute erythroid leukemia or not. 

#####Training Set Creation:
Data sourced from: http://imagebank.hematology.org/ as well as http://library.med.utah.edu/WebPath/HEMEHTML/HEMEIDX.html#6
* How to create/use this dataset:
  * First, we run a resizing script that forces each image into a 300x300 thumbnail (consistency in processing)
  * The infected images and the healthy images are spearately resized and labeled with either 'L' or 'N' headings (refer to img_proc_leuk.py for details)
  * Some healthy and some infected cells are selected from the pool and then a renaming/label-creating script is run to randomize their names as well as assign a 0-1 label for further supervised learning.


#####TODO:
* UI:
    * Test with real response from server
* Server:
    * Call Python on the uploaded files by passing them via the command line
    * Test writing to SQL
* ML Proc:
    * Test