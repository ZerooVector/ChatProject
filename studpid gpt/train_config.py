import argparse

import sys

sys.path.append("..")
from utils import get_project_rootpath
import os

checkpoints_dir = os.path.join(get_project_rootpath(), "model_checkpoints")


def train_parse_args():
    parser = argparse.ArgumentParser(description="训练参数配置")
    parser.add_argument("--device", type=str, default="cpu", help="batch size")
    parser.add_argument("--batch_size", type=int, default=4, help="batch size")
    parser.add_argument("--epochs", type=int, default=5, help="epochs")
    parser.add_argument("--print_every", type=int, default=10, help="print every")
    parser.add_argument("--clip", type=int, default=1, help="clip")


    parser.add_argument("--train_file_path", type=str, default=os.path.join(get_project_rootpath(), "data/train5.txt"),
                        help="train_file_path")

    parser.add_argument('--save_path', type=str, default=os.path.join(checkpoints_dir, "GPT5.pt"),
                        help='decay step')
    parser.add_argument('--lr', type=float, default=1e-4, help='learning rate')


    return parser.parse_args()
