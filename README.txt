Haikus Generation Project:

In this project, there are two folder named:  corpus and corpus2 that contain different txt files that is used as input when creating models.

The phoneme-groups.json is an open source file from Kang's Phoneme project: https://github.com/jimkang/phonemenon
This json file guarantees the Haikus we generated will follow a pattern of 5-7-5 syllables.

There are two python files, first one is test.py that is mainly for exploring the corpus and input phoneme-group json file.

The complete working code for Haikus Generations is in haikus.py.
In haikus.py, there are several functions:
    1. functions: uppercase and capitalize are for pre-processing and cleaning the words.

    2. function: create_models(path) will create dictionary for all words and corresponding syllables.
                Then we convert the dictionary format into DataFrame: dict_df.
                Next we use the dict_df and txt files in two folders to create two models as a model group.
                The model group will be used later on to generate our Haikus and contains two models:
                    1) A two-word model
                    2) A three-word model
                The models are generated based on specifying the path of the input corpus.
                These models include features such as: word1, word2, and word3 if in three-word model;
                                                       count; end; start; (record the occurrence)
                                                       syllables, syllables_word1, (look up from dict_df)
                                                       based on the end and start number we calculate the end_percent,start_percent

    3.The following functions get_first_word(model_2) and get_word(model_2, model_3) are inner steps when generating haikus,
      since each word we generate has to satisfies the syllables restricting and likelihood of appearance.

    4. Last, generate_haiku(model_2, model_3) will use get_first_word(model_2) and get_word(model_2, model_3) functions
       to do the Haikus generation as desired.

After the models are created, we convert the models into csv files:
model_with_2_path1.csv, model_with2_path2.csv, model_with_3_path1.csv, model_with3_path2.csv
for clearer presentation of the models