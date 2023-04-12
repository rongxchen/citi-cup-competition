# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:56:07 2023

@author: zhout
"""

from langdetect import detect
from langdetect import detect_langs
# import jieba.analyse
from nlp_tool.lib import ws, max_len, try_batch_size  # , try_text_path
from nlp_tool import lib
from nlp_tool.words_model_self import MyModel
# from lib import ws, max_len, try_batch_size  # , try_text_path
# import lib
# from words_model_self import MyModel
from tqdm import tqdm
from snownlp import SnowNLP
from nlp_tool.words_dataset import tokenize
# from words_dataset import tokenize
from torch.utils.data import DataLoader, Dataset
# import torch.nn.functional as F
import torch
import os

text_list = ["Story of a man who has unnatural feelings for a pig. Starts out with a opening scene that is a terrific "
             "example of absurd comedy. A formal orchestra audience is turned into an insane, violent mob by the "
             "crazy chantings of it's singers. Unfortunately it stays absurd the WHOLE time with no general narrative "
             "eventually making it just too off putting. Even those from the era should be turned off. The cryptic "
             "dialogue would make Shakespeare seem easy to a third grader. On a technical level it's better than you "
             "might think with some good cinematography by future great Vilmos Zsigmond. Future stars Sally Kirkland "
             "and Frederic Forrest can be seen briefly."]


def collate_fn(batch):
    """
    Parameters
    ----------
    batch : TYPE
    """

    content, label = list(zip(*batch))
    content = [ws.transform(i, max_len=max_len) for i in content]
    content = torch.LongTensor(content)
    label = torch.LongTensor(label)
    return content, label


class WorkDataset(Dataset):
    def __init__(self, lst):
        self.text_list = lst

    def __getitem__(self, index):
        # 得到一组词并转化为token
        tokens = tokenize(self.text_list[index])
        label = 0
        return tokens, label

    def __len__(self):
        return len(self.text_list)


# 当文本过短或模糊时，判断出来的结果会不确定；
# 如果要让结果唯一，添加以下两行：
from langdetect import DetectorFactory
DetectorFactory.seed = 0

curdir = os.getcwd()
model = MyModel().to(lib.device)
if os.path.exists(f"{curdir}\\nlp_tool\model\model3LSTM.pkl"):
    model.load_state_dict(torch.load(f"{curdir}\\nlp_tool\model\model3LSTM.pkl"))

def get_language(string):
    # 判断语言种类
    return [detect(string), detect_langs(string)]
    
def get_dataloader(batch_size=lib.try_batch_size, text_lst=None):
    imdb_dataset = WorkDataset(text_lst)
    data_loader = DataLoader(imdb_dataset, batch_size=try_batch_size, shuffle=False, collate_fn=collate_fn)
    return data_loader


"""直接调用emotion_detection并传入一个list即可传出一个answer"""


def emotion_detection(text_list, language='en'):
    ans_list = []
    if language == "zh-cn":
        for i in tqdm(text_list, desc="正在运行cn-nlp模型"):
            s_cn = SnowNLP(i).sentiments
            if s_cn > 0.5:
                ans_list.append(1)
            else:
                ans_list.append(0)
    elif language == "en":
        data_loader = get_dataloader(batch_size=lib.try_batch_size, text_lst=text_list)
        for idx, (inputs, label) in tqdm(enumerate(data_loader), total=len(data_loader), ascii=True,
                                         desc="正在运行en-nlp模型"):
            inputs = inputs.to(lib.device)
            with torch.no_grad():
                # 得到输出并生成answer list
                output = model(inputs).max(dim=-1)[-1]
                ans_list.append(output.item())
    else:
        print("no currently matching language")

    print(ans_list)
    return ans_list


# if __name__ == '__main__':
    # emotion_detection(text_list)
