# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 14:37:14 2023

@author: caqin
"""

# Importing required libraries
import cv2
import numpy as np

# Defining functions to avoid redundancy in code
def hist_projection(img):
    # Setting threshold for pixels values below 64 as black pixels
    threshold = 64

    # Counting the number of black pixels horizontally (axis=1) and vertically (axis=0)
    horizontal_projection = np.sum(img < threshold, axis=1)
    vertical_projection = np.sum(img < threshold, axis=0)

    return horizontal_projection, vertical_projection

def remove_table(image, horizontal_projection):
    max_pixels = np.max(horizontal_projection)

    # A table is identified,
    # if the maximum horizontal projection within the range of 
    # max_pixels-5 and max_pixels is found in exactly 5 rows. 
    # Set pixels to 255 to remove
    if np.count_nonzero((horizontal_projection >= max_pixels - 5) & (horizontal_projection <= max_pixels)) == 5:
        max_pixels_rows = [i for i in range(len(horizontal_projection)) 
                        if horizontal_projection[i] == max_pixels]
        image[max_pixels_rows[0]:max_pixels_rows[-1]+1,:] = 255
     
    return image
            
def find_columns(img, vertical_projection):

    # Initialising array to store the left and right boundaries of text columns
    # Set to zero by default
    col_boundaries = np.zeros((6), dtype='int32')
    
    condition = 0 # Flag to determine if current interation is reading the histogram of a text column. Zero when not in text column
    index = 0 # Flag to index col_boundaries. Increases by one everytime a boundary is identified
    col_gap = 0 # Variable to track gap size between histogram
    col_gap_threshold = 80 # Minimum gap size for a column to be identified
    
    for i in range(len(vertical_projection)):
        # Condition when left boundary of text column is identified
        if vertical_projection[i] >= 10 and condition == 0:
            col_boundaries[index] = i-padding # Adding left padding
            condition += 1
            index += 1
        # Condition when gap is found but threshold is not met
        elif vertical_projection[i] < 10 and condition == 1 and col_gap <= col_gap_threshold:
            col_gap += 1
        # Condition when new left boundary is found but threshold is not met
        elif vertical_projection[i] >= 10 and condition == 1 and col_gap <= col_gap_threshold:
            col_gap = 0
        # Condition when no new left boundary is found and threshold is met
        elif vertical_projection[i] < 10 and condition == 1 and col_gap > col_gap_threshold:
            col_boundaries[index] = i-col_gap_threshold+padding # Adding Right padding
            condition -= 1
            col_gap = 0
            index += 1
    
    return col_boundaries
    
# Global Variables
# Create a list to iterate through the images
img_list = ["001.png","002.png","003.png","004.png","005.png","006.png","007.png","008.png"] 
padding = 10 # Padding added to each paragraph extract for tidiness

#Main Loop
for i in img_list:
    # Read the image from the list
    img = cv2.imread(i,0)
       
    # Remove tables and images that span across all columns
    hor_proj_img, ver_proj_img = hist_projection(img)
    img = remove_table(img, hor_proj_img)
    hor_proj_img, ver_proj_img = hist_projection(img)
    
    # Identify column boundaries
    col_boundaries = find_columns(img, ver_proj_img)
    
    counter = 0 # Counter to sort paragraphs as they are extracted
    for c in range(0,6,2):
        if col_boundaries[c] != 0 : # Cycle through every left boundary identified
        
            # Extract the column
            col_img = img[:,col_boundaries[c]:col_boundaries[c+1]]
            
            hor_proj_col, ver_proj_col = hist_projection(col_img)
        
            condition = 0 # Flag to determine if current iteration is reading a paragraph
            start_row = 0 # Upper boundary of an identified paragraph
            end_row = 0 # Lower boundary of the identified paragraph
            row_gap = 0 # Variable to track gap size between text lines
            row_gap_threshold = 30 # Minimum gap size for a paragraph to be recognised
            
            # Extract the content
            for t in range(len(hor_proj_col)):
                # Start the extraction:
                # Condition when upper boundary of paragraph is detected
                if hor_proj_col[t] != 0 and condition == 0:
                    start_row = t - padding # Adding Top padding
                    condition += 1
                # Condition when gap is found but threshold is not met
                elif hor_proj_col[t] == 0 and condition == 1 and row_gap <= row_gap_threshold:
                    row_gap += 1
                # Condition when new upper boundary is found but threshold is not met
                elif hor_proj_col[t] != 0 and condition == 1 and row_gap <= row_gap_threshold:
                    row_gap = 0
                # Stop the extraction:
                # Condition when no new upper boundary is found and threshold is met
                elif hor_proj_col[t] == 0 and condition == 1 and row_gap > row_gap_threshold:
                    end_row = t - row_gap_threshold + padding # Adding Bottom padding
                    condition -= 1
                    row_gap = 0
                
                    # Extract, sort and save the paragraphs while ignoring figures and tables
                    content = col_img[start_row-padding:end_row+padding+1,:]
                    hor_proj_ex, ver_proj_ex = hist_projection(content)
                    
                    max_pixels = np.max(hor_proj_ex)
                    max_value_range = 5  # Set a range for maximum projection values to be used in count_max
                    
                    # Calculate number of occurence of maximum projection values within the range 
                    # (max_pixels-5 to max_pixels)
                    count_max = np.count_nonzero((hor_proj_ex >= max_pixels-max_value_range) & (hor_proj_ex <= max_pixels))
                    
                    # Sort and save paragraphs while ignoring the figures and table that is not removed previously
                    # Content won't be saved as output image if it does not fulfill any of the requirements.
                    if count_max != 5 and np.min(hor_proj_ex[50:200]) == 0 and max_pixels > 30:
                        counter += 1
                        cv2.imwrite(i[:-4] + "_" + str(counter) + ".png", content)
                    
        else: # Break the loop if a zero is detected, meaning there's no more new boundaries
            break