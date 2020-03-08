# -*- coding: utf-8 -*-
import redis,time

FROM_HOST='192.168.1.102' #conf.get_redis_host() #'192.168.1.102' #
print('Redis FROM_HOST:',FROM_HOST)
pfrom = redis.ConnectionPool(host=FROM_HOST, port=6379, decode_responses=True,max_connections=50)
cfrom = redis.Redis(connection_pool=pfrom)

TO_HOST='127.0.0.1' #conf.get_redis_host() #'192.168.1.102' #
print('Redis TO_HOST:',TO_HOST)
pto = redis.ConnectionPool(host=TO_HOST, port=6379, decode_responses=True,max_connections=50)
cto = redis.Redis(connection_pool=pto)

allkey=[]

t0 = time.time()
allkey = cfrom.keys('*')
print('search time:',time.time()-t0)
t0 = time.time()
allkey.sort()
print('sort time:',time.time()-t0)