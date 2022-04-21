# coding: utf-8
import sys, os
import urllib
import tarfile, math
import hashlib
import numpy as np
import random
import pdb
import gc
import time 
from collections import Counter
'''
    2020/2/6
    ratings文件载入：user唯一标志符user_id,artist标志符：name(艺术家的id信息有缺失)      len of item:292589  num of ratings:17559530   
    len of user:359347
    0.000167    0.0167%
    当保存新的评分文件的时候，我们既保存了新的评分方式：0-5，也保存了旧的plays指标，防止需要重新设计
    保存方式：txt文本，间隔“，”，[user item rating plays]
'''
def smoothed_rating(times_played):
    rating = math.log(times_played)
    if rating > 6:
        rating = 6
    rating = rating*2/3 + 1
    rating = int(rating+0.5)
    if rating < 1 or rating >5:
        pdb.set_trace()
    return rating

# load all country's name
countrys = set()
with open('./usersha1-profile.tsv', 'r',encoding='utf-8') as plays_file:
    for line in plays_file:
        (user_id,gender,age,country,date) = line.strip().split('\t')
        if country != '':
            countrys.add(country)
countrys = list(countrys)

# load item information
artist_names = dict()
lines_read = 0
item_new_id = 0 
with open('./usersha1-artmbid-artname-plays.tsv', 'r',encoding='utf-8') as plays_file:
    for line in plays_file:
        lines_read += 1
        (user_id, artist_id, artist_name, plays) = line.strip().split('\t')
        if artist_name not in artist_names.keys():
            artist_names[artist_name] = item_new_id
            item_new_id += 1
        if lines_read % 100000 == 0:
            print("%d lines read..." % lines_read)
# two {'sep 20, 2008', 'dec 27, 2008'} 

print("len of item:"+str(item_new_id))      
print("num of ratings:"+str(lines_read))

# load gender age country
# 如果feature读取不满意，只需要改这里
# 这部分可以单独写在外面，因为user的新id是在这个文件读取时设置的

user_ids=dict()
user_new_id = 0

gender_list=[]
age_list=[]
country_list=[]
ages = [25,35]
with open('./usersha1-profile.tsv', 'r',encoding='utf-8') as plays_file:
    for line in plays_file:
        (user_id,gender,age,country,date) = line.strip().split('\t')

        if user_id not in user_ids.keys():
            user_ids[user_id] = user_new_id
            user_new_id += 1

        if gender == 'f':
            gender_list.append(np.array([1,0]))
        elif gender == 'm':
            gender_list.append(np.array([0,1]))
        else:
            gender_list.append(np.array([0,0]))
        if age =='':
            age_list.append(np.array([0,0,0]))
        elif int(age) < ages[0]:
            age_list.append(np.array([0,0,1]))
        elif int(age) < ages[1]:
            age_list.append(np.array([0,1,0]))
        else:
            age_list.append(np.array([1,0,0]))
        if country == '':
            country_list.append(np.array([0 for i in range(len(countrys))]))
        else:
            country_list.append(np.array([1 if i in country else 0 for i in countrys]))
print("len of user:"+str(user_new_id))
genders= np.array(gender_list)
ages = np.array(age_list)
countrys2 = np.array(country_list)

# countrys.shape (359347, 239) ages.shape (359347, 3)

np.save("./genders.npy",genders)
np.save("./ages.npy",ages)
np.save("./countrys.npy",countrys2)

# preferences_file = open('./usersha1-artmbid-artname-plays.txt','a')
lines_read = 0
etra_id = ['sep 20, 2008', 'dec 27, 2008']
ratings_list=[]
with open('./usersha1-artmbid-artname-plays.tsv', 'r',encoding='utf-8') as plays_file:
    for line in plays_file:  
        lines_read += 1
        (user_id, artist_id, artist_name, plays) = line.strip().split('\t')
        if user_id not in etra_id:
            if int(plays) != 0:
                user_new_id = user_ids[user_id]
                artist_new_name = artist_names[artist_name]

                rating = smoothed_rating(int(plays))
                ratings_list.append(rating)
                # preferences_file.write(str(user_new_id) + ',' + str(artist_new_name) + ',' + str(rating) + ',' + str(plays) +'\n')

        if lines_read % 100000 == 0:
            print("%d lines read..." % lines_read)
        
counted = Counter(ratings_list)
pdb.set_trace()
# preferences_file.flush()
print("store ratings ok")

gc.collect()

