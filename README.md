# Foci generator  

This tool can be used for generating test data for pipelines of data analysis in biology, like generating random foci (organelles, membraneless bodies, vacuoles, etc.) occuring in cells.


## Getting Started

### Installing the modules

1. OpenCV

```shell
pip install opencv-python
```

2. Numpy

```shell
pip install numpy
```


### Preparing the folders for data generation

You need to make two folders:

* Generated images folder - For all the images making uup the stack
* Test folder - For the overview images to test the correctness of the script 

We start by accessing the required libraries and dictating output folders:

```python
### Setup the libraries, paths and folders
import cv2
import numpy as np
import random
import os

images_path=r"C:\......\3D images"
test_path=r"C:\......\3D images\test"
```
Then we proceed to generating the future coordinates for the spheres in a 3D space:

```python
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
```

We can perform an initial screen of the efectiveness of our coordinate creation (optional) by plotting the coordinates of the future circles on a black image.

```python
### Draw overlap of future spheres by drawing their borders in red 
### circles on a black background
coordinates=np.zeros((img_size[0], img_size[0],3), dtype=np.uint8)
for sphere in spheres:
    cv2.circle(coordinates, sphere[0][:2], sphere[1], [0,0,255], 1) 
    
os.chdir(test_path)   
cv2.imshow("spheres in one image", coordinates)   
cv2.imwrite("coordinates.png", coordinates)
cv2.waitKey()
```
The output will look like this:

![coordinates](https://user-images.githubusercontent.com/47111504/223753958-6e833da3-f1dd-4581-9baa-2ace835e6005.png)


Using the Cell Counter in the FIJI (ImageJ) tool you can see the coordinates creator script generated as many circles as it was asked.
![-COUNTED CIRCLES](https://user-images.githubusercontent.com/47111504/223763285-5c10b181-6493-4ed2-bdee-d13add077a6c.png)


Now we can return to the sphere generation tool and perform the final step, of transforming the initial spheres coordinates and asociated diameters into gradiented circles on 2D images.

``` python
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
            x, y = np.ogrid[:img_size[0], :img_size[0]]Cancel changes
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
``` 
  
 You will find in the output folder n images of this general patttern:
 ![image_047](https://user-images.githubusercontent.com/47111504/223792316-5c277cd3-7792-41d2-a3dd-96ef15f7c95f.png)

The second half of the optional verification process is to generate the merged image of the n stacks we have generated.

``` python
### Merge resulting spheres to count
# 1. Get a list of all the image files in the folder
image_files = os.listdir(image_path)
image_files = [f for f in image_files if f.endswith(".png")]

# 2. Load the first image to get the dimensions
img = cv2.imread(os.path.join(folder_path, image_files[0]))
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
```
The output merged image will loook like this:
![merged](https://user-images.githubusercontent.com/47111504/223754068-2a0ae5c1-5cea-4ab0-b662-668731ea7738.png)

You can then compare the "merged.png" image with the initial "coordinates.png" image.
![comparison](https://user-images.githubusercontent.com/47111504/223755256-12695f86-827c-4d80-a6d1-6d4a5ac9aa90.png)


Use whatever prefered image format for your outputs. This example was for illustration purposes.
You can test if images are 3D either by scrolling through an image viewer image by image or creating using another tool I developped for this purpose, found at .... link.
Note: You may encounter an error message: 
"nvalid value encountered in divide
  gradient_indices = (distances[mask] / radius * 255).astype(np.uint8)"
This happens because there is a division of happening sometimes. This does not affect the funtionality of the code even at large numbers of spheres being generated.

