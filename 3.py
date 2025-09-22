# A - Handwritten dig using autoencoders
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
(x_train, _), (x_test, _) = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))
input_dim = x_train.shape[1]
encoding_dim = 32
input_img = tf.keras.Input(shape=(input_dim,))
encoded = tf.keras.layers.Dense(encoding_dim, activation='relu')(input_img)
decoded = tf.keras.layers.Dense(input_dim, activation='sigmoid')(encoded)
autoencoder = tf.keras.Model(input_img, decoded)
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
autoencoder.fit(x_train, x_train, epochs=50, batch_size=256, shuffle=True, validation_data=(x_test, x_test))
reconstructed_images = autoencoder.predict(x_test)
n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(x_test[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax = plt.subplot(2, n, i + 1 + n)
    plt.imshow(reconstructed_images[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()

# B - Medical xray image classification using CNN
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
train_path ='D://Babisha//train'
test_path ='D://Babisha//test'
valid_path ='D://Babisha//val'
batch_size = 16
img_height = 500
img_width = 500
from tensorflow.keras.preprocessing.image import ImageDataGenerator
image_gen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
test_data_gen = ImageDataGenerator(rescale=1./255)
train = image_gen.flow_from_directory(
    train_path,
    target_size=(99, 128),
    color_mode='grayscale',
    class_mode='binary',
    batch_size=batch_size
)
test = test_data_gen.flow_from_directory(
    test_path,
    target_size=(99, 128),
    color_mode='grayscale',
    shuffle=False,
    class_mode='binary',
    batch_size=batch_size
)
valid = test_data_gen.flow_from_directory(
    valid_path,
    target_size=(99,128),
    color_mode='grayscale',
    class_mode='binary',
    batch_size=batch_size
)
plt.figure(figsize=(12, 12))
for i in range(0, 10):
    plt.subplot(2, 5, i+1)
    for X_batch, Y_batch in train:
        image = X_batch[0]
        dic = {0:'NORMAL', 1:'PNEUMONIA'}
        plt.title(dic.get(Y_batch[0]))
        plt.axis('off')
        plt.imshow(np.squeeze(image),cmap='gray',interpolation='nearest')
        break
plt.tight_layout()
plt.show()
