# -*- coding: utf-8 -*-
import _config as conf
import redis,time
import lib.dblib as ldb

HOST='192.168.1.102' #conf.get_redis_host() #'192.168.1.102' #
print('Redis host:',HOST)
pool = redis.ConnectionPool(host=HOST, port=6379, decode_responses=True,max_connections=50)
cache = redis.Redis(connection_pool=pool)

sorted_feature_key=[]
sorted_option_key=[]

t0 = time.time()
allkey = cache.keys('*')
allkey.sort()
print('search time:',time.time()-t0)

t0 = time.time()
for key in allkey:
	kName,kTime,kDate=key.split(',')
	if len(kName)==10:
		sorted_option_key.append(','.join([kDate,kTime,kName]))
	else:
		sorted_feature_key.append(','.join([kDate,kTime,kName]))
print('list time:',time.time()-t0)
	
t0 = time.time()
sorted_feature_key.sort()
sorted_option_key.sort()
print('sort time:',time.time()-t0)
	
for i in range(len(sorted_feature_key)):
	kDate,kTime,kName=sorted_feature_key[i].split(',')
	sorted_feature_key[i]=','.join([kName,kTime,kDate])

for i in range(len(sorted_option_key)):
	kDate,kTime,kName=sorted_option_key[i].split(',')
	sorted_option_key[i]=','.join([kName,kTime,kDate])

#dbc=ldb.DBConn(HOST,'sa','geniustom',)
'''
tx00_data=[]	
for tx in sorted_feature_key:
	if tx.find('TX00')>0:
		print(cache.hgetall(tx))
		#tx00_data.append()
'''

for k in allkey:
	ba,c4,c3,c2,c1=cache.hmget(k,'nBestBid5','nBestBid4','nBestBid3','nBestBid2','nBestBid1')
	bb,a4,a3,a2,a1=cache.hmget(k,'nBestAsk5','nBestAsk4','nBestAsk3','nBestAsk2','nBestAsk1')
	if ba==None or bb==None:
		print(k,ba,bb)
		continue
	if float(ba)%100==0: #and float(ba)>float(c4)*5  :
		print(k,'nBestBid5',ba,c4,c3,c2,c1)
		#cache.hset(k,'nBestBid5',float(ba)/100)
	if float(bb)%100==0: #and float(bb)>float(a4)*5  :
		print(k,'nBestAsk5',bb,a4,a3,a2,a1)
		#cache.hset(k,'nBestAsk5',float(bb)/100)