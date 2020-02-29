#REF: https://easontseng.blogspot.com/2017/
# -*- coding: utf-8 -*-
import lib.util as lu
import _getpass as getpass
import pythoncom, time, os,threading
import comtypes.client as cc
import math
import comtypes.gen.SKCOMLib as sk

from datetime import datetime,date
import matplotlib.pyplot as plt
from logging import handlers

#使用python来操作redis用法详解  https://www.jianshu.com/p/2639549bedc8
import redis   # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
cache = redis.Redis(connection_pool=pool)
#cache = redis.Redis(host='localhost', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
#redis.


class CAP_Thread(threading.Thread):
	#建立事件類別
	class skQ_events:
		def __init__(self, parent):
			self.MSG=parent.MSG
			self.parent=parent
		def OnConnection(self, nKind, nCode):
			self.parent.log.critical('[v]OnConnection:', self.MSG(nKind),nKind, self.MSG(nCode))	
			if nKind==3003: self.parent.step2()
		def OnNotifyServerTime(self,sHour,sMinute,sSecond,nTotal):
			self.parent.watchdog=0
			self.parent.timestr="{}:{}:{}".format(str(sHour).zfill(2),str(sMinute).zfill(2),str(sSecond).zfill(2))
			self.parent.timestamp=nTotal
			#log.info(sHour,":",sMinute,":",sSecond,"--",nTotal)
		def OnNotifyKLineData(self,bstrStockNo,bstrData):
			pass
		def OnNotifyStockList(self,sMarketNo,bstrStockData):
			pass

		def OnNotifyTicks(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			self.parent.get_tick(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		def OnNotifyHistoryTicks(self, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			self.parent.get_tick(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		def OnNotifyFutureTradeInfo(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
			self.parent.get_market(bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount)
		def OnNotifyBest5(self,sMarketNo,sStockIdx,nBestBid1,nBestBidQty1,nBestBid2,nBestBidQty2,nBestBid3,nBestBidQty3,nBestBid4,nBestBidQty4,nBestBid5,nBestBidQty5,nExtendBid,nExtendBidQty,nBestAsk1,nBestAskQty1,nBestAsk2,nBestAskQty2,nBestAsk3,nBestAskQty3,nBestAsk4,nBestAskQty4,nBestAsk5,nBestAskQty5,nExtendAsk,nExtendAskQty,nSimulate):
			pass
		def OnNotifyQuote(self,sMarketNo,sStockidx):
			#self.parent.log.info(sMarketNo,sStockidx)
			pStock = sk.SKSTOCK()
			self.parent.skQ.SKQuoteLib_GetStockByIndex(sMarketNo, sStockidx, pStock)
			self.parent.get_price(self,pStock.bstrStockNo,pStock.nOpen/math.pow(10,pStock.sDecimal),pStock.nHigh/math.pow(10,pStock.sDecimal),pStock.nLow/math.pow(10,pStock.sDecimal),pStock.nClose/math.pow(10,pStock.sDecimal),pStock.nTQty)


		
	def __init__(self,tid,tpw,log,price_data,tick_data,market_data):
		threading.Thread.__init__(self)
		cc.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\lib\SKCOM.dll')
		self.feature_list=[]
		self.feature_code=[]
		self.feature_dict={}
		self.watchdog=0
		self.timestr=''
		self.timestamp=0
		self.id=tid
		self.pw=tpw
		self.log=log
		self.tick_data=tick_data
		self.market_data=market_data
		self.price_data=price_data
		self.sk_init()
		
	def sk_init(self):
		import json
		self.skC=cc.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
		self.skQ=cc.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
		self.EventQ=self.skQ_events(self)
		self.ConnectionQ = cc.GetEvents(self.skQ, self.EventQ)
		input_file = open ('market_info/feature_code.json')
		self.feature_code = json.load(input_file)
		input_file.close

	def join(self):
		self.log.critical("[9]LeaveMonitor:", self.MSG(self.skQ.SKQuoteLib_LeaveMonitor()))	
		threading.Thread.join(self)

			
	def MSG(self,code):
		return self.skC.SKCenterLib_GetReturnCodeMessage(code)
	
	def delay(self,sec):
		for i in range(sec):
			time.sleep(1)
			pass
	
	def step1(self): #登入
		self.log.critical("[1]Login:", self.MSG(self.skC.SKCenterLib_Login(self.id,self.pw)))
		self.log.critical("[2]EnterMonitor:", self.MSG(self.skQ.SKQuoteLib_EnterMonitor()))
		

	def step2(self): #收取量價資訊
		pagelen=30
		part=math.floor( len(self.feature_code)/pagelen)
		for p in range(part):
			quote_list=','.join(self.feature_code[p*pagelen:p*pagelen+pagelen])	 
			#print(quote_list)
			self.log.critical("[3]RequestStocks", self.skQ.SKQuoteLib_RequestStocks(p,quote_list))
		#剩下不足一頁的獨立做一次
		if len(self.feature_code)>part*pagelen:
			quote_list=','.join(self.feature_code[part*pagelen:])
			#print(quote_list)	
			self.log.critical("[3]RequestStocks", self.skQ.SKQuoteLib_RequestStocks(part,quote_list))
		
	def step3(self): #收取掛單資訊
		import ctypes
		p=0
		for fc in self.feature_code:
			self.log.critical("[4]RequestTick,", self.skQ.SKQuoteLib_RequestTicks(p, fc))
			self.log.critical("[5]RequestFutureTradeInfo,", self.skQ.SKQuoteLib_RequestFutureTradeInfo(ctypes.c_short(p),fc))
			p+=1

	def filelog(self,file,data):
		print(data,file=self.tick_data,sep=",")


	def get_tick(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
		'''
		sMarketNo	報價有異動的商品市場別。
		sIndex	系統自行定義的股票代碼。
		nPtr	表示資料的位址(Key)
		nDate	交易日期。(YYYYMMDD)
		nTimehms	時間1。(時：分：秒’毫秒"微秒)
		nTimemillismicros	時間2。(’毫秒"微秒)
		nBid	買價。
		nAsk	賣價。
		nClose	成交價。
		nQty	成交量。
		nSimulate	0:一般揭示 1:試算揭示
		'''
		#self.log.info(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		self.filelog(self.tick_data,[self.get_time(),self.timestr,sMarketNo, sStockIdx, nPtr, lTimehms, nClose, nQty])

	def get_market(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
		'''
		bstrStockNo	(1)商品代號
		sMarketNo	市場別代號(不需要存)
		sStockidx	系統編碼後的特殊商品索引代號。(不需要存)
		nBuyTotalCount	(4)總委託買進筆數
		nSellTotalCount	(5)總委託賣出筆數
		nBuyTotalQty		(2)總委託買進口數
		nSellTotalQty	(3)總委託賣出口數
		nBuyDealTotalCount	(6)總成交買進筆數
		nSellDealTotalCount	(7)總成交賣出筆數
		'''
		in_time=self.get_time()
		in_date=time.strftime("%y/%m/%d",time.localtime())
		api_time=self.timestr
		api_timestamp=self.timestamp
		redis_key="{},{},{}".format(bstrStockNo,api_time,time.strftime("%y%m%d",time.localtime()) )
		#寫入system log
		#self.log.info(sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo)
		#寫入log檔
		self.filelog(self.market_data,[in_time,bstrStockNo,api_time,api_timestamp,nBuyTotalQty,nSellTotalQty,nBuyTotalCount,nSellTotalCount,nBuyDealTotalCount,nSellDealTotalCount])
		cache.hmset(redis_key,{'Market':bstrStockNo,'Date':in_date,'Time':api_time,'InTime':in_time,'TimsStamp':api_timestamp,'nBuyTotalQty':nBuyTotalQty,'nSellTotalQty':nSellTotalQty,'nBuyTotalCount':nBuyTotalCount,'nSellTotalCount':nSellTotalCount,'nBuyDealTotalCount':nBuyDealTotalCount,'nSellDealTotalCount':nSellDealTotalCount})

	def get_price(self,bstrStockNo,bstrStockName,nOpen,nHigh,nLow,nClose,nTQty):
		'''
		bstrStockNo 	代碼
		bstrStockName 	名稱
		nOpen 	開盤價
		nHigh 	最高價
		nLow 	 	最低價
		nClose 	成交價
		nTQty 	總量
		'''
		if (nOpen!=0 and nHigh!=0 and nLow!=0 and nClose!=0):
			self.feature_dict[bstrStockName]=(bstrStockName,nOpen,nHigh,nLow,nClose,nTQty)
			self.filelog(self.price_data,[bstrStockName,nOpen,nHigh,nLow,nClose,nTQty])


	def get_time(self):
		return datetime.now().strftime('%H:%M:%S.%f')[:-3]

	def check_alive(self,period=10000):
		self.watchdog+=1
		return self.watchdog<period
	
		
	
	def run(self):
		import winsound
		winsound.MessageBeep()
		if self.skQ.SKQuoteLib_IsConnected()==0: self.step1()
		self.delay(5)
			
		#self.log.info("RequestTick,", self.MSG(self.skQ.SKQuoteLib_RequestTicks(0, 'TX00')[1]))		
		#log.info("RequestServerTime",self.MSG(self.skQ.SKQuoteLib_RequestServerTime()))
		self.step2()
		#self.delay(5)
		#self.step3()
		self.delay(5)
		print(len(self.feature_dict))


if __name__ == '__main__':
	log = lu.Logger(level='crit')
	tick_data = open('data/'+datetime.now().strftime('%y%m%d_%H%M')+ '_feature_tick.txt','a') 
	price_data = open('data/'+datetime.now().strftime('%y%m%d_%H%M')+ '_feature_price.txt','a')
	market_data = open('data/'+datetime.now().strftime('%y%m%d_%H%M')+ '_feature.txt','a') 

	#輸入身分證與密碼
	Id=getpass.getpass(prompt='ID= ')
	Pw=getpass.getpass(prompt='PW= ')
	
	while True:
		t1=CAP_Thread(Id,Pw,log,price_data,tick_data,market_data) 
		t1.start()
		while t1.check_alive():
			time.sleep(0.0001)
			pythoncom.PumpWaitingMessages()
		time.sleep(1)
		t1.join()
