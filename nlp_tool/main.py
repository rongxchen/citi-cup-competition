# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 13:33:07 2023
@author: zhout
"""

str = '【一点资讯】“别上飞机！”埃航遇难中国女学生微博留言看哭了 ' \
      'www.yidianzixun.com首页段子汽车娱乐军事体育游戏一点号动漫比赛NBA财经科技数码美女健康时尚搞笑电台旅游“别上飞机！”埃航遇难中国女学生微博留言看哭了原标题：浙江女大学生在埃航空难中遇难 ' \
      '她微博下的留言看哭了北京头条客户端3月11日消息，据外交部领事保护中心11日消息，埃航失事客机上8名遇难中国公民身份初步确认，4人为中国公司员工，2人为联合国系统国际职员（包括1名中国香港居民），另2' \
      '人分别来自辽宁和浙江，为因私出行。驻埃塞使馆已与埃方建立协调联络机制，并同遇难中国公民家属取得联系，为家属处理善后提供积极协助。救援人员在封锁坠机现场进行搜救处理工作。东方IC 图ET 302航班的残骸。东方IC ' \
      '图据@浙江之声报道，今天（03.11' \
      '）中午从浙江万里学院党委宣传部了解到，校方经过与学生家属及大使馆方面核实，确认埃航空难事件中遇难的浙江女孩为浙江万里学院大四学生，接下来，学校方面将协助做好相关善后工作。记者了解到，该女学生来自金华兰溪，97' \
      '年出生，今年即将毕业，此次乘坐埃航航班，是准备去非洲旅游。另据浙江新闻客户端报道，记者向浙江万里学院核实后确认，该女生为新闻专业大四学生。记者找到了失事客机上遇难的女大学生的微博，在3月9' \
      '日，她发布了最后一条微博，定位正是在上海浦东机场。而在她的表述中，此次前往非洲旅行，是为了观看长颈鹿。同时，她将和一位朋友在目的地汇合。不少网友在她的微博留言，表示哀悼。埃塞俄比亚宣布3月11' \
      '日为全国哀悼日坠机事故发生后，埃塞俄比亚宣布3月11日为全国哀悼日，悼念所有事故遇难者。埃塞俄比亚总理阿比·艾哈迈德宣布，将对事故展开深入调查。责任编辑：李欢收藏举报相关新闻'

# str = 'Otec matka syn.'

from langdetect import detect
from langdetect import detect_langs
# import jieba.analyse
from nlp_tool.lib import ws, max_len, try_batch_size  # , try_text_path
from nlp_tool import lib
from nlp_tool.words_model_self import MyModel
# from tqdm import tqdm
# from snownlp import SnowNLP
from nlp_tool.words_dataset import tokenize
from torch.utils.data import DataLoader, Dataset
# import torch.nn.functional as F
import torch
import os

curdir = os.getcwd()


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


class WorkDataset(Dataset):
    def __init__(self):
        self.work_data_path = f"{curdir}\\nlp_tool\\text"
        
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
        tokens = tokenize(open(file_path, encoding='utf-8').read())
        label = 0
        return tokens, label

    def __len__(self):
        return len(self.total_file_path)


# 当文本过短或模糊时，判断出来的结果会不确定；
# 如果要让结果唯一，添加以下两行：
from langdetect import DetectorFactory
DetectorFactory.seed = 0

model = MyModel().to(lib.device)
if os.path.exists(f"{curdir}\\nlp_tool\\model\model3LSTM.pkl"):
    model.load_state_dict(torch.load(f"{curdir}\\nlp_tool\\model\model3LSTM.pkl"))

def get_language(string):
    # 判断语言种类
    return [detect(string), detect_langs(string)]
    
def get_dataloader(batch_size=lib.try_batch_size):
    imdb_dataset = WorkDataset()
    data_loader = DataLoader(imdb_dataset, batch_size=try_batch_size, shuffle=False, collate_fn=collate_fn)
    return data_loader

# if __name__ == '__main__':
#     string = open(try_text_path, encoding = "utf-8").read()
#     # 之后可以直接识别文件名，如果文件名包含语言，那么就不用detect语言了
#     if False:  # get_language(string) == "zh-cn":
#         # 中文之后再做
#         s_cn = SnowNLP(string)
#     elif True:#get_language(string) == "en":
#         ans_list = []
#         data_loader = get_dataloader(batch_size=lib.try_batch_size)  # 这里batch_size得改一改
#         for idx, (inputs, label) in tqdm(enumerate(data_loader), total=len(data_loader), ascii=True, desc="测试模型"):
#             inputs = inputs.to(lib.device)
#             with torch.no_grad():
#                 output = model(inputs).max(dim=-1)[-1]
#                 ans_list.append(output.item())
#                 #cur_loss = F.nll_loss(output, target)
#                 #loss_list.append(cur_loss.cpu().item())
#                 # 计算准确率
#                 #pred = output.max(dim=-1)[-1]
#                 #cur_acc = pred.eq(target).float().mean()
#                 #acc_list.append(cur_acc.cpu().item())
#         print("answer: ", ans_list)
#         # print("answer: ", np.mean(loss_list),np.mean(acc_list))
        