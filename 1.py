# XOR with MLP
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import tensorflow as tf
tf.random.set_seed(69)
X_train = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_train = np.array([[0], [1], [1], [0]])
model = Sequential([
Dense(4, input_dim=2, activation='sigmoid'),
Dense(1, activation='sigmoid')])
model.compile(loss='binary_crossentropy',
optimizer='adam',
metrics=['accuracy'])
model.fit(X_train, y_train, epochs=2000, verbose=0)
loss, accuracy = model.evaluate(X_train, y_train, verbose=0)
print(f"Loss: {loss:.2f}, Accuracy: {accuracy:.2f}")
X_test = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_pred = (model.predict(X_test, verbose=0) > 0.5).astype("int32")
print("Input\tOutput")
for i in range(len(X_test)):
    print(f"{X_test[i]}\t{y_pred[i][0]}")