#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-09-20 11:57

################################################################################
#
#  基于百度 DDParser(v1.06) 进行重构：添加自定义行业词典，抽提显式关系
#
#################################################################################


import sys
import os
import logging
import six
import paddle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import LAC
import numpy as np


from dparser.parser import epoch_predict
from dparser.parser import load
from dparser.parser import ArgConfig
from dparser.parser import Environment
from dparser.parser.data_struct import Corpus
from dparser.parser.data_struct import TextDataset
from dparser.parser.data_struct import batchify
from dparser.parser.data_struct import Field
from dparser.parser.data_struct import utils

import warnings
warnings.filterwarnings('ignore')

class DDParser(object):
    """
    DDParser

    Args:
    use_cuda: BOOL, 是否使用gpu
    tree: BOOL, 是否返回树结构
    prob: BOOL, 是否返回弧的概率
    use_pos: BOOL, 是否返回词性标签(仅parse函数生效)
    model_files_path: str, 模型地址, 为None时下载默认模型
    buckets: BOOL, 是否对样本分桶. 若buckets=True，则会对inputs按长度分桶，处理长度不均匀的输入速度更新快，default=False
    batch_size: INT, 批尺寸, 当buckets为False时，每个batch大小均等于batch_size; 当buckets为True时，每个batch的大小约为'batch_size / 当前桶句子的平均长度'。
                当default=None时，分桶batch_size默认等于1000，不分桶默认等于50。
    encoding_model:指定模型，可以选lstm、transformer、ernie-1.0、ernie-tiny等
    """
    def __init__(
        self,
        use_cuda=False,
        tree=True,
        prob=False,
        use_pos=False,
        model_files_path=None,
        buckets=False,
        batch_size=None,
        encoding_model="ernie-lstm",
    ):
        if model_files_path is None:
            if encoding_model in ["lstm", "transformer", "ernie-1.0", "ernie-tiny", "ernie-lstm"]:
                model_files_path = self._get_abs_path(os.path.join("./model_files/ernie-lstm"))
            else:
                raise KeyError("Unknown encoding model.")

            if not os.path.exists(model_files_path):
                try:
                    utils.download_model_from_url(model_files_path, encoding_model)
                except Exception as e:
                    logging.error("Failed to download model, please try again")
                    logging.error("error: {}".format(e))
                    raise e

        args = [
            "--model_files={}".format(model_files_path), "--config_path={}".format(self._get_abs_path('config.ini')),
            "--encoding_model={}".format(encoding_model)
        ]
        self.custom_dict = self._get_abs_path('./model_files/custom_dict2.txt')
        if use_cuda:
            args.append("--use_cuda")
        if tree:
            args.append("--tree")
        if prob:
            args.append("--prob")
        if batch_size:
            args.append("--batch_size={}".format(batch_size))

        args = ArgConfig(args)
        # Don't instantiate the log handle
        args.log_path = None
        self.env = Environment(args)
        self.args = self.env.args
        paddle.set_device(self.env.place)
        self.model = load(self.args.model_path)
        self.model.eval()
        self.lac = None
        self.use_pos = use_pos
        # buckets=None if not buckets else defaults
        if not buckets:
            self.args.buckets = None
        if args.prob:
            self.env.fields = self.env.fields._replace(PHEAD=Field("prob"))
        if self.use_pos:
            self.env.fields = self.env.fields._replace(CPOS=Field("postag"))
        # set default batch size if batch_size is None and not buckets
        if batch_size is None and not buckets:
            self.args.batch_size = 50

    def parse(self, inputs):
        if not self.lac:
            self.lac = LAC.LAC(mode="lac" if self.use_pos else "seg", use_cuda=self.args.use_cuda)
            self.lac.load_customization(self.custom_dict)
        if not inputs:
            return
        if isinstance(inputs, six.string_types):
            inputs = [inputs]
        if all([isinstance(i, six.string_types) and i for i in inputs]):
            lac_results = []
            position = 0
            try:
                inputs = [query if isinstance(query, six.text_type) else query.decode("utf-8") for query in inputs]
            except UnicodeDecodeError:
                logging.warning("encoding only supports UTF-8!")
                return

            while position < len(inputs):
                lac_results += self.lac.run(inputs[position:position + self.args.batch_size])
                position += self.args.batch_size
            predicts = Corpus.load_lac_results(lac_results, self.env.fields)
        else:
            logging.warning("please check the foramt of your inputs.")
            return
        dataset = TextDataset(predicts, [self.env.WORD, self.env.FEAT], self.args.buckets)
        # set the data loader

        dataset.loader = batchify(
            dataset,
            self.args.batch_size,
            use_multiprocess=False,
            sequential_sampler=True if not self.args.buckets else False,
        )
        pred_arcs, pred_rels, pred_probs = epoch_predict(self.env, self.args, self.model, dataset.loader)

        if self.args.buckets:
            indices = np.argsort(np.array([i for bucket in dataset.buckets.values() for i in bucket]))
        else:
            indices = range(len(pred_arcs))
        predicts.head = [pred_arcs[i] for i in indices]
        predicts.deprel = [pred_rels[i] for i in indices]
        if self.args.prob:
            predicts.prob = [pred_probs[i] for i in indices]

        outputs = predicts.get_result()
        return outputs

    def parse_seg(self, inputs):

        if not inputs:
            return
        if all([isinstance(i, list) and i and all(i) for i in inputs]):
            predicts = Corpus.load_word_segments(inputs, self.env.fields)
        else:
            logging.warning("please check the foramt of your inputs.")
            return
        dataset = TextDataset(predicts, [self.env.WORD, self.env.FEAT], self.args.buckets)
        # set the data loader
        dataset.loader = batchify(
            dataset,
            self.args.batch_size,
            use_multiprocess=False,
            sequential_sampler=True if not self.args.buckets else False,
        )
        pred_arcs, pred_rels, pred_probs = epoch_predict(self.env, self.args, self.model, dataset.loader)

        if self.args.buckets:
            indices = np.argsort(np.array([i for bucket in dataset.buckets.values() for i in bucket]))
        else:
            indices = range(len(pred_arcs))
        predicts.head = [pred_arcs[i] for i in indices]
        predicts.deprel = [pred_rels[i] for i in indices]
        if self.args.prob:
            predicts.prob = [pred_probs[i] for i in indices]

        outputs = predicts.get_result()
        if outputs[0].get("postag", None):
            for output in outputs:
                del output["postag"]
        return outputs

    def _get_abs_path(self, path):
        return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), path))


if __name__ == "__main__":
    logging.info("init arguments.")
    args = ArgConfig()

    logging.info("init environment.")
    env = Environment(args)

    logging.info("Override the default configs\n{}".format(env.args))
    logging.info("{}\n{}\n{}\n{}".format(env.WORD, env.FEAT, env.ARC, env.REL))
    logging.info("Set the max num of threads to {}".format(env.args.threads))
    logging.info("Set the seed for generating random numbers to {}".format(env.args.seed))
    logging.info("Run the subcommand in mode {}".format(env.args.mode))

    paddle.set_device(env.place)
    mode = env.args.mode
    # print("mode: ", mode)
    # if mode == "train":
    #     train(env)
    # elif mode == "evaluate":
    #     evaluate(env)
    # elif mode == "predict":
    #     predict(env)
    # elif mode == "predict_q":
    #     predict_query(env)
    # else:
    #     logging.error("Unknown task mode: {}.".format(mode))
