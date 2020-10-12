# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 18:31:35 2020

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
from datetime import datetime,timedelta

import pymongo
from pymongo import MongoClient

##################################Global config variable######################
database_name = 'tmp-log-database'

honey_usr = ['honeypot']
honeypot_files = ['user.txt']

data ={}
##################################Connect to the database#####################
client = MongoClient()
db = client[database_name]

collection_names = db.collection_names()

##################################Get the table values########################
#RULE 1 we try checking if we have get commands for the password file form our server if any user is trying to access the 
# all the files with password details.

#Rule 2 if anyone is trying to log in with our honeypot passwords then also try detectig that

def getissue_rule1(df,issues,key):
    #RULE 1 analysis
    ##Analysis of IIS logs
    for file in honeypot_files:
        for idx,xf in df.iterrows():
            if(key == 'iis'):        
                if('GET' in xf['cs-method']) and (file in xf['cs-uri-stem']):
                    issue = []
                    issue.append(xf['s-ip'])
                    issue.append(xf['cs(Referer)'])
                    issue.append('Rule1')
                    issues.append(issue)
        ##Analysis of IIS logs
            if(key == 'ftp'):
                if('NLST' in xf['cs-method']) and (file in xf['cs-uri-stem']):
                    issue = []
                    issue.append(xf['s-ip'])
                    issue.append(xf['cs-username'])
                    issue.append('Rule1')
                    issues.append(issue)
        ##Analysis of nginx logs
            if(key == 'nginx'):
                if('GET' in xf['verb']) and (file in xf['request']):
                    issue = []
                    issue.append(xf['clientip'])
                    issue.append(xf['referrer'])
                    issue.append('Rule1')
                    issues.append(issue)
        ##Analysis of SSH logs
            if(key == 'ssh'):
                if('scp' in xf['message']) and (file in xf['message']):
                    issue = []
                    issue.append(xf['pid'])
                    issue.append(xf['message'])
                    issue.append('Rule1')
                    issues.append(issue)
                
def getissue_rule2(df,issues,key):
    ##Rule2 Analysis for this store the source IP and the username to be used to acces file
    #analysis of ssh
    for usr in honey_usr:
        for idx,xf in df.iterrows():
            if(key == 'ssh'):    
                if('Accepted' in xf['command']) and (usr in xf['message']):
                     issue = []
                     issue.append(xf['pid'])
                     issue.append(xf['message'])
                     issue.append('Rule1')
                     issues.append(issue)
        
        #analysis of ssh
            if(key == 'ftp'):
                if(usr in xf['cs-username']) and ('DataChannelOpened' in xf['cs-method']):
                     issue = []
                     issue.append(xf['s-ip'])
                     issue.append(xf['cs-username'])
                     issue.append('Rule1')
                     issues.append(issue)
    
########################################Read each of the service logs and then find the issues####

issues = []#ip referere which rule violated

for key in collection_names:
    # df = pd.DataFrame(list(db[key].find()))
    df = pd.DataFrame(list(db[key].find({"timestamp":{"$gte": (datetime.now()-timedelta(1))}})
))
    if '_id' in df.columns:
        df = df.drop(['_id'],axis  =1)
    
    
    getissue_rule1(df, issues,key)
    getissue_rule2(df, issues,key)
    
    # print(key)
    # print(df)
    
#########################################################################
print(issues)





    
    
    