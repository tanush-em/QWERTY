# Fraud detection of share market
import tensorflow as tf
import pandas as pd
import numpy as np
data = pd.read_csv('D:\Babisha\stock1.csv')
features = data[['Open','Close']].values
labels = np.array(data['Adj Close'])
normalized_features = (features - features.mean()) / features.std()
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(2,)),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(normalized_features, labels, epochs=10, batch_size=32, validation_split=0.2)
predictions = model.predict(normalized_features)
data['FraudProbability'] = predictions
fraudulent_activities = data[data['FraudProbability'] > 0.5]
print("Fraudulent Activities:")
print(fraudulent_activities)
