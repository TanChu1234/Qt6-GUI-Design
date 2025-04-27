import cv2
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread(r'src\asset\data\1.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# MeanShift
mean_shift = cv2.pyrMeanShiftFiltering(image, sp=30, sr=40, maxLevel=1)

# K-means
pixel_values = image.reshape((-1, 3))
pixel_values = np.float32(pixel_values)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85)
_, labels, centers = cv2.kmeans(pixel_values, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
centers = np.uint8(centers)
kmeans = centers[labels.flatten()].reshape(image.shape)

# Plot
plt.figure(figsize=(15, 5))
plt.subplot(131), plt.imshow(image), plt.title('Original')
plt.subplot(132), plt.imshow(mean_shift), plt.title('MeanShift')
plt.subplot(133), plt.imshow(kmeans), plt.title('K-means (K=3)')
plt.show()