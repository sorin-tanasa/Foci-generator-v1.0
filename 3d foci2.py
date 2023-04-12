#THIS SCRIPT CREATEs GRADIENTED SPHERES in a 3d space
### Setup the libraries, paths and folders
import cv2
import numpy as np
import random
import os

image_path=r"G:\Github saves\Foci generator v1.0\3dtest"
test_path=r"G:\Github saves\Foci generator v1.0\3dtest\outputs"



### Generate sphere coordinates
# 1. Set the dimensions of the images and the number of spheres
img_size = (1024, 1024)
num_spheres = 52

# 2. Counter variable to keep track of actual number of spheres generated
actual_num_spheres = 0

# 3. Generate spheres until the desired number of non-overlapping spheres are generated
spheres = []
while actual_num_spheres < num_spheres:
    # Generate sphere parameters
    diameter = random.randint(5, 25)
    x = random.randint(diameter, img_size[0] - diameter)
    y = random.randint(diameter, img_size[1] - diameter)
    z = random.randint(0, 99)
    center = [x, y, z]
    
    # Check if sphere overlaps with previously generated spheres
    overlaps = False
    for sphere in spheres:
        dist = np.linalg.norm(np.array(center) - np.array(sphere[0]))
        if dist < (diameter + sphere[1]) / 2:
            overlaps = True
            break
    # Add sphere to list if it does not overlap with any previously generated spheres
    if not overlaps:
        spheres.append([center, diameter])
        actual_num_spheres += 1
print(f"Generated {actual_num_spheres} spheres")

### Draw overlap of future sppheres by drawing their borders in red circles on a black background
coordinates=np.zeros((img_size[0], img_size[0],3), dtype=np.uint8)
for x in spheres:
    cv2.circle(coordinates, x[0][:2], x[1], [0,0,255], 1) 
    
os.chdir(test_path)   
cv2.imshow("spheres in one image", coordinates)   
cv2.imwrite("coordinates.png", coordinates)
cv2.waitKey()



### Finalize the sphere generation of n images
# 1. Define the gradient space.
gradient = np.linspace(255, 1, 256, dtype=np.uint8) 
# (center intensity - adjustable, edge indensity - adjustable, 
# color range 255+1 - do not change)

# 2. Generate the images
os.chdir(image_path) 
for z in range(100): # set here number of stacked images
    # Create a new image
    img = np.zeros((img_size[0], img_size[1], 3), dtype=np.uint8)
    # Draw the spheres that overlap with the current slice
    for sphere in spheres:
        center, diameter = sphere
        if abs(center[2] - z) <= int(diameter / 2):
            radius = int(diameter / 2) - abs(center[2] - z)
            
            # Create a boolean mask for the circle region
            x, y = np.ogrid[:img_size[0], :img_size[0]]
            distances = np.sqrt((x - center[0])**2 + (y - center[1])**2)
            mask = distances <= radius

            # Calculate the gradient for the circle
            gradient_indices = (distances[mask] / radius * 255).astype(np.uint8)
            #print(gradient_indices, " at loop", z)
            colors = gradient[gradient_indices]

            # Update the image with the gradient colors for the circle
            img[mask] = np.stack((colors, colors, colors), axis=-1)
            #cv2.circle(img, (center[0], center[1]), radius, color, -1)            
            
    # Add the current slice to the 3D image stack
    
    cv2.imwrite(f'image_{z:03}.png', img)
    
    
### Merge resulting spheres to count
# 1. Get a list of all the image files in the folder
image_files = os.listdir(image_path)
image_files = [f for f in image_files if f.endswith(".png")]

# 2. Load the first image to get the dimensions
img = cv2.imread(os.path.join(image_path, image_files[0]))
height, width = img.shape[:2]

# 3. Create an empty array to hold the merged image
merged = np.zeros((height, width), dtype=np.uint8)

# 4. Loop through the images and merge them
for file in image_files:
    img = cv2.imread(os.path.join(image_path, file))
    # Convert to grayscale and threshold to binarize
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # Use logical OR to combine with previous image
    merged = cv2.bitwise_or(merged, binary)

# 5. Save the merged image
os.chdir(test_path)   
cv2.imwrite("merged.png", merged)
print("Done")

#Make changes
#More changes