import json
import os

import torch
import sys

sys.path.append("..")
import torch.utils.data as Data
from torch import nn, optim
import numpy as np
import time
from tqdm import tqdm

from train_config import train_parse_args
from dataset import make_data, MyDataSet
from model import GPT2
from transformers import BertTokenizer
from loss_recorder import AverageMeter
from utils import get_project_rootpath

#训练参数
train_args = train_parse_args()


#记录训练时间的函数
def epoch_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs


#每一步训练
def train_step(model, data_loader, epoch, optimizer, criterion, clip=1, print_every=None):
    model.train()

    #多少次训练就打印一次损失
    if print_every == 0:
        print_every = 1

    #当前epoch的loss总值
    epoch_loss = 0
    #损失记录
    losses = AverageMeter()
    temp_time = time.time()
    #遍历dataloader的每个batch
    for step, (dec_inputs, dec_outputs) in enumerate(data_loader):
        '''
        dec_inputs: [batch_size, tgt_len]
        dec_outputs: [batch_size, tgt_len]
        '''
        optimizer.zero_grad()
        #转到相应的device
        dec_inputs, dec_outputs = dec_inputs.to(device), dec_outputs.to(device)
        # outputs: [batch_size * tgt_len, tgt_vocab_size]
        #输入模型，得到输出，
        outputs = model(dec_inputs)
        outputs = outputs.logits
        #改变输出维度，便于进行交叉熵损失 (batch,seq_len,hid_dim) -> (batch*seq_len,hid_dim)
        outputs = outputs.view(-1,outputs.size(-1))
        #计算交叉熵损失
        loss = criterion(outputs, dec_outputs.view(-1))
        epoch_loss += loss.item()
        losses.update(loss.item(), batch_size)

        #反向传播
        loss.backward()

        # 梯度裁剪
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)

        optimizer.step()

        #打印损失以及时间
        if print_every and (step + 1) % print_every == 0:
            minutes, seconds = epoch_time(temp_time, time.time())
            print('Epoch: [{0}][{1}/{2}] '
                  'Loss: {loss.val:.4f}({loss.avg:.4f}) '
                  'Elapsed {minutes:s}min {seconds:s}s '
                  .format(epoch, step + 1, len(data_loader),
                          minutes=minutes.__str__(),
                          seconds=seconds.__str__(),
                          loss=losses))
            temp_time = time.time()

    return epoch_loss / len(data_loader)


#训练函数
def train(model, dataloader, train_args):
    #损失计算方法
    criterion = nn.CrossEntropyLoss(ignore_index=0).to(device)
    lr = train_args.lr
    CLIP = train_args.clip
    print_every = train_args.print_every
    save_path = train_args.save_path
    optimizer = optim.Adam(model.parameters(), lr=lr)

    #训练epoch轮
    for epoch in range(epochs):
        start_time = time.time()
        train_loss = train_step(model, dataloader, epoch, optimizer, criterion, CLIP, print_every=print_every)
        end_time = time.time()

        torch.save(model.state_dict(), "./model_checkpoints/GPT5.pt")

        epoch_mins, epoch_secs = epoch_time(start_time, end_time)
        print(f'Epoch: {epoch + 1:02} | Time: {epoch_mins}m {epoch_secs}s')
        print(f'\tTrain Loss: {train_loss:.3f}')


#打印模型参数总量
def print_num_parameters(model):
    # Find total parameters and trainable parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f'{total_params:,} total parameters.')
    total_trainable_params = sum(

        p.numel() for p in model.parameters() if p.requires_grad)
    print(f'{total_trainable_params:,} training parameters.')


if __name__ == '__main__':
    device = torch.device('cpu')
    #使用huggingface中的tokenizer
    tokenizer = BertTokenizer.from_pretrained(os.path.join(get_project_rootpath(), "gpt2-chinese-cluecorpussmall"))

    #读取超参数
    epochs = train_args.epochs
    batch_size = train_args.batch_size

    train_file_path = train_args.train_file_path
    datas = make_data(train_file_path, tokenizer)
    dataset = MyDataSet(datas, tokenizer.vocab)
    #封装数据
    dataloader = Data.DataLoader(dataset, batch_size=batch_size, collate_fn=dataset.padding_batch)

    #实例化模型
    model=GPT2()
    model.load_state_dict(torch.load("./model_checkpoints/GPT5.pt",map_location=torch.device('cpu')),False)
    model =model.to(device)
    #进行训练
    train(model, dataloader, train_args)
