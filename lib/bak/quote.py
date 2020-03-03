# -*- coding: utf-8 -*-
#REF: https://easontseng.blogspot.com/2017/

import pythoncom, time, os,threading
import comtypes.client as cc
from datetime import datetime
import matplotlib.pyplot as plt
from logging import handlers

class CAP_Quoter(threading.Thread):
	#建立事件類別
	class skQ_events:
		def __init__(self, parent):
			self.MSG=parent.MSG
			self.parent=parent
		def OnConnection(self, nKind, nCode):
			self.parent.log.critical('[e]OnConnection:', self.MSG(nKind),nKind, self.MSG(nCode))	
			if nKind==3003: self.parent.step2()
				
		def OnNotifyServerTime(self,sHour,sMinute,sSecond,nTotal):
			self.parent.watchdog=0 #log.info(sHour,":",sMinute,":",sSecond,"--",nTotal)
		def OnNotifyQuote(self, sMarketNo, sStockidx):
			self.parent.log.info(sMarketNo,sStockidx)
		def OnNotifyHistoryTicks(self, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			self.parent.log.info(sMarketNo, sStockIdx, nPtr, lTimehms, nClose, nQty)
		def OnNotifyTicks(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			self.parent.log.info(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		def OnNotifyKLineData(self,bstrStockNo,bstrData):
			self.parent.log.info(bstrStockNo,bstrData)
		def OnNotifyFutureTradeInfo(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
			self.parent.log.info(sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo)
		def OnNotifyStockList(self,sMarketNo,bstrStockData):
			if self.parent.FilterStockList(sMarketNo,bstrStockData):	self.parent.step3()
		
	def __init__(self,tid,tpw,log):
		threading.Thread.__init__(self)
		cc.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
		from comtypes.gen import SKCOMLib as sk
		self.skC=cc.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
		self.skQ=cc.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
		self.EventQ=self.skQ_events(self)
		self.ConnectionQ = cc.GetEvents(self.skQ, self.EventQ)
		self.feature_list=[]
		self.option_list=[]
		self.feature_code=""
		self.option_code=""
		self.watchdog=0
		self.id=tid
		self.pw=tpw
		self.log=log
		
	def join(self):
		self.log.critical("[9]LeaveMonitor:", self.MSG(self.skQ.SKQuoteLib_LeaveMonitor()))	
		threading.Thread.join(self)

			
	def MSG(self,code):
		return self.skC.SKCenterLib_GetReturnCodeMessage(code)
	
	def step1(self):
		self.log.critical("[1]Login:", self.MSG(self.skC.SKCenterLib_Login(self.id,self.pw)))
		self.log.critical("[2]EnterMonitor:", self.MSG(self.skQ.SKQuoteLib_EnterMonitor()))	
		
	def step2(self):
		self.log.critical("[3]RequestFutureList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(2)))
		self.log.critical("[4]RequestOptionList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(3)))
		
	def step3(self):
		import ctypes
		self.log.critical(self.option_code)
		self.log.critical(self.feature_code)
#		for fc in self.feature_code.split(","):
#			r=self.skQ.SKQuoteLib_RequestTicks(-1, fc)
#			self.log.critical("[5]RequestLiveTick:",fc, self.MSG(r[1]),r[0])
#			self.log.critical("[6]RequestFutureTradeInfo:",fc, self.MSG(self.skQ.SKQuoteLib_RequestFutureTradeInfo(ctypes.c_short(r[0]), fc)))
			
	def FilterStockList(self,sMarketNo,bstrStockData):
		tmp_dict=bstrStockData.split(';')
		market_dict=[]
		market_code=[]
		for m in tmp_dict:
			if ('TX' in m) and not('/' in m): 
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)
		if len(market_dict)<10: return False #避免出現 ['TXO06', 'TXO07', 'TXO08', 'TXO09', 'TXO12', 'TX106']
		if sMarketNo==2: 
			self.feature_list=market_dict
			self.feature_code=",".join(market_code)
		if sMarketNo==3: 
			self.option_list=market_dict
			self.option_code=",".join(market_code)

		return len(self.feature_list)>0 and len(self.option_list)>0
	
	def check_alive(self,period=10000):
		self.watchdog+=1
		return self.watchdog<period
	
	def run(self):
		import winsound
		winsound.MessageBeep()
		if self.skQ.SKQuoteLib_IsConnected()==0: self.step1()
		#log.info("RequestTick,", self.MSG(self.skQ.SKQuoteLib_RequestTicks(0, 'TX00')[1]))		
		#log.info("RequestServerTime",self.MSG(self.skQ.SKQuoteLib_RequestServerTime()))
		
		
class CAP_Quoter():
	def __init__(self,tid,tpw,log):
		try:
			while 1:
				t1=None
				t1=CAP_Thread(tid,tpw,log) 
				t1.start()
				while t1.check_alive():
					time.sleep(0.001)
					pythoncom.PumpWaitingMessages()
				t1.join()
		except KeyboardInterrupt:
			pass
		t1.join()
		log.close()
	