#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-08 16:58
# @Author   : NING MEI
# @Desc     :



import sys
# sys.path.append("./uie_torch")

import argparse
import collections
import json
import os
import pickle
import shutil
import torch
from utils import get_path_from_url
try:
    import paddle
    paddle_installed = True
except (ImportError, ModuleNotFoundError):
    # from utils import get_path_from_url
    paddle_installed = False

from utils import logger


"""
 目的: 将paddlenlp-uie模型转为torch 模型
"""



def build_params_map(model_prefix='encoder', attention_num=12):
    """
    build params map from paddle-paddle's ERNIE to transformer's BERT
    :return:
    """
    weight_map = collections.OrderedDict({
        f'{model_prefix}.embeddings.word_embeddings.weight': "encoder.embeddings.word_embeddings.weight",
        f'{model_prefix}.embeddings.position_embeddings.weight': "encoder.embeddings.position_embeddings.weight",
        f'{model_prefix}.embeddings.token_type_embeddings.weight': "encoder.embeddings.token_type_embeddings.weight",
        f'{model_prefix}.embeddings.task_type_embeddings.weight': "encoder.embeddings.task_type_embeddings.weight",
        f'{model_prefix}.embeddings.layer_norm.weight': 'encoder.embeddings.LayerNorm.gamma',
        f'{model_prefix}.embeddings.layer_norm.bias': 'encoder.embeddings.LayerNorm.beta',
    })
    # add attention layers
    for i in range(attention_num):
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.q_proj.weight'] = f'encoder.encoder.layer.{i}.attention.self.query.weight'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.q_proj.bias'] = f'encoder.encoder.layer.{i}.attention.self.query.bias'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.k_proj.weight'] = f'encoder.encoder.layer.{i}.attention.self.key.weight'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.k_proj.bias'] = f'encoder.encoder.layer.{i}.attention.self.key.bias'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.v_proj.weight'] = f'encoder.encoder.layer.{i}.attention.self.value.weight'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.v_proj.bias'] = f'encoder.encoder.layer.{i}.attention.self.value.bias'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.out_proj.weight'] = f'encoder.encoder.layer.{i}.attention.output.dense.weight'
        weight_map[f'{model_prefix}.encoder.layers.{i}.self_attn.out_proj.bias'] = f'encoder.encoder.layer.{i}.attention.output.dense.bias'
        weight_map[f'{model_prefix}.encoder.layers.{i}.norm1.weight'] = f'encoder.encoder.layer.{i}.attention.output.LayerNorm.gamma'
        weight_map[f'{model_prefix}.encoder.layers.{i}.norm1.bias'] = f'encoder.encoder.layer.{i}.attention.output.LayerNorm.beta'
        weight_map[f'{model_prefix}.encoder.layers.{i}.linear1.weight'] = f'encoder.encoder.layer.{i}.intermediate.dense.weight'
        weight_map[f'{model_prefix}.encoder.layers.{i}.linear1.bias'] = f'encoder.encoder.layer.{i}.intermediate.dense.bias'
        weight_map[f'{model_prefix}.encoder.layers.{i}.linear2.weight'] = f'encoder.encoder.layer.{i}.output.dense.weight'
        weight_map[f'{model_prefix}.encoder.layers.{i}.linear2.bias'] = f'encoder.encoder.layer.{i}.output.dense.bias'
        weight_map[f'{model_prefix}.encoder.layers.{i}.norm2.weight'] = f'encoder.encoder.layer.{i}.output.LayerNorm.gamma'
        weight_map[f'{model_prefix}.encoder.layers.{i}.norm2.bias'] = f'encoder.encoder.layer.{i}.output.LayerNorm.beta'
    # add pooler
    weight_map.update(
        {
            f'{model_prefix}.pooler.dense.weight': 'encoder.pooler.dense.weight',
            f'{model_prefix}.pooler.dense.bias': 'encoder.pooler.dense.bias',
            'linear_start.weight': 'linear_start.weight',
            'linear_start.bias': 'linear_start.bias',
            'linear_end.weight': 'linear_end.weight',
            'linear_end.bias': 'linear_end.bias',
        }
    )
    return weight_map





