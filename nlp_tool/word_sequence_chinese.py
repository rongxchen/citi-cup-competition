# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 12:41:08 2023
@author: zhout
"""

import jieba.analyse
 
text = '''
关键词是能够表达文档中心内容的词语、常用于计算机系统标引论文内容特征、
信息检索、系统汇集以供读者检阅。关键词提取是文本挖掘领域的一个分支，是文本检索、
文档比较、摘要生成、文档分类和聚类等文本挖掘研究的基础性工作
'''
 
keywords = jieba.analyse.extract_tags(text, topK=5, withWeight=False, allowPOS=())
print(keywords)
