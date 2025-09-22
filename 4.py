# Speech recog using NLP
import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')
import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames[:2]:
        print(os.path.join(dirname, filename))
import librosa
import IPython.display as ipd
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
ipd.Audio('/kaggle/input/nlp-specialization-data/harvard.wav')
ipd.Audio('/kaggle/input/nlp-specialization-data/testSpeech.wav')
ipd.Audio('/kaggle/input/nlp-specialization-data/singleEnglishWord.wav')
r = sr.Recognizer()
harvard = sr.AudioFile('/kaggle/input/nlp-specialization-data/testSpeech.wav')
with harvard as source:
    audio = r.record(source)
text = r.recognize_google(audio)
print(text)