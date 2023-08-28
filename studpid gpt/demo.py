import torch
import numpy as np
from transformers.models.gpt2 import GPT2LMHeadModel
from transformers import BertTokenizer
import sys
sys.path.append("..")
from model import GPT2




def answer(sentence, model, tokenizer,max_length = 200):

    input_ids = []
    input_ids.extend(tokenizer.encode(sentence))

    answer = ''
    for i in range(max_length):
        inputs = torch.tensor(input_ids).unsqueeze(0).to(device)

        outputs = model(inputs)
        logits = outputs.logits

        last_token_id = int(np.argmax(logits[0][-1].cpu().detach().numpy()))

        last_token = tokenizer.convert_ids_to_tokens(last_token_id)
        if last_token=="[SEP]":
            break
        answer += last_token
        input_ids.append(last_token_id)

    return answer

def talk():
    sentence = ''
    while True:
        print("我：", end='')
        temp_sentence = input()

        sentence += (temp_sentence + '[SEP]')
        if len(sentence) > 1024:
            sep_index = sentence.rfind('[SEP]')
            sentence = sentence[sep_index + 1:]
        print("机器人:", answer(sentence, model, tokenizer))
if __name__ == '__main__':
    device = torch.device("cpu")
    model = GPT2().to(device)
    model.eval()
    tokenizer = BertTokenizer.from_pretrained("./gpt2-chinese-cluecorpussmall")
    model.load_state_dict(torch.load("./model_checkpoints/GPT5.pt",map_location=torch.device('cpu')),False)
    talk()

