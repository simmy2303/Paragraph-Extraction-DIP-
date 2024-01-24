# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:13:01 2023

@author: caqin
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

img_list = ["001.png","002.png","003.png","004.png","005.png","006.png","007.png","008.png"]
# img_list = ["005_2.png", "008_6.png"]

for i in img_list:
    # Read the image from the list
    img = cv2.imread(i, 0)

    # Threshold for considering pixels as black
    threshold = 64

    # Counting the number of black pixels along rows and columns
    horizontal_projection = np.sum(img < threshold, axis=1)
    vertical_projection = np.sum(img < threshold, axis=0)

    # Plot and save horizontal projection
    plt.plot(horizontal_projection)
    plt.title("Horizontal Projection")
    plt.xlabel("Pixel Position")
    plt.ylabel("Projection Value")
    plt.savefig(f"{i[:-4]}_horizontal_proj.png")  # Adjust the slicing to keep the original prefix
    plt.clf()  # Clear the plot for the next iteration

    # Plot and save vertical projection
    plt.plot(vertical_projection)
    plt.title("Vertical Projection")
    plt.xlabel("Pixel Position")
    plt.ylabel("Projection Value")
    plt.savefig(f"{i[:-4]}_vertical_proj.png")  # Adjust the slicing to keep the original prefix
    plt.clf()  # Clear the plot for the next iteration






