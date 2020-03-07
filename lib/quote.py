#REF: https://easontseng.blogspot.com/2017/
# -*- coding: utf-8 -*-

import time, os,threading ,datetime , math
import comtypes.client as cc
cc.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
import comtypes.gen.SKCOMLib as sk


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
			self.parent.watchdog=0
			pass
		def OnNotifyStockList(self,sMarketNo,bstrStockData):
			self.parent.watchdog=0
			pass

		def OnNotifyTicks(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			self.parent.watchdog=0
			self.parent.get_tick(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		def OnNotifyHistoryTicks(self, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			self.parent.watchdog=0
			self.parent.get_tick(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		def OnNotifyFutureTradeInfo(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
			self.parent.watchdog=0
			self.parent.get_market(bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount)
		def OnNotifyBest5(self,sMarketNo,sStockIdx,nBestBid1,nBestBidQty1,nBestBid2,nBestBidQty2,nBestBid3,nBestBidQty3,nBestBid4,nBestBidQty4,nBestBid5,nBestBidQty5,nExtendBid,nExtendBidQty,nBestAsk1,nBestAskQty1,nBestAsk2,nBestAskQty2,nBestAsk3,nBestAskQty3,nBestAsk4,nBestAskQty4,nBestAsk5,nBestAskQty5,nExtendAsk,nExtendAskQty,nSimulate):
			self.parent.watchdog=0
			self.parent.get_best5(sMarketNo,sStockIdx,nBestBid1,nBestBidQty1,nBestBid2,nBestBidQty2,nBestBid3,nBestBidQty3,nBestBid4,nBestBidQty4,nBestBid5,nBestBidQty5,nExtendBid,nExtendBidQty,nBestAsk1,nBestAskQty1,nBestAsk2,nBestAskQty2,nBestAsk3,nBestAskQty3,nBestAsk4,nBestAskQty4,nBestAsk5,nBestAskQty5,nExtendAsk,nExtendAskQty,nSimulate)
		def OnNotifyQuote(self,sMarketNo,sStockidx):
			self.parent.watchdog=0
			pStock = sk.SKSTOCK()
			self.parent.skQ.SKQuoteLib_GetStockByIndex(sMarketNo, sStockidx, pStock)
			self.parent.get_price(self,pStock.bstrStockNo,pStock.nOpen/math.pow(10,pStock.sDecimal),pStock.nHigh/math.pow(10,pStock.sDecimal),pStock.nLow/math.pow(10,pStock.sDecimal),pStock.nClose/math.pow(10,pStock.sDecimal),pStock.nTQty)

		
	def __init__(self,tid,tpw,log,stock_code,price_data,tick_data,market_data,thread_id=0,redis_host='localhost',from_idx=0,to_idx=0):
		threading.Thread.__init__(self)
		import json
		import redis   #使用python来操作redis用法详解  https://www.jianshu.com/p/2639549bedc8 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库
		#cache = redis.Redis(host='localhost', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
		pool = redis.ConnectionPool(host=redis_host, port=6379, decode_responses=True,max_connections=50)
		self.cache = redis.Redis(connection_pool=pool)
		
		self.tid=thread_id
		self.stock_list=[]
		self.stock_code = json.load(stock_code)
		if (from_idx!=0) or (to_idx!=0):
			self.stock_code=self.stock_code[from_idx:min(len(self.stock_code),to_idx)]
		self.stock_dict={}
		self.best5_dict={}
		self.best5_id_dict={}
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
		self.skC=cc.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
		self.skQ=cc.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
		self.EventQ=self.skQ_events(self)
		self.ConnectionQ = cc.GetEvents(self.skQ, self.EventQ)


	def join(self):
		self.log.critical("[9]LeaveMonitor:", self.MSG(self.skQ.SKQuoteLib_LeaveMonitor()))	
		threading.Thread.join(self)

			
	def MSG(self,code):
		return self.skC.SKCenterLib_GetReturnCodeMessage(code)
	
	def delay(self,sec):
		for i in range(sec):
			self.watchdog=0
			time.sleep(1)
			pass
	
	def step1(self): #登入
		self.log.critical("[1]Login:", self.MSG(self.skC.SKCenterLib_Login(self.id,self.pw)),"tid:",self.tid)
		self.log.critical("[2]EnterMonitor:", self.MSG(self.skQ.SKQuoteLib_EnterMonitor()),"tid:",self.tid)
		

	def step2(self): #收取量價資訊
		pagelen=50
		part=math.floor( len(self.stock_code)/pagelen)
		for p in range(part):
			quote_list=','.join(self.stock_code[p*pagelen:p*pagelen+pagelen])	 
			#print(quote_list)
			self.log.critical("[3]RequestStocks", self.skQ.SKQuoteLib_RequestStocks(p,quote_list),"tid:",self.tid)
		#剩下不足一頁的獨立做一次
		if len(self.stock_code)>part*pagelen:
			quote_list=','.join(self.stock_code[part*pagelen:])
			#print(quote_list)	
			self.log.critical("[3]RequestStocks", self.skQ.SKQuoteLib_RequestStocks(part,quote_list),"tid:",self.tid)
		
	def step3(self): #收取掛單資訊
		import ctypes
		p=0
		print('----------- 商品列表 -----------')
		print(','.join(self.stock_code))
		for fc in self.stock_code:
			self.log.info("[4]RequestTick,", self.skQ.SKQuoteLib_RequestTicks(p, fc),"tid:",self.tid)
			self.log.info("[5]RequestTradeInfo,", self.skQ.SKQuoteLib_RequestFutureTradeInfo(ctypes.c_short(p),fc),"tid:",self.tid)
			p+=1

	def filelog(self,file,data,log_on=False):
		if log_on==True :	print(data,file=file,sep=",")


	def get_tick(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
		'''
		sMarketNo	報價有異動的商品市場別。
		sStockIdx	系統自行定義的股票代碼。
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
		if sStockIdx in self.best5_dict:
			bstrStockNo=self.best5_dict[sStockIdx]
			#self.log.info(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
			self.filelog(self.tick_data,[self.get_time(),self.timestr,bstrStockNo, nPtr, lTimehms, nClose, nQty])

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
		self.best5_id_dict[sStockidx]=bstrStockNo
		in_time=self.get_time()
		in_date=time.strftime("%y/%m/%d",time.localtime())
		api_time=self.timestr
		api_timestamp=self.timestamp
		redis_key="{},{},{}".format(bstrStockNo,api_time,time.strftime("%y%m%d",time.localtime()) )
		#寫入system log
		#self.log.info(sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo)
		#寫入log檔
		if (bstrStockNo in self.stock_dict) and (bstrStockNo in self.best5_dict):
			############ set trade info ############
			self.cache.hmset(redis_key,{'Market':bstrStockNo,'Date':in_date,'Time':api_time,'InTime':in_time,'TimsStamp':api_timestamp,
								  'nBuyTotalQty':nBuyTotalQty,'nSellTotalQty':nSellTotalQty,'nBuyTotalCount':nBuyTotalCount,'nSellTotalCount':nSellTotalCount,
								  'nBuyDealTotalCount':nBuyDealTotalCount,'nSellDealTotalCount':nSellDealTotalCount,
								  })
			############ check time info ############
			pt,bt=self.cache.hmget(redis_key,'PriceTime','Best5Time')
			############ set market info ############
			data=self.stock_dict[bstrStockNo]
			if pt==None: pt='00:00:00'
			#print(time.strftime(data[1]) , time.strftime(t))
			if time.strftime(data[1]) > time.strftime(pt):
				self.cache.hmset(redis_key,{'PriceTime':data[1],'nOpen':data[2],'nHigh':data[3],'nLow':data[4],'nClose':data[5],'nTQty':data[6] })
			
			############ set best5 info ############
			data=self.best5_dict[bstrStockNo]
			if bt==None: bt='00:00:00'
			#print(time.strftime(data[0]) , time.strftime(t))
			if time.strftime(data[0]) > time.strftime(bt):
				self.cache.hmset(redis_key,{'Best5Time':data[0],
								   'nBestBid1':data[1],'nBestBidQty1':data[2],'nBestBid2':data[3],'nBestBidQty2':data[4],'nBestBid3':data[5],'nBestBidQty3':data[6],'nBestBid4':data[7],'nBestBidQty4':data[8],'nBestBid5':data[9],'nBestBidQty5':data[10],'nExtendBid':data[11],'nExtendBidQty':data[12],
								   'nBestAsk1':data[13],'nBestAskQty1':data[14],'nBestAsk2':data[15],'nBestAskQty2':data[16],'nBestAsk3':data[17],'nBestAskQty3':data[18],'nBestAsk4':data[19],'nBestAskQty4':data[20],'nBestAsk5':data[21],'nBestAskQty5':data[22],'nExtendAsk':data[23],'nExtendAskQty':data[24],'nSimulate':data[25]
								   })
			self.filelog(self.market_data,[in_time,bstrStockNo,api_time,api_timestamp,nBuyTotalQty,nSellTotalQty,nBuyTotalCount,nSellTotalCount,nBuyDealTotalCount,nSellDealTotalCount])


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
			self.stock_dict[bstrStockName]=(bstrStockName,self.timestr,nOpen,nHigh,nLow,nClose,nTQty)
			self.filelog(self.price_data,[bstrStockName,self.timestr,nOpen,nHigh,nLow,nClose,nTQty])
			#print(self.stock_dict[bstrStockName])

	def get_best5(self,sMarketNo,sStockIdx,nBestBid1,nBestBidQty1,nBestBid2,nBestBidQty2,nBestBid3,nBestBidQty3,nBestBid4,nBestBidQty4,nBestBid5,nBestBidQty5,nExtendBid,nExtendBidQty,nBestAsk1,nBestAskQty1,nBestAsk2,nBestAskQty2,nBestAsk3,nBestAskQty3,nBestAsk4,nBestAskQty4,nBestAsk5,nBestAskQty5,nExtendAsk,nExtendAskQty,nSimulate):
		'''
		sMarketNo,	市埸代碼
		sStockidx,	系統編碼後的特殊商品代號
		nBestBid1,nBestBidQty1,  買價1, 買量1
		nBestBid2,nBestBidQty2,  買價2, 買量2
		nBestBid3,nBestBidQty3,  買價3, 買量3
		nBestBid4,nBestBidQty4,  買價4, 買量4
		nBestBid5,nBestBidQty5,  買價5, 買量5
		nExtendBid,nExtendBidQty,延伸買價,延伸買量		
		nBestAsk1,nBestAskQty1,  買價1, 買量1
		nBestAsk2,nBestAskQty2,  買價2, 買量2
		nBestAsk3,nBestAskQty3,  買價3, 買量3
		nBestAsk4,nBestAskQty4,  買價4, 買量4
		nBestAsk5,nBestAskQty5,  買價5, 買量5
		nExtendAsk,nExtendAskQty,延伸賣價,延伸賣量		
		nSimulate 0:一般揭示 1:試算揭示
		'''
		if sStockIdx in self.best5_id_dict:
			pStock = sk.SKSTOCK()
			self.skQ.SKQuoteLib_GetStockByIndex(sMarketNo, sStockIdx, pStock)
			df=math.pow(10,pStock.sDecimal)
			bstrStockName=self.best5_id_dict[sStockIdx]
			self.best5_dict[bstrStockName]=(self.timestr,
					nBestBid1/df,nBestBidQty1,nBestBid2/df,nBestBidQty2,nBestBid3/df,nBestBidQty3,nBestBid4/df,nBestBidQty4,nBestBid5/df,nBestBidQty5,nExtendBid/df,nExtendBidQty,
					nBestAsk1/df,nBestAskQty1,nBestAsk2/df,nBestAskQty2,nBestAsk3/df,nBestAskQty3,nBestAsk4/df,nBestAskQty4,nBestAsk5/df,nBestAskQty5,nExtendAsk/df,nExtendAskQty,nSimulate)


	def get_time(self):
		return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

	def is_alive(self,deadline=10000):
		self.watchdog+=1
		return self.watchdog<deadline
	
	def run(self):
		import winsound
		winsound.MessageBeep()
		if self.skQ.SKQuoteLib_IsConnected()==0: 
			self.step1()
			self.step2()
			self.delay(5)
			print('共計有',len(self.stock_code),'個商品')
			print('共計有',len(self.stock_dict),'個商品有交易紀錄')
			self.step3()
		