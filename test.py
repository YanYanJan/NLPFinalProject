import json
import random
import re
import pathlib
import pandas as pd


corpus = []
regex = re.compile("[^A-Z\s'-\.]")
#for path in pathlib.Path('corpus').glob('*'):
#    print(str(path))
#    with open(str(path)) as f:
#        corpus = corpus + re.split(r'\.\s+', regex.sub('', f.read().upper()))


dictionary = {}
with open('phoneme-groups-with-syllables.json') as f:
    for l in f:
        j = json.loads(l)
        if len(j['word']) > 1 or j['word'] in ['A', 'I', 'O']:
            dictionary[j['word']] = len(j['syllables'])

print(len(dictionary))

print(dictionary['CAN\'T'])

syllabels = [[] for i in range(20)]
for k in dictionary:
    syllabels[dictionary[k]].append(k)


#for i in range(1,5):
#    print(syllabels[i])
#print(syllabels[7])

haiku = []
for j in [5, 7, 5]:
    remaining = j
    haiku.append([])
    while remaining > 0:
        s = random.randint(1, remaining)
        haiku[-1].append(random.choice(syllabels[s]).lower())
        remaining -= s

print(haiku)


def uppercase(word):
    return word.group(0).upper()

def capitalize(symbol):
    return re.sub('^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)', uppercase, symbol)