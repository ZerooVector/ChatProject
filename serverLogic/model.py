import sys
import torch 

sys.path.append("..")
from transformers import BertTokenizer, GPT2LMHeadModel
from torch import nn

from utils import get_project_rootpath
import os


class GPT2(nn.Module):
    def __init__(self):
        super(GPT2, self).__init__()
        #这里直接调用huggingface上预训练好的gpt模型，使用了100G纯文本进行预训练的模型，在其基础上进行微调。
        self.gpt = GPT2LMHeadModel.from_pretrained(os.path.join("/home/syh/MyProjects/ChatProject/serverLogic", "gpt2-chinese-cluecorpussmall"))
    

    # def load_checkpoint(self, checkpoint_path):
    #     self.gpt.load_state_dict(torch.load(checkpoint_path))


    def forward(self, batch_inputs):
        outputs = self.gpt(input_ids=batch_inputs)
        return outputs
