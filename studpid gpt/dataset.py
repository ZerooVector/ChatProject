import json
import torch
import torch.utils.data as Data
from torch import nn, optim
import numpy as np


#处理数据，对原始对话数据进行处理
def make_data(file_path, tokenizer):
    #读取原始数据的每一行，放进变量lines
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    train_datas = []
    #遍历每一行数据
    for line in lines:
        line = line.lower()
        line = line.strip()
        #把原始数据中的\t变成分隔符SEP，每次生成汉字到SEP结束生成
        train_data = [i if i != '\t' else "[SEP]" for i in line] + ['[SEP]']
        #使用tokenizer对中文数据进行编码
        train_num_data = tokenizer.encode(train_data)
        #编码后最后自动会多加一个SEP，不取加的SEP符号
        train_num_data = train_num_data[:-1]
        train_datas.append(train_num_data)

    return train_datas


#自定义Dataset封装数据
class MyDataSet(Data.Dataset):
    def __init__(self, datas, vocab2id):
        self.datas = datas
        self.vocab2id = vocab2id

    def __getitem__(self, item):
        data = self.datas[item]
        #输入数据是[CLS]问题[SEP]回答
        decoder_input = data[:-1]
        #输出数据是问题[SEP]回答[SEP]
        #输入与输出错位，可以实现基于前面的字预测下一个字的效果
        decoder_output = data[1:]

        #获取句子长度，后面需要用到对数据填充长度
        decoder_input_len = len(decoder_input)
        decoder_output_len = len(decoder_output)

        return {"decoder_input": decoder_input, "decoder_input_len": decoder_input_len,
                "decoder_output": decoder_output, "decoder_output_len": decoder_output_len}

    def __len__(self):
        return len(self.datas)

    #对一个batch的数据进行填充
    def padding_batch(self, batch):
        decoder_input_lens = [d["decoder_input_len"] for d in batch]
        decoder_output_lens = [d["decoder_output_len"] for d in batch]

        #获取这个batch中最长的句子的长度
        decoder_input_maxlen = max(decoder_input_lens)
        decoder_output_maxlen = max(decoder_output_lens)

        #把每个句子填充成这个batch中最长句子的长度，用PAD填充
        for d in batch:
            d["decoder_input"].extend([self.vocab2id["[PAD]"]] * (decoder_input_maxlen - d["decoder_input_len"]))
            d["decoder_output"].extend([self.vocab2id["[PAD]"]] * (decoder_output_maxlen - d["decoder_output_len"]))

        #变成tensor类型
        decoder_inputs = torch.tensor([d["decoder_input"] for d in batch], dtype=torch.long)
        decoder_outputs = torch.tensor([d["decoder_output"] for d in batch], dtype=torch.long)

        return decoder_inputs, decoder_outputs