def extract_and_convert(input_dir, output_dir, verbose=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if verbose:
        logger.info('=' * 20 + 'save config file' + '=' * 20)
    config = json.load(open(os.path.join(input_dir, 'model_config.json'), 'rt', encoding='utf-8'))
    if 'init_args' in config:
        config = config['init_args'][0]
    config["architectures"] = ["UIE"]
    config['layer_norm_eps'] = 1e-12
    del config['init_class']
    if 'sent_type_vocab_size' in config:
        config['type_vocab_size'] = config['sent_type_vocab_size']
    config['intermediate_size'] = 4 * config['hidden_size']
    json.dump(config, open(os.path.join(output_dir, 'config.json'),'wt', encoding='utf-8'), indent=4)
    if verbose:
        logger.info('=' * 20 + 'save vocab file' + '=' * 20)
    shutil.copy(os.path.join(input_dir, 'vocab.txt'), os.path.join(output_dir, 'vocab.txt'))
    special_tokens_map = json.load(open(os.path.join(input_dir, 'special_tokens_map.json'), 'rt', encoding='utf-8'))
    json.dump(special_tokens_map, open(os.path.join(output_dir, 'special_tokens_map.json'), 'wt', encoding='utf-8'))
    tokenizer_config = json.load(open(os.path.join(input_dir, 'tokenizer_config.json'), 'rt', encoding='utf-8'))
    if tokenizer_config['tokenizer_class'] == 'ErnieTokenizer':
        tokenizer_config['tokenizer_class'] = "BertTokenizer"
    json.dump(tokenizer_config, open(os.path.join(output_dir, 'tokenizer_config.json'),'wt', encoding='utf-8'))
    spm_file = os.path.join(input_dir, 'sentencepiece.bpe.model')
    if os.path.exists(spm_file):
        shutil.copy(spm_file, os.path.join(output_dir, 'sentencepiece.bpe.model'))
    if verbose:
        logger.info('=' * 20 + 'extract weights' + '=' * 20)
    state_dict = collections.OrderedDict()
    weight_map = build_params_map(attention_num=config['num_hidden_layers'])
    weight_map.update(build_params_map('ernie', attention_num=config['num_hidden_layers']))
    if paddle_installed:
        import paddle.fluid.dygraph as D
        from paddle import fluid
        with fluid.dygraph.guard():
            paddle_paddle_params, _ = D.load_dygraph( os.path.join(input_dir, 'model_state'))
    else:
        paddle_paddle_params = pickle.load(open(os.path.join(input_dir, 'model_state.pdparams'), 'rb'))
        del paddle_paddle_params['StructuredToParameterName@@']
    for weight_name, weight_value in paddle_paddle_params.items():
        transposed = ''
        if 'weight' in weight_name:
            if '.encoder' in weight_name or 'pooler' in weight_name or 'linear' in weight_name:
                weight_value = weight_value.transpose()
                transposed = '.T'
        # Fix: embedding error
        if 'word_embeddings.weight' in weight_name:
            weight_value[0, :] = 0
        if weight_name not in weight_map:
            if verbose:
                logger.info(f"{'='*20} [SKIP] {weight_name} {'='*20}")
            continue
        state_dict[weight_map[weight_name]] = torch.FloatTensor(weight_value)
        if verbose:
            logger.info(f"{weight_name}{transposed} -> {weight_map[weight_name]} {weight_value.shape}")
    torch.save(state_dict, os.path.join(output_dir, "pytorch_model.bin"))


def check_model(input_model):

    if not os.path.exists(input_model):
        MODEL_MAP = {
            # vocab.txt/special_tokens_map.json/tokenizer_config.json are common to the default model.
            "uie-base": {
                "resource_file_urls": {
                    "model_state.pdparams":
                        "https://bj.bcebos.com/paddlenlp/taskflow/information_extraction/uie_base_v1.0/model_state.pdparams",
                    "model_config.json":
                        "https://bj.bcebos.com/paddlenlp/taskflow/information_extraction/uie_base/model_config.json",
                    "vocab.txt":
                        "https://bj.bcebos.com/paddlenlp/taskflow/information_extraction/uie_base/vocab.txt",
                    "special_tokens_map.json":
                        "https://bj.bcebos.com/paddlenlp/taskflow/information_extraction/uie_base/special_tokens_map.json",
                    "tokenizer_config.json":
                        "https://bj.bcebos.com/paddlenlp/taskflow/information_extraction/uie_base/tokenizer_config.json"
                }
            }
        }
        if input_model not in MODEL_MAP:
            raise ValueError('input_model not exists!')

        resource_file_urls = MODEL_MAP[input_model]['resource_file_urls']
        logger.info("Downloading resource files...")

        for key, val in resource_file_urls.items():
            file_path = os.path.join(input_model, key)
            download_path = get_path_from_url(val, input_model)
            if download_path != file_path:
                shutil.move(download_path, file_path)




def do_main():
    if args.output_model is None:
        args.output_model = args.input_model.replace('-', '_')+'_pytorch'
    args.input_model = "uie-base"
    check_model(args.input_model)
    extract_and_convert(args.input_model, args.output_model, verbose=True)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_model", default="uie-base", type=str,
                        help="mode name should be 'uie-base' ")
    parser.add_argument("-o", "--output_model", default=None, type=str,
                        help="Directory of output pytorch model")
    args = parser.parse_args()
    do_main()

