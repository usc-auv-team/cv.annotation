#Image Annotation

import PIL
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os
import threading
import sys
import time
import numpy as np
import json
import os.path as ops
from os import path
import matplotlib.pyplot as plt
import ast



# config_path = "C:/users/vivek/Annotator/config_img_gui.json"


def init_args():
	global config_path
	parser = argparse.ArgumentParser()
	parser.add_argument('config_file', type=str, help = 'config file name',default = "")
	return parser.parse_args()
	# config = {"config_file":config_path}
	# return config


class Application:
	def __init__(self, output_path = path):
		# global config_path
		self.is_paused = False
		self.prev_x = 0 
		self.prev_y = 0
		self.x_topleft = 0
		self.y_topleft = 0
		self.prev_xtl = 0
		self.prev_ytl = 0
		self.x_bottomright = 0
		self.y_bottomright = 0
		self.prev_xbr = 0
		self.prev_ybr = 0
		self.x_live =  0
		self.y_live = 0
		self.prev_xl = 0
		self.prev_yl = 0
		self.points = []
		self.frame_no = 0
		self.global_image_frame = None
		self.log_list = []
		self.index = 0
		self.speed_ratio = 1
		self.text = []
		self.is_submit = False
		self.label = ''

		
		self.config = init_args()#{'config_file':config_path}#init_args()
		self.args = json.loads(open(self.config.config_file).read())
		# self.args = json.loads(open(self.config['config_file']).read())
		self.filename = self.args['filename']
		self.output_dir = self.args['output_dir']
		self.image_folder = self.args['image_folder']
		self.frame_no = self.args['frame_no']
		self.mul = self.args['mul']
		if not os.path.exists(self.output_dir):
			os.mkdir(self.output_dir)
		if not os.path.exists(self.output_dir + '/' + 'boxes'):
			os.mkdir(self.output_dir + '/' + 'boxes')
		if not os.path.exists(self.output_dir + '/' + 'detections'):
			os.mkdir(self.output_dir + '/' + 'detections')	

		self.log = open(self.output_dir + '/' + self.image_folder + '_log.txt','a')
		self.img_list =  [f for f in os.listdir(self.filename + '/' + self.image_folder + '/')]
		self.current_image = None  # current image from the camera

		self.root = tk.Tk()  # initialize root window
		self.root.geometry('1280x720')
		self.root.geometry("%dx%d+%d+%d" % (1280, 720, 0, 0))
		self.root.title("Test")  # set window title
		
		self.root.protocol('WM_DELETE_WINDOW', self.destructor)
		self.root.bind("<Right>",self.next_call)
		self.root.bind("<Left>",self.previous_call)
		self.root.bind("b",self.label_call)
		self.root.bind("q",self.label_call)
		self.root.bind("c",self.label_call)
		self.root.bind("s",self.submit)
		self.root.bind("x",self.clear)

		self.clear_button = tk.Button(self.root, text="Clear", command = self.clear)
		self.clear_button.place(x = 570, y = 50)
		self.next_button = tk.Button(self.root, text = 'Next', command = self.next_call)
		self.next_button.place(x = 700, y = 50)
		self.previous_button = tk.Button(self.root, text = 'Previous', command = self.previous_call)
		self.previous_button.place(x = 627, y = 50)
		
		self.panel = tk.Label(self.root)  # initialize image panel
		self.panel.place(x = 300, y = 100)
		self.panel2 = tk.Label(self.root)  # initialize panel for cropped image
		self.panel2.place(x = 50,y = 600)
		self.text_object = tk.Text(self.root,width = 50,height = 1)
		self.text_object.place(x = 300,y = 600)
		self.text_object.configure(font=("Times New Roman", 12, "bold"))
		self.text_object.insert(tk.END,'Comment')
		

		self.panel6 = tk.Button(self.root, text="Submit", command=self.submit)
		self.panel6.place(x = 850,y = 600)
		self.log_object = tk.Text(self.root,width = 50, height = 40)
		self.log_object.place(x = 1000,y = 100)
		self.log_object_text = tk.Label(self.root, text = 'PROCESS LOG')
		self.log_object_text.configure(font=("Times New Roman", 12, "bold"))
		self.log_object_text.place(x = 1000, y = 80)

		self.instr_text = tk.Label(self.root, text = 'PRESS b for buoy, q for qual gate, c for channel, s for submit, left-right for previous-next, x for clear')
		self.instr_text.configure(font=("Times New Roman", 12, "bold"))
		self.instr_text.place(x = 200, y = 650)
		
		self.root.config(cursor="arrow")
		self.readLogFile = open(self.output_dir + '/' + self.image_folder + '_log.txt','r').readlines()
		self.start = True

		self.video_loop()


	def video_loop(self):
		
		""" Get frame from the video stream and show it in Tkinter """
		if self.frame_no != 0 and self.start == True:
			try:
				self.index = self.img_list.index(str(self.readLogFile[-1].split('\t')[0])) + 1 
				self.start = False
			except:
				pass

		if len(self.readLogFile)!=0 and self.start == True:
			self.index = self.img_list.index(str(self.readLogFile[-1].split('\t')[0])) + 1 
			self.start = False


		if  not self.is_paused:
			self.frame_no = self.img_list[self.index].split('.')[0]
			self.frame = cv2.imread(self.filename + '/' + self.image_folder + '/' + self.img_list[self.index])
			if self.frame.size >= 640*360*3:
				self.mul = np.array([640,360])/np.array(self.frame.shape[-2::-1])
			else:
				self.mul = [1,1]

			self.global_image_frame = self.frame
			self.is_paused = True
			self.x_topleft,self.y_topleft,self.x_bottomright,self.y_bottomright,self.x_live,self.y_live = 0,0,0,0,0,0
		else:
			self.frame = self.global_image_frame

		cv2image = self.frame.copy() 
		r,col,ch = cv2image.shape
		cv2resized = cv2.resize(cv2image,fx = self.mul[0],fy = self.mul[1],dsize = (0,0))


		if True:  # frame captured without any errors
			self.panel.bind("<Button-1>",self.top_left_click)
			self.panel.bind("<ButtonRelease-1>",self.bottom_right_release)
			self.panel.bind("<B1-Motion>",self.mouse_movement)


			if (self.x_topleft, self.y_topleft)!=(self.prev_xtl, self.prev_ytl):
				self.prev_xtl,self.prev_ytl = self.x_topleft,self.y_topleft
				self.points = [(self.prev_xtl,self.prev_ytl)]
				self.is_paused = True
			if (self.x_bottomright, self.y_bottomright)!=(self.prev_xbr, self.prev_ybr) and self.is_paused:
				self.prev_xbr,self.prev_ybr = self.x_bottomright,self.y_bottomright
				self.points += [(self.prev_xbr,self.prev_ybr)]
				thread1 = threading.Thread(target=self.boundingbox,args=(cv2image,self.frame_no,self.points))
				thread1.start()

			if (self.x_live, self.y_live)!=(self.prev_xl, self.prev_yl):
				self.prev_xl, self.prev_yl = self.x_live, self.y_live
				cv2.rectangle(cv2resized,(self.x_topleft,self.y_topleft),(self.x_live,self.y_live),(0,255,0),1)

			if self.is_paused:
				cv2.rectangle(cv2resized,(self.x_topleft,self.y_topleft),(self.x_live,self.y_live),(0,255,0),1)


			self.current_image = Image.fromarray(cv2resized)  # convert image for PIL
			imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter 
			self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
			self.panel.config(image=imgtk)  # show the image
		self.root.after(40//self.speed_ratio, self.video_loop)  # call the same function after 30 milliseconds



	def trigger(self):
		self.log_object.insert(tk.END,'The Trigger is called for frame {}\n'.format(frame_no))
		thread2 = threading.Thread(target=self.api_calls)
		thread2.start()
		

	
	def boundingbox(self,image,frame_no,points):
		smallest_x = int(np.min([pt[0] for pt in points])/self.mul[0])
		smallest_y = int(np.min([pt[1] for pt in points])/self.mul[1])
		largest_x = int(np.max([pt[0] for pt in points])/self.mul[0])
		largest_y = int(np.max([pt[1] for pt in points])/self.mul[1])
		box_img = cv2.rectangle(image,(smallest_x,smallest_y),(largest_x,largest_y),(0,255,0))
		cv2.imwrite(self.output_dir + '/detections/' + '{}.jpg'.format(self.frame_no),box_img)
		cv2.imwrite(self.output_dir + '/boxes/' + '{}.jpg'.format(self.frame_no),
			self.frame[smallest_y:largest_y,smallest_x:largest_x])

		# Show cropped image on gui
		self.panel2 = tk.Label(self.root)  # initialize panel for cropped image
		self.panel2.place(x = 50,y = 600)
		img = cv2.resize(image[smallest_y:largest_y,smallest_x:largest_x],(100,100))
		current_image = Image.fromarray(img)  # convert image for PIL
		imgtk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter 
		self.panel2.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
		self.panel2.config(image=imgtk)  # show the image
		self.log_object.insert(tk.END,'The box for frame {} is created\n'.format(self.frame_no))
		box = [(smallest_x,smallest_y),(largest_x,largest_y)]
		self.log_list.append([self.frame_no + '.jpg',box])

	   
	def clear(self,character=''):
		print("RESUMING...")
		self.text_object.delete('1.0',tk.END)
		self.text_object.insert(tk.END,'Comment')
		try:
			for panel in self.panel_list:
				panel.destroy()
		except:
			pass
		try:
			self.panel2.destroy()
		except:
			pass
		self.is_paused = False
		if self.is_submit == False:
			self.log_list.remove(self.log_list[-1])
		self.x_topleft,self.y_topleft,self.x_bottomright,self.y_bottomright,self.x_live,self.y_live = 0,0,0,0,0,0



	def submit(self,character=''):
		
		commented_text = self.text_object.get('1.0',tk.END).split('\n')[0]
		print(self.label,'lalalala')
		if commented_text and self.label == '':
			self.text_object.delete('1.0',tk.END)
			self.text_object.insert(tk.END,'Comment')
			self.log_list[-1].append(commented_text)
		elif self.label:
			self.log_list[-1].append(self.label)
			self.label = ''

		try:
			for panel in self.panel_list:
				panel.destroy()
		except:
			pass
		try:
			self.panel2.destroy()
		except:
			pass

		self.is_paused = False
		self.is_submit = True
		self.x_bottomright,self.y_bottomright,self.prev_xbr, self.prev_ybr = 0,0,0,0

	#Top Left Click
	def top_left_click(self,event):
		self.x_topleft = event.x
		self.y_topleft = event.y
		self.is_submit = False

	#Bottom Right Mouse Release
	def bottom_right_release(self,event):
		self.x_bottomright = event.x
		self.y_bottomright = event.y

	#Mouse movements after click
	def mouse_movement(self,event):
		self.x_live = event.x
		self.y_live = event.y



	def set_delay(self):
		global delay
		delay = int(self.delay_text.get('1.0',tk.END).split('\n')[0])
		

	def next_call(self,character = ''):

		self.is_paused = False
		self.index+=1

	def previous_call(self,character=''):

		self.is_paused = False
		if self.index!=0:
			self.index-=1
		else:
			pass



	def destructor(self):

		""" Destroy the root object and release all resources """
		print("Last frame:",self.frame_no)
		print("[INFO] closing...")
		try:
			for line in self.log_list:
				print(line)
				self.log.write('{}\t{}\t{}\n'.format(line[0],line[1],line[2]))
		except:
			pass
		self.root.destroy()
		self.log.close()
	 
	def label_call(self,character=''):
		self.label = character.char
		print(self.label,'papapapap',type(self.label))

	
# start the app
print("[INFO] starting...")
pba = Application(path)	 
pba.root.mainloop()