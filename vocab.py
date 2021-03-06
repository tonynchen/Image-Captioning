import nltk
import json
import os
from pycocotools.coco import COCO
from collections import Counter

class Vocab():
    def __init__(self, annotations_file, vocab_threshold=5):
        self.vocab_threshold = vocab_threshold
        self.annotations_file = annotations_file
        self.start_word = '<start>'
        self.end_word = '<end>'
        self.unknown_word = '<unknown>'
        self.get_vocab()

    def __call__(self, word):
        if not word in self.word2idx:
            return self.word2idx[self.unknown_word]
        return self.word2idx[word]
    
    def __len__(self):
        return len(self.word2idx)

    def get_vocab(self):
        if os.path.exists('./built_vocab.json'):
            temp = None
            with open('./built_vocab.json', 'r') as f:
                # string = f.read().split(';')
                temp = json.load(f)
            self.word2idx = temp['word2idx']
            self.idx2word = temp['idx2word']
        else:
            self.build_vocab()
            temp = {'word2idx': self.word2idx,
                    'idx2word': self.idx2word}
            # word_to_index_string = json.dumps(self.word_to_index)
            # idx2word_string = json.dumps(self.index_to_word)
            # result = word_to_index_string + ";" + idx2word_string
            with open('./built_vocab.json', 'w') as f:
                f.write(json.dumps(temp))

            # self.word_to_index = temp[]

    def build_vocab(self):
        self.init_vocab()
        self.add_word(self.start_word)
        self.add_word(self.end_word)
        self.add_word(self.unknown_word)
        self.add_captions()

    def init_vocab(self):
        self.word2idx = {}
        self.idx2word = {}
        self.index = 0

    def add_word(self, word):
        if not word in self.word2idx:
            self.word2idx[word] = self.index
            self.idx2word[self.index] = word
            self.index += 1

    def add_captions(self):
        coco = COCO(self.annotations_file)
        ids = coco.anns.keys()
        word_frequency = Counter()
        for i, id in enumerate(ids):
            caption = str(coco.anns[id]['caption'])
            tokens = nltk.tokenize.word_tokenize(caption.lower())
            word_frequency.update(tokens)

            if i % 100000 == 0:
                print('[%d/%d] Tokenizing captions...' % (i, len(ids)))

        important_words = []
        for word, count in word_frequency.items():
            if count >= self.vocab_threshold:
                important_words.append(word)

        for i, word in enumerate(important_words):
            self.add_word(word)