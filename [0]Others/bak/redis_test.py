# -*- coding: utf-8 -*-

import redis   # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库

# host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
r = redis.Redis(host='192.168.1.200', port=32768, decode_responses=True)   
r.set('foo', 'bar')  # key是"foo" value是"bar" 将键值对存入redis缓存
print(r['foo'])
print(r.get('foo'))  # 取出键name对应的值
print(type(r.get('foo')))