# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 15:53:29 2022

@author: zhout
"""

from torch.utils.data import DataLoader, Dataset
from nlp_tool.lib import ws, max_len  # , batch_size
from nlp_tool import lib
import torch
import os
import re

def tokenize(content):
    content = re.sub("<.*?>", " ", content)
    filters = ['\t', '\n', '\×97', '\×96', '#', '$', '%', '&']
    content = re.sub("|".join(filters), " ", content)
    tokens = [i.strip().lower() for i in content.split()]
    return tokens
    # 可以考虑把大写转成小写
    
class ImdbDataset(Dataset):
    def __init__(self, train=True):
        self.train_data_path = r"D:\anaconda\Machine learning datasets\python\word training data\aclImdb_v1\aclImdb\train"
        self.test_data_path = r"D:\anaconda\Machine learning datasets\python\word training data\aclImdb_v1\aclImdb\test"
        data_path = self.train_data_path if train else self.test_data_path
        
        # 把所有的文件名放入列表
        temp_data_path = [os.path.join(data_path, "pos"), os.path.join(data_path, "neg")]
        self.total_file_path = []
        for path in temp_data_path:
            file_name_list = os.listdir(path)
            file_path_list = [os.path.join(path, i) for i in file_name_list if i.endswith(".txt")]
            self.total_file_path.extend(file_path_list)

    def __getitem__(self, index):
        file_path = self.total_file_path[index]
        # 获取label
        label_str = file_path.split("\\")[-2]
        label = 0 if label_str == "neg" else 1
        # 获取内容
        tokens = tokenize(open(file_path, encoding='utf-8').read())
        
        return tokens, label
    
    def __len__(self):
        return len(self.total_file_path)

def collate_fn(batch):
    """
    Parameters
    ----------
    batch : TYPE
        DESCRIPTION.
    Returns
    -------
    None.
    """
    content, label = list(zip(*batch))
    content = [ws.transform(i, max_len=max_len) for i in content]
    content = torch.LongTensor(content)
    label = torch.LongTensor(label)
    return content, label

def get_dataloader(train=True, batch_size=lib.batch_size):
    imdb_dataset = ImdbDataset(train)
    data_loader = DataLoader(imdb_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    return data_loader

# if __name__ == '__main__':
#     for idx,(inpt,target) in enumerate(get_dataloader()):
#         print(idx)
#         print(inpt)
#         print(target)
#         break
