# A -  Image augmentation
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

# 7B - RBM MODELLING TO HANDWRITEN DIGITS
import numpy as np
import pandas as pd
import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
import matplotlib.pyplot as plt
plt.rcParams['image.cmap'] = 'gray'
def gen_mnist_image(X):
    return np.rollaxis(np.rollaxis(X[0:200].reshape(20, -1, 28, 28), 0, 2), 1, 3).reshape(-1, 20 * 28)
X_train = pd.read_csv('../input/mnist-digit-recognizer/train.csv').values[:,1:]
X_train = (X_train - np.min(X_train, 0)) / (np.max(X_train, 0) + 0.0001)
plt.figure(figsize=(10,20))
plt.imshow(gen_mnist_image(X_train))
from sklearn.neural_network import BernoulliRBM
rbm = BernoulliRBM(n_components=100, learning_rate=0.01, random_state=0, verbose=True)
rbm.fit(X_train)
xx = X_train[:40].copy()
for ii in range(1000):
    for n in range(40):
        xx[n] = rbm.gibbs(xx[n])
plt.figure(figsize=(10,20))
plt.imshow(gen_mnist_image(xx))
xx = X_train[:40].copy()
for ii in range(10000):
    for n in range(40):
        xx[n] = rbm.gibbs(xx[n])
plt.figure(figsize=(10,20))
plt.imshow(gen_mnist_image(xx))