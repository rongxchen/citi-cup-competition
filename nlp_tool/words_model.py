# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 14:23:59 2023
@author: zhout
"""
import numpy as np
import torch
import torch.nn as nn
from nlp_tool.lib import ws  # , max_len
import torch.nn.functional as F
from torch.optim import Adam
from nlp_tool.words_dataset import get_dataloader
from nlp_tool import lib
import os
from tqdm import tqdm


class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.embedding = nn.Embedding(len(ws), 100)
        # 加入LSTM层
        self.lstm = nn.LSTM(input_size=100, hidden_size=lib.hidden_size, num_layers=lib.num_layer, batch_first=True,
                            bidirectional=lib.bidirectional, dropout=lib.dropout)
        self.fc = nn.Linear(lib.hidden_size*2, 2)
        
    def forward(self, inputs):
        """
        ----------
        input : [batch_size,max_len]
            DESCRIPTION.
        """
        x = self.embedding(inputs)  # shape:[batch_size,max_len,100]
        # x:[batch_size, max_len, hidden_size], h_n:[2*2, batch_size, hidden_size]
        x, (h_n, c_n) = self.lstm(x)  # 用正向lstm进行处理
        # 获取两个方向的最后一个output，进行concat
        output_fw = h_n[-2, :, :]
        output_bw = h_n[-1, :, :]
        output = torch.cat([output_fw, output_bw], dim=-1)  # output: [batch_size, hidden_size*2]
        
        # x = x.view([-1,max_len*100])
        out = self.fc(output)
        
        # 添加一个新的全连接层作为输出层，激活函数处理
        return F.log_softmax(out, dim=-1)

    
model = MyModel().to(lib.device)
optimizer = Adam(model.parameters(), 0.001)

if os.path.exists(r"C:\Users\chenr\PycharmProjects\Citi\nlp_tool\model\model.pkl"):
    model.load_state_dict(torch.load(r"C:\Users\chenr\PycharmProjects\Citi\nlp_tool\model\model.pkl"))
    optimizer.load_state_dict(torch.load(r"C:\Users\chenr\PycharmProjects\Citi\nlp_tool\model\optimizer.pkl"))

def train(epoch):
    for idx, (inputs, target) in enumerate(get_dataloader(train=True)):
        # 梯度归零
        inputs = inputs.to(lib.device)
        target = target.to(lib.device)
        optimizer.zero_grad()
        output = model(inputs)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        print(epoch, idx, loss.item())
        # 模型的保存
        if idx % 100 == 0:
            torch.save(model.state_dict(), r"C:\Users\chenr\PycharmProjects\Citi\nlp_tool\model\model.pkl")
            torch.save(optimizer.state_dict(), r"C:\Users\chenr\PycharmProjects\Citi\nlp_tool\model\optimizer.pkl")
        
def evaluate():
    loss_list = []
    acc_list = []
    data_loader = get_dataloader(train=False, batch_size=lib.test_batch_size)
    for idx, (inputs, target) in tqdm(enumerate(data_loader), total=len(data_loader), ascii=True, desc="测试模型"):
        inputs = inputs.to(lib.device)
        target = target.to(lib.device)
        with torch.no_grad():
            output = model(inputs)
            cur_loss = F.nll_loss(output, target)
            loss_list.append(cur_loss.cpu().item())
            # 计算准确率
            pred = output.max(dim=-1)[-1]
            cur_acc = pred.eq(target).float().mean()
            acc_list.append(cur_acc.cpu().item())
    print("total loss,acc: ", np.mean(loss_list), np.mean(acc_list))
        
# if __name__ == '__main__':
#     for i in range(10):
#         train(i)
#     evaluate()
