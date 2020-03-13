# -*- coding: utf-8 -*-
import _config as conf
import redis,time
import lib.dblib as ldb


HOST=conf.get_redis_host() #conf.get_redis_host() #'192.168.1.102' #
print('Redis host:',HOST)
pool = redis.ConnectionPool(host=HOST, port=6379, decode_responses=True,max_connections=50)
cache = redis.Redis(connection_pool=pool)

sorted_feature_key=[]
sorted_option_key=[]


def InsertIfNotExist(redis_key,query,data,keys,vals):
	try:
		sql='IF NOT EXISTS (SELECT * FROM RawData WHERE Market=%s and Date=%s and Time=%s) INSERT INTO RawData(%s) VALUES(%s)'%(
				"'"+data['Market']+"'",
				"'"+data['Date']+"'",
				"'"+data['Time']+"'",
				','.join(keys),
				','.join(vals)
				)
		#print(sql)	
		r,cnt=query.ExecDB(sql)
		#print(r,cnt)
		#if cnt==1:	print("Key inserted~")
		#if cnt==-1:	print("Key duplicate,do nothing~")
	except:
		print('-----------------------------------')
		print(redis_key,"error:")
		print(data)
		print('-----------------------------------')
		return False

	return True


def CheckKeyIsInvalid(key):
	m,t,d= str(key).split(',')
	today=time.strftime("%y%m%d",time.localtime())
	if m=='' or t=='' or d=='': 
		print('Key',key,' is invalid')
		return True
	if int(today)>int(d): 
		print('Key',key,' is expire')
		return True
	return False	
	

if __name__ == '__main__':
	###################################################################
	t0 = time.time()
	allkey = cache.keys('*')
	allkey.sort()
	print('search time:',time.time()-t0)
	###################################################################
	t0 = time.time()
	for key in allkey:
		kName,kTime,kDate=key.split(',')
		if len(kName)==10:
			sorted_option_key.append(','.join([kDate,kTime,kName]))
		else:
			sorted_feature_key.append(','.join([kDate,kTime,kName]))
	print('list time:',time.time()-t0)
	###################################################################	
	t0 = time.time()
	sorted_feature_key.sort()
	sorted_option_key.sort()
	print('sort time:',time.time()-t0)
	print('future data cnt:',len(sorted_feature_key))
	print('option data cnt:',len(sorted_option_key))
	###################################################################	
	for i in range(len(sorted_feature_key)):
		kDate,kTime,kName=sorted_feature_key[i].split(',')
		sorted_feature_key[i]=','.join([kName,kTime,kDate])
	
	for i in range(len(sorted_option_key)):
		kDate,kTime,kName=sorted_option_key[i].split(',')
		sorted_option_key[i]=','.join([kName,kTime,kDate])
	
	
	dbcf=ldb.DBConn('127.0.0.1','sa','geniustom','FutureData')
	dbco=ldb.DBConn('127.0.0.1','sa','geniustom','OptionData')
	qf=ldb.Query(dbcf.conn)
	qc=ldb.Query(dbco.conn)
	
	###################################################################
	t0 = time.time()
	fk_invalid_cnt=0
	for fk in sorted_feature_key:
		fdata=cache.hgetall(fk)
		if len(fdata)<37:
			if CheckKeyIsInvalid(fk)==True: cache.delete(fk) 
			fk_invalid_cnt+=1
			continue
		keys=[]
		vals=[]
		for item in fdata:
			keys.append(item)
			vals.append("'"+fdata[item]+"'")
		if InsertIfNotExist(fk,qf,fdata,keys,vals)==True:
			cache.delete(fk)
			#print('success..redis key',fk,'deleted')
		else:
			pass
	print('future sync time:',time.time()-t0,',invalid_cnt=',fk_invalid_cnt)
	###################################################################
	t0 = time.time()
	ok_invalid_cnt=0
	for ok in sorted_option_key:
		odata=cache.hgetall(ok)
		if len(fdata)<37:
			if CheckKeyIsInvalid(ok)==True: cache.delete(ok) 
			ok_invalid_cnt+=1
			continue
		keys=[]
		vals=[]
		for item in odata:
			keys.append(item)
			vals.append("'"+odata[item]+"'")
		if InsertIfNotExist(ok,qc,odata,keys,vals)==True:
			cache.delete(ok) 
			#print('success..redis key',ok,'deleted')
		else:
			pass
	print('option sync time:',time.time()-t0,',invalid_cnt=',ok_invalid_cnt)
	###################################################################



'''
tx00_data=[]	
for tx in sorted_feature_key:
	if tx.find('TX00')>0:
		print(cache.hgetall(tx))
		#tx00_data.append()
'''
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
'''