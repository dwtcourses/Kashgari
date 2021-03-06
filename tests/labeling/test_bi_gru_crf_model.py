# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: test_blstm_crf_model.py
# time: 00:38


import tests.labeling.test_cnn_lstm_model as base
from kashgari.tasks.labeling import BiGRU_CRF_Model


class TestGRUCRFModel(base.TestCNN_LSTM_Model):
    @classmethod
    def setUpClass(cls):
        cls.epochs = 1
        cls.model_class = BiGRU_CRF_Model

    def test_basic_use_build(self):
        super(TestGRUCRFModel, self).test_basic_use_build()


if __name__ == "__main__":
    print("Hello world")