# Sentiment analysis using lstm
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
df = pd.read_csv('movie_review.csv')
reviews = df['Review'].values
sentiments = df['Sentiment'].values
tokenizer = Tokenizer(num_words=10000, oov_token='<unk>')
tokenizer.fit_on_texts(reviews)
sequences = tokenizer.texts_to_sequences(reviews)
max_length = max(len(s) for s in sequences)
padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post', truncating='post')
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(sentiments)
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, encoded_labels, test_size=0.2, random_state=42)
model = Sequential([
    Embedding(input_dim=10000, output_dim=128, input_length=max_length),
    LSTM(128, return_sequences=True),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.2, verbose=1)
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f'Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}')
new_reviews = [
    'This movie was fantastic and I enjoyed every moment of it.',
    'The acting was terrible and the plot was confusing.',
    'The movie was okay, not great but not bad either.',
]
new_sequences = tokenizer.texts_to_sequences(new_reviews)
new_padded_sequences = pad_sequences(new_sequences, maxlen=max_length, padding='post', truncating='post')
predictions = model.predict(new_padded_sequences)
predicted_sentiments = ['Positive' if pred > 0.5 else 'Negative' for pred in predictions]
for review, sentiment in zip(new_reviews, predicted_sentiments):
    print(f'Review: "{review}" -> Predicted Sentiment: {sentiment}')