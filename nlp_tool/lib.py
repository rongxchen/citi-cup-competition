# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 14:12:00 2023
@author: zhout
"""
import os
import pickle
import torch

# model settings

curdir = os.getcwd()
print(f"{curdir}\\nlp_tool\model\ws.pkl")
ws = pickle.load(open(f"{curdir}\\nlp_tool\model\ws.pkl", "rb"))

max_len = 200

hidden_size = 128
hidden_size_organize = 128
num_layer = 2
bidirectional = True
dropout = 0.5

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

batch_size = 512
test_batch_size = 512
try_batch_size = 1

# main settings

try_text_path = f"{curdir}\\nlp_tool\\text\\try.txt"
