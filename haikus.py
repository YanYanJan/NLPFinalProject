import json
import pathlib
import re
import pandas as pd


# Define functions for better representation
def uppercase(word):
    return word.group(0).upper()

def capitalize(character):
    return re.sub('^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)', uppercase, character)

# Load dictionary of words with syllable counts
dictionary = {}
direction = 'phoneme-groups.json'
with open(direction) as f:
    for l in f:
        j = json.loads(l)
        dictionary[j['word']] = len(j['syllables'])

# Convert into a DataFrame and since all delete all with syllables more than 7
dict_df = pd.DataFrame.from_records([(k, dictionary[k]) for k in dictionary])
dict_df = dict_df[dict_df[1] <= 7]

# Load training text
corpus_direction = 'corpus'
corpus = []
regex = re.compile("[^A-Z\s'-\.]")
for path in pathlib.Path(corpus_direction).glob('*'):
    with open(str(path)) as f:
        corpus = corpus + [file.split() for file in re.split(r'[\.!\?;]',
                regex.sub('',f.read().upper().replace(",", "").replace("--", " ")))]


# markov model: 2 word
my_model = {}
for c in corpus:
    for i in range(len(c) - 1):
        w1 = c[i]
        w2 = c[i+1]

        if w1 not in my_model:
            my_model[w1] = {}

        if w2 not in my_model[w1]:
            my_model[w1][w2] = {'count': 1, 'end': 0, 'start': 0}
        else:
            my_model[w1][w2]['count'] += 1

        if i == (len(c) - 2):
            my_model[w1][w2]['end'] += 1
        if i == 0:
            my_model[w1][w2]['start'] += 1

records = [(w1, w2,my_model[w1][w2]['count'],
            my_model[w1][w2]['end'],
            my_model[w1][w2]['start']
        )
        for w1 in my_model for w2 in my_model[w1]
    ]

model_2 = pd.DataFrame.from_records(records).rename(columns={
    0: 'word1', 1:'word2', 2:'count', 3: 'end', 4: 'start'})

model_2 = model_2.merge(dict_df.rename(columns={0: 'word2', 1: 'syllables'}), on='word2')

model_2 = model_2.merge(dict_df.rename(columns={0: 'word1', 1: 'syllables_word1'}), on='word1')

group= model_2.groupby('word2')

percent = group.sum().reset_index()[['word2', 'end']].merge(group.sum().reset_index()[['word2', 'count']], on='word2')

percent['end_percent'] = percent['end']/percent['count']
model_2 = model_2.merge(percent[['word2', 'end_percent']], on='word2')

group = model_2.groupby('word1')
percent = group.sum().reset_index()[['word1', 'start']].merge(group.sum().reset_index()[['word1', 'count']], on='word1')


percent['start_percent'] = percent['start']/percent['count']

model_2 = model_2.merge(percent[['word1', 'start_percent']], on='word1')

# model with three words
my_model2 = {}
for c in corpus:
    for i in range(len(c) - 2):
        w1 = c[i]
        w2 = c[i+1]
        w3 = c[i+2]

        if w1 not in my_model2:
            my_model2[w1] = {}

        if w2 not in my_model2[w1]:
            my_model2[w1][w2] = {}

        if w3 not in my_model2[w1][w2]:
            my_model2[w1][w2][w3] = {'count': 1, 'end': 0}
        else:
            my_model2[w1][w2][w3]['count'] += 1

        if i == (len(c) - 3):
            my_model2[w1][w2][w3]['end'] += 1

records = []
for w1 in my_model2:
    for w2 in my_model2[w1]:
        for w3 in my_model2[w1][w2]:
            records.append((w1, w2, w3,
                my_model2[w1][w2][w3]['count'], my_model2[w1][w2][w3]['end']))

model_3 = pd.DataFrame.from_records(records).rename(columns={
    0: 'word1', 1:'word2', 2: 'word3', 3:'count', 4: 'end'})

model_3 = model_3.merge(dict_df.rename(columns={0: 'word3', 1: 'syllables'}), on='word3')

group = model_3.groupby('word3')

percent = group.sum().reset_index()[['word3', 'end']].merge(group.sum().reset_index()[['word3', 'count']], on='word3')

percent['end_percent'] =percent['end']/percent['count']
model_3 = model_3.merge(percent[['word3', 'end_percent']], on='word3')

model_2.to_csv('model_with_2.csv', index=False)
model_3.to_csv('model_with_3.csv', index=False)


# After we build the model, now we start to generate haikus based on our model

# the first word is special to make sure the syllables is not greater then 5
def get_first_word():
    subset = model_2[(model_2['syllables_word1'] <= 5) & (model_2['start_percent'] > .1)]
    w = subset.sample(n=1).iloc[0]
    return {'word': w['word1'], 'syllables': w['syllables_word1']}

def get_word(previous_words, remaining, line):
    if len(previous_words) >= 2:
        subset = model_3[
            (model_3['word1'] == previous_words[-2]['word']) &
            (model_3['word2'] == previous_words[-1]['word']) &
            (model_3['syllables'] <= remaining)
        ]

        if line == 2:
            subset = subset[
                (subset['syllables'] < remaining) | (subset['end_percent'] > .1)
            ]

        if len(subset) == 0:
            return get_word([previous_words[-1]], remaining, line)

        w = subset.sample(n=1, weights='count').iloc[0]

        return {'word': w['word3'], 'syllables': w['syllables']}
    else:
        subset = model_2[
            (model_2['word1'] == previous_words[-1]['word']) &
            (model_2['syllables'] <= remaining)
        ]

        if line == 2:
            subset = subset[
                (subset['syllables'] < remaining) | (subset['end_percent'] > .1)
            ]

        w = subset.sample(n=1, weights='count').iloc[0]

        return {'word': w['word2'], 'syllables': w['syllables']}

def generate_haiku():
    w = get_first_word()
    #print(w)
    previous_words = [w]
    haiku = [[w], [], []]
    counts = [5 - w['syllables'], 7, 5]

    for i,j in enumerate(counts):
        remain = j
        while remain > 0:
            try:
                w = get_word(previous_words, remain, i)
                previous_words.append(w)
                haiku[i].append(w)
                remain -= w['syllables']
            except Exception as e:
                previous = haiku[i].pop()
                previous_words.pop()
                remain += previous['syllables']
                #raise e

    print(capitalize(
        "\n".join([" ".join([w['word'] for w in l]) for l in haiku]).lower()
    ))

for i in range(10):
    generate_haiku()

