# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 20:09:45 2023
@author: zhout
"""

from torch.utils.data import DataLoader, Dataset
from nlp_tool.lib import ws, max_len, batch_size
# import lib
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


class WorkDataset(Dataset):
    def __init__(self):
        self.work_data_path = r"C:\Users\chenr\PycharmProjects\Citi\nlp_tool\text"

        # 把所有的文件名放入列表
        # temp_data_path = [os.path.join(data_path,"pos"),os.path.join(data_path,"neg")]
        self.total_file_path = []
        file_name_list = os.listdir(self.work_data_path)
        file_path_list = [os.path.join(self.work_data_path, i) for i in file_name_list if i.endswith(".txt")]
        self.total_file_path.extend(file_path_list)

    def __getitem__(self, index):
        file_path = self.total_file_path[index]
        # 获取label
        # label_str = file_path.split("\\")[-2]
        # label = 0 if label_str == "neg" else 1
        # 获取内容
        label = 0
        tokens = tokenize(open(file_path, encoding='utf-8').read())
        print(tokens)
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


def get_dataloader(train=True, batch_size=batch_size):
    imdb_dataset = WorkDataset()
    data_loader = DataLoader(imdb_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    return data_loader


# if __name__ == '__main__':
#     for idx, (inpt, target) in enumerate(get_dataloader()):
#         print(idx)
#         print(inpt)
#         print(target)
#         break
