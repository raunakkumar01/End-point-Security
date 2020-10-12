# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 10:30:07 2020

@author: windows
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pathlib
import re
import csv
import json
import datetime

import pymongo
from pymongo import MongoClient
from pymongo import errors
from bson import BSON
##############################Global variables ################################

database_name = 'tmp-log-database'
path = pathlib.Path('C:/ProgramData/Docker/volumes/vol101/logs')

diffLogForm = ['**/*.log','**/*.csv']
diffLogInfoForm = ['**/*.info']


fet = {}
data = {}

regex = [ r'"?\d+[-\d+]+"?', r'"?(?P<time>[\d+:]+)[.\d]*?"?']
##############################Few functions of our use#########################
def appendToDic(data,dic,key):
    if key in dic.keys():
        dic[mtmp].append(data)
    else:
        tdata =[]
        tdata.append(data)
        dic[mtmp]= tdata

def getMatchInfo(source,info):
    k=0
    rdata = []
    i=0
    fl =2
    sz = len(info)
    while(i<sz):
        if(info[i]=='%' or info[i]=='{'):
            fl=0
        elif(fl==2 and k<len(source) and source[k]==info[i]):
            k = k+1
            i=i+1
            continue
        if(info[i]==':'):
            s = ''
            fl = 1
        elif(info[i]=='}'):
            vl =''
            fl=2
            while(k<len(source) and source[k]!=info[i+1]):
                vl+= source[k]
                k = k+1
            rdata.append(vl)
        i += 1
    return rdata

def getInfoColumns(loginfo):
    info = []
    for i in loginfo.split('%')[1:]:
        info.append(i.split('}')[0].split(':')[1])
    return info
        
def getFiles(pat):
    return [ f for f in path.glob(pat)]


def gettimestamp(df,key):
    fl = [None,None]
    vl = []
    for col in df.columns:
        if('date' == col.lower()):
            fl[0]=col
        if('time' == col.lower() or 'timestamp'  == col.lower() or 'timegenerated'  == col.lower() or 'timecreated'  == col.lower()):
            fl[1]=col
    x = []
    print(fl)
    if(fl[0]==None):
        for i in df[fl[1]]:
            if(key == 'nginx'):
                x.append(datetime.datetime.strptime(i[:-6], "%d/%b/%Y:%H:%M:%S"))
            elif(key == 'application' or key =='security' or key=='system' or key=='rdp'):
                x.append(datetime.datetime.strptime(i[:-3], "%m/%d/%Y %H:%M:%S"))
            elif(key == 'ssh'):
                mx = datetime.datetime.now()
                x.append(mx.combine(mx,datetime.datetime.strptime(i[:-4], "%H:%M:%S").time()))
    else:
        if(key == 'ftp' or key == 'iis'):
            mx = None
            for row in df[fl[0]]:
                mx = datetime.datetime.strptime(row,"%Y-%m-%d")
            i=0
            for row in df[fl[1]]: 
                tx =(datetime.datetime.strptime(row,"%H:%M:%S"))
                x.append(mx.combine(mx, tx.time()))
                i+=1
            
    return x  
        
    

##############################Find all the path names#########################
print("###################Get all the paths of .log,.csv format###############################")


file_list = getFiles('**/*.log')

file_list_info = [ f for f in path.glob('**/*.info')]

file_list_csv = getFiles('**/*.csv')

###################################Extract the features#############################
#####################################For LOG################################
print("###################Extract features and corresponding data of .log format##############")

for file in range(len(file_list_info)):#get the columns
    with open(file_list_info[file],'r') as f:
        tmpdata = f.read()
        tp = file_list_info[file]._str
        mtmp = tp.split('\\')[-2] #+ '.csv'
        if mtmp not in fet.keys():
            fet[mtmp] = tmpdata
        
for file in range(len(file_list)):#get the row values for with respect to the columns
    with open(file_list[file],'r') as f:
        ndata ={}
        tmpdata = f.read()
        newdata = tmpdata.split('\n')
        tdata = []
        tp = file_list[file]._str
        mtmp = tp.split('\\')[-2] #+ '.csv'        
        s = ''
        fl = 0
       
        for r in newdata:
            if  len(r) == 0:
                continue
            if r[0] == '#':
                continue
            else:
                rdata = getMatchInfo(r, fet[mtmp])
                appendToDic(rdata, data, mtmp)
         
for file in range(len(file_list)):# convert each into dataframe
    tp = file_list[file]._str
    mtmp = tp.split('\\')[-2] #+ '.csv'          
    df = pd.DataFrame(data[mtmp],columns = getInfoColumns(fet[mtmp]))
    print(mtmp)
    df['timestamp'] = gettimestamp(df,mtmp) #datetime.datetime.now()  
    print(df['timestamp'])
    data[mtmp] = df
        
#####################################For CSV################################

print("###################Extract features and corresponding data of .csv format##############")

for file in range(len(file_list_csv)):# convert each into dataframe
    tp = str(file_list_csv[file])
    mtmp = tp.split('\\')[-1].split('.')[0]
    df = pd.read_csv(file_list_csv[file] , skiprows = 1)
    # print(mtmp)
    df['timestamp'] = gettimestamp(df,mtmp) #datetime.datetime.now()   
    data[mtmp]=df

####################################Create database Mongodb#################

client = MongoClient()
db = client[database_name]
    
####################################Write into database#####################
print("###################Writing collection into database##################################")

for key in data:
      print(key)
      record = data[key].to_dict(orient='records')
      # record =BSON.encode(json.loads(data[key].T.to_json()).values())
      # db[key].insert_many(record)
      for row in record:
          db[key].update(row, row, upsert = True )
     
    
    
        
        