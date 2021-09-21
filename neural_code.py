#############################################################################
#                  neural network command analyzer                          #
#############################################################################
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()
from .LRU_cache import *

def load_saved_data(arg='LRU'):
    model = load_model('chatbot_model.model')
    intents = json.loads(open('data/intents.json').read())
    words = pickle.load(open('data/words.pkl', 'rb'))
    classes = pickle.load(open('data/classes.pkl', 'rb'))
    return (intents, words, classes, model)


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words (sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    intents, words, classes, model = load_saved_data()
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.5
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list, intents


def get_response(intents_list, intents):
    tag = intents_list[0]['intent']
    list_of_intents = intents['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = (i['responses'], i['tag'])
            break
    return result