import os
import random
import numpy as np
import torch

def get_project_rootpath():
    """
    获取项目根目录。此函数的能力体现在，不论当前module被import到任何位置，都可以正确获取项目根目录
    :return:
    """
    path = os.path.realpath(os.curdir)
    while True:
        # PyCharm项目中，'.idea'是必然存在的，且名称唯一
        if '.idea' in os.listdir(path):
            return path
        path = os.path.dirname(path)

