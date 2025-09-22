# Speech recog using NLP
import speech_recognition as sr
r = sr.Recognizer()
test_file = sr.AudioFile('/kaggle/input/nlp-specialization-data/testSpeech.wav')
with test_file as source:
    audio = r.record(source)
text = r.recognize_google(audio)
print(text)