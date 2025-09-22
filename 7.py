# Image augmentation
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import load_img, img_to_array
import matplotlib.pyplot as plt
import os
image_path = 'car.jpeg'
image = load_img(image_path)
image = img_to_array(image)
image = image.reshape((1,) + image.shape)
datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
i = 0
plt.figure(figsize=(10, 10))
for batch in datagen.flow(image, batch_size=1):
    plt.subplot(3, 3, i + 1)
    imgplot = plt.imshow(batch[0].astype('uint8'))
    i += 1
    if i % 9 == 0:
        break
plt.show()