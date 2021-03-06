# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: transformer_embedding.py
# time: 2:22 下午


import os

os.environ['TF_KERAS'] = '1'

import json
import codecs
import logging
from typing import Union, Optional
from bert4keras.models import build_transformer_model
import kashgari
import tensorflow as tf
from kashgari.embeddings.bert_embedding import BERTEmbedding
from kashgari.layers import NonMaskingLayer
from kashgari.processors.base_processor import BaseProcessor
import keras_bert


class TransformerEmbedding(BERTEmbedding):
    """Pre-trained BERT embedding"""

    def info(self):
        info = super(BERTEmbedding, self).info()
        info['config'] = {
            'vocab_path': self.vocab_path,
            'config_path': self.config_path,
            'checkpoint_path': self.checkpoint_path,
            'bert_type': self.bert_type,
            'sequence_length': self.sequence_length
        }
        return info

    def __init__(self,
                 vocab_path: str,
                 config_path: str,
                 checkpoint_path: str,
                 bert_type: str = 'bert',
                 task: str = None,
                 sequence_length: Union[str, int] = 'auto',
                 processor: Optional[BaseProcessor] = None,
                 from_saved_model: bool = False):
        self.model_folder = ''
        self.vocab_path = vocab_path
        self.config_path = config_path
        self.checkpoint_path = checkpoint_path
        super(BERTEmbedding, self).__init__(task=task,
                                            sequence_length=sequence_length,
                                            embedding_size=0,
                                            processor=processor,
                                            from_saved_model=from_saved_model)
        self.bert_type = bert_type
        self.processor.token_pad = '[PAD]'
        self.processor.token_unk = '[UNK]'
        self.processor.token_bos = '[CLS]'
        self.processor.token_eos = '[SEP]'

        self.processor.add_bos_eos = True

        if not from_saved_model:
            self._build_token2idx_from_bert()
            self._build_model()

    def _build_token2idx_from_bert(self):
        token2idx = {}
        with codecs.open(self.vocab_path, 'r', 'utf8') as reader:
            for line in reader:
                token = line.strip()
                token2idx[token] = len(token2idx)

        self.bert_token2idx = token2idx
        self._tokenizer = keras_bert.Tokenizer(token2idx)
        self.processor.token2idx = self.bert_token2idx
        self.processor.idx2token = dict([(value, key) for key, value in token2idx.items()])

    def _build_model(self, **kwargs):
        if self.embed_model is None:
            seq_len = self.sequence_length
            if isinstance(seq_len, tuple):
                seq_len = seq_len[0]
            if isinstance(seq_len, str):
                logging.warning("Model will be built when sequence length is determined")
                return

            config_path = self.config_path

            config = json.load(open(config_path))
            if seq_len > config.get('max_position_embeddings'):
                seq_len = config.get('max_position_embeddings')
                logging.warning(f"Max seq length is {seq_len}")

            bert_model = build_transformer_model(config_path=self.config_path,
                                                 checkpoint_path=self.checkpoint_path,
                                                 model=self.bert_type,
                                                 application='encoder',
                                                 return_keras_model=True)

            bert_model.trainable = False

            self.embed_model = bert_model

            self.embedding_size = int(bert_model.output.shape[-1])
            output_features = NonMaskingLayer()(bert_model.output)
            self.embed_model = tf.keras.Model(bert_model.inputs, output_features)


BERTEmbeddingV2 = TransformerEmbedding

if __name__ == "__main__":
    model_folder = '/Users/brikerman/Desktop/nlp/language_models/albert_base'

    embed = TransformerEmbedding(os.path.join(model_folder, 'vocab_chinese.txt'),
                                 os.path.join(model_folder, 'model_config.json'),
                                 os.path.join(model_folder, 'model.ckpt-best'),
                                 bert_type='albert',
                                 task=kashgari.CLASSIFICATION,
                                 sequence_length=100)
    x = embed.embed_one(list('今天天气不错'))
    print(x)
