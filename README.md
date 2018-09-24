# Image and Video Annotation Tool #
@author: frozenscrypt

Tool is under maintenance and feature additions with video annotation script coming soon!

### Uses python 3 ###
## Installations: ##
### For ubuntu users ###
* sudo apt-get install python-tk
* sudo apt-get isntall opencv-python
* pip install Pillow

### For windows users, exe file will be updated shortly! ###

## Instructions: ##

* GUI utilizes images numbered starting from 1

* The bash script renames all images in a directory as needed.
	run rename_images.sh

* To run the GUI
	python image_annotation_gui.py path-to-configFile

Config-file is a json file with keys to specify the filename(input folder directory) , image folder name, output folder name, multiplier to scale the images as needed(<1), frame number or the initial image number( tells the gui from where to start the annotation process)

## Features: ##

* Allows to draw multiple boxes to a image
* Each time a box is drawn and a comment is added if needed, click submit to save the annotation
* Clear button allows to clear a faulty annotation but once submitted, it can't be cleared
* Next button calls the next image
* Previous button calls the previous image and deletes the previous annotation from the data file
* Log box displays the current operation on the current image


