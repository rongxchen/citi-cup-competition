# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 16:52:56 2023
@author: zhout
"""

"""实现word2sequence"""


class Word2Sequence:
    UNK_TAG = "UNK"
    PAD_TAG = "PAD"
    
    UNK = 0
    PAD = 1
    
    def __init__(self):
        self.inverse_dict = None
        self.dict = {
            self.UNK_TAG: self.UNK,
            self.PAD_TAG: self.PAD
        }
        self.count = {}  # 统计词频
    
    def fit(self, sentence):
        """把单个句子保存到dict中"""
        
        for word in sentence:
            self.count[word] = self.count.get(word, 0) + 1
    
    def build_vocab(self, Min=5, Max=None, max_features=None):
        """
        Parameters
        ----------
        Min : 最小出现的次数
        Max : 最大出现的次数
        max_features : 一共保留多少个词语
        """

        # 删除count中词频小于min的word
        if Min is not None:
            self.count = {word: value for word, value in self.count.items() if value > Min}
        # 删除count中词频大于max的word
        if Max is not None:
            self.count = {word: value for word, value in self.count.items() if value < Max}
        # 限制保留的词语数
        if max_features is not None:
            temp = sorted(self.count.items(), key=lambda x: x[-1], reverse=True)[:max_features]
            self.count = dict(temp)
        
        for word in self.count:
            self.dict[word] = len(self.dict)
        # 得到一个反转的dict字典
        self.inverse_dict = dict(zip(self.dict.values(), self.dict.keys()))
    
    def transform(self, sentence, max_len=None):
        """
        把句子转化为序列
        Parameters
        ----------
        sentence :[word1,word2...]
        max_len: 增长或裁剪句子
        ---
        """
        # for word in sentence:
        # self.dict.get(word,self.UNK)
        if max_len is not None:
            if max_len > len(sentence):
                sentence = sentence + [self.PAD_TAG] * (max_len - len(sentence))  # 加长句子
            if max_len < len(sentence):
                sentence = sentence[:max_len]  # 裁剪句子
        return [self.dict.get(word, self.UNK) for word in sentence]

    def inverse_transform(self, indices):
        """
        把序列转化为句子
        Parameters
        ----------
        indices : 序列
        Returns
        -------
        """
        return [self.inverse_dict.get(idx) for idx in indices]
    
    def __len__(self):
        return len(self.dict)

# if __name__ == '__main__':
#     #ws = Word2Sequence()
#     #ws.fit(["Who","am","I",""])
#     #ws.fit(["I","am","myself",""])
#     #ws.build_vocab(Min = 0)
#     #print(ws.dict)
#     #保存处理后的word sequence
#     import pickle
#     import os
#     from words_dataset import tokenize
#     from tqdm import tqdm
#     ws = Word2Sequence()
#     path = r"D:\anaconda\Machine learning datasets\python\word training data\aclImdb_v1\aclImdb\train"
#     temp_data_path = [os.path.join(path,"pos"),os.path.join(path,"neg")]
#     for data_path in temp_data_path:
#         file_paths = [os.path.join(data_path, file_name) for file_name in os.listdir(data_path) if file_name.endswith("txt")]
#         for file_path in tqdm(file_paths):
#             sentence = tokenize(open(file_path,encoding="utf-8").read())
#             ws.fit(sentence)
#     ws.build_vocab(Min = 10,max_features=10000)
#     pickle.dump(ws,open("./model/ws.pkl","wb"))
#     print(len(ws))
