import json
import numpy as np
from tensorflow import keras
import music21 as m21
from preprocess import SEQUENCE_LENGTH, MAPPING_PATH
from Input_Conversion import encode_song,parse_m21,transpose


class MelodyGenerator:
    """A class that wraps the LSTM model and offers utilities to generate melodies."""

    def __init__(self, model_path="model.h5"):
        """Constructor that initialises TensorFlow model"""

        self.model_path = model_path
        self.model = keras.models.load_model(model_path)

        with open(MAPPING_PATH, "r") as fp:
            self._mappings = json.load(fp)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH


    def generate_melody(self, seed, num_steps, max_sequence_length, temperature):
        """Generates a melody using the DL model and returns a midi file.
        :param seed (str): Melody seed with the notation used to encode the dataset
        :param num_steps (int): Number of steps to be generated
        :param max_sequence_len (int): Max number of steps in seed to be considered for generation
        :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
            A number closer to 1 makes the generation more unpredictable.
        :return melody (list of str): List with symbols representing a melody
        """

        # create seed with start symbols
        seed = seed.split()
        melody = seed
        seed = self._start_symbols + seed

        # map seed to int
        seed = [self._mappings[symbol] for symbol in seed]

        for _ in range(num_steps):

            # limit the seed to max_sequence_length
            seed = seed[-max_sequence_length:]

            # one-hot encode the seed
            onehot_seed = keras.utils.to_categorical(seed, num_classes=len(self._mappings))
            # (1, max_sequence_length, num of symbols in the vocabulary)
            onehot_seed = onehot_seed[np.newaxis, ...]

            # make a prediction
            probabilities = self.model.predict(onehot_seed)[0]
            # [0.1, 0.2, 0.1, 0.6] -> 1
            output_int = self._sample_with_temperature(probabilities, temperature)

            # update seed
            seed.append(output_int)

            # map int to our encoding
            output_symbol = [k for k, v in self._mappings.items() if v == output_int][0]

            # check whether we're at the end of a melody
            if output_symbol == "/":
                break

            # update melody
            melody.append(output_symbol)



        return melody


    def _sample_with_temperature(self, probabilites, temperature):
        """Samples an index from a probability array reapplying softmax using temperature
        :param predictions (nd.array): Array containing probabilities for each of the possible outputs.
        :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
            A number closer to 1 makes the generation more unpredictable.
        :return index (int): Selected output symbol
        """

        predictions = np.log(probabilites) / temperature
        probabilites = np.exp(predictions) / np.sum(np.exp(predictions))
        # print("Probabilities",probabilites)
        choices = range(len(probabilites)) # [0, 1, 2, 3]
        # print("Choices:",choices)
        index = np.random.choice(choices, p=probabilites)
        # print("Index:",index)

        return index


    def save_melody(self, melody, step_duration=0.25, format="midi", file_name="D:\Music Project\static\Output\mel.mid"):
        """Converts a melody into a MIDI file
        :param melody (list of str):
        :param min_duration (float): Duration of each time step in quarter length
        :param file_name (str): Name of midi file
        :return:
        """

        # create a music21 stream
        stream = m21.stream.Stream()

        start_symbol = None
        step_counter = 1

        # parse all the symbols in the melody and create note/rest objects
        for i, symbol in enumerate(melody):

            # handle case in which we have a note/rest
            if symbol != "_" or i + 1 == len(melody):

                # ensure we're dealing with note/rest beyond the first one
                if start_symbol is not None:

                    quarter_length_duration = step_duration * step_counter # 0.25 * 4 = 1

                    # handle rest
                    if start_symbol == "r":
                        m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                    # handle note
                    else:
                        m21_event = m21.note.Note(int(start_symbol), quarterLength=quarter_length_duration)

                    stream.append(m21_event)

                    # reset the step counter
                    step_counter = 1

                start_symbol = symbol

            # handle case in which we have a prolongation sign "_"
            else:
                step_counter += 1


        # write the m21 stream to a midi file
        stream.write(format, file_name)




# This function will trigger the model to run and save the final output
def initialize_generator():
    mg = MelodyGenerator()
    input_song = parse_m21();

    transposed_song = transpose(input_song)
    encoded_song = encode_song(transposed_song)
    seed = check_seed_values(encoded_song)
    melody = mg.generate_melody(seed, 500, SEQUENCE_LENGTH, 0.7)
    print("This is melody: ",melody)
    #melody=['r', '_', '_', '_', '48', '_', 'r', '52', 'r', '55', '52', '59', '57', 'r', '69', '69', '69', '69', '64', '76', '76', '76', '76', '73', '63', '63', '63', '61', '63', '56', '80', '64', '80', '56', '56', '53', '56', '80', '64', '73', '80', '58', '58', '58', '58', '61', '64', '73', '61', '61', '53', '60', '60', '53', '53']

    mg.save_melody(melody)





# This function checks that if seed contains any note that is not mapped
def check_seed_values(seed):
    demo_seed = "62 _ _ _ 65 _ _ 60 _ 64 _ 61 _ 62 _ _"
    seed_notes_list = seed.split()
    approve_list = []
    print(seed_notes_list)
    # This dictionary has content from mapping.json
    mapped_midi_notes = {"74": 0, "_": 1, "68": 2, "66": 3, "76": 4, "71": 5, "78": 6, "53": 7, "52": 8, "56": 9,
                         "r": 10, "62": 11, "72": 12, "57": 13, "51": 14, "70": 15, "48": 16, "63": 17, "75": 18,
                         "81": 19, "64": 20, "/": 21, "47": 22, "55": 23, "67": 24, "61": 25, "79": 26, "80": 27,
                         "65": 28, "60": 29, "54": 30, "45": 31, "58": 32, "73": 33, "50": 34, "59": 35, "69": 36,
                         "77": 37}

    for note in seed_notes_list:
        if str(note) in mapped_midi_notes.keys():
            approve_list.append(1)
        else:
            approve_list.append(0)
    bad_case = approve_list.count(0)
    if bad_case > 0:
        seed = demo_seed

    return seed

initialize_generator()
