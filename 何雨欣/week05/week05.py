#!/usr/bin/env python3
#coding: utf-8

#基于训练好的词向量模型进行聚类
#聚类采用Kmeans算法
import math
import re
import json
import jieba
import numpy as np
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from collections import defaultdict

#输入模型文件路径
#加载训练好的模型
def load_word2vec_model(path):
    model = Word2Vec.load(path)
    return model

def load_sentence(path):
    sentences = set()
    with open(path, encoding="utf8") as f:
        for line in f:
            sentence = line.strip()
            sentences.add(" ".join(jieba.cut(sentence)))
    print("获取句子数量：", len(sentences))
    return sentences

#将文本向量化
def sentences_to_vectors(sentences, model):
    vectors = []
    for sentence in sentences:
        words = sentence.split()  #sentence是分好词的，空格分开
        vector = np.zeros(model.vector_size)
        #所有词的向量相加求平均，作为句子向量
        for word in words:
            try:
                vector += model.wv[word]
            except KeyError:
                #部分词在训练中未出现，用全0向量代替
                vector += np.zeros(model.vector_size)
        vectors.append(vector / len(words))
    return np.array(vectors)


def distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))


def main():
    model = load_word2vec_model("model.w2v") #加载词向量模型
    sentences = load_sentence("titles.txt")  #加载所有标题
    vectors = sentences_to_vectors(sentences, model)   #将所有标题向量化

    n_clusters = int(math.sqrt(len(sentences)))  #指定聚类数量
    print("指定聚类数量：", n_clusters)
    kmeans = KMeans(n_clusters)  #定义一个kmeans计算类
    kmeans.fit(vectors)          #进行聚类计算

    sentence_label_dict = defaultdict(list)
    for sentence, label in zip(sentences, kmeans.labels_):  #取出句子和标签
        sentence_label_dict[label].append(sentence)         #同标签的放到一起


    all_label = kmeans.labels_
    distance_list = defaultdict(list)
    for vec_now, label_now in enumerate(all_label):
        vec = vectors[vec_now]
        center = kmeans.cluster_centers_[label_now]
        distance_now = distance(vec, center)
        distance_list[label_now].append(distance_now)


    for label, sentences in sentence_label_dict.items():
        print("cluster %s :" % label)
        distance_list_now = distance_list[label]
        combine = list(zip(sentences, distance_list_now))
        sorted_combined = sorted(combine, key=lambda x: x[1])
        sentences_sorted, distance_sorted = zip(*sorted_combined)
        for i in range(min(10, len(sentences_sorted))):  #随便打印几个，太多了看不过来
            print("距离:{:.5f} —— {}".format(distance_sorted[i], sentences_sorted[i].replace(" ", "")))
        print("---------")

if __name__ == "__main__":
    main()

