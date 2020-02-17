#REF: https://easontseng.blogspot.com/2017/
# -*- coding: utf-8 -*-
import lib.util as lu
import _getpass as getpass
import pythoncom, time, os,threading
import comtypes.client as cc
from datetime import datetime,date
import matplotlib.pyplot as plt
from logging import handlers


class CAP_Thread(threading.Thread):
	#建立事件類別
	class skQ_events:
		def __init__(self, parent):
			self.MSG=parent.MSG
			self.parent=parent
		def OnConnection(self, nKind, nCode):
			self.parent.log.critical('[e]OnConnection:', self.MSG(nKind),nKind, self.MSG(nCode))	
			if nKind==3003: self.parent.step2()
		def OnNotifyQuote(self, sMarketNo, sStockidx):
			self.parent.log.info(sMarketNo,sStockidx)
		def OnNotifyServerTime(self,sHour,sMinute,sSecond,nTotal):
			self.parent.watchdog=0
			self.parent.timestr="{}:{}:{}".format(sHour,sMinute,sSecond)
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

		
	def __init__(self,tid,tpw,log,tick_data,market_data):
		threading.Thread.__init__(self)
		cc.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\lib\SKCOM.dll')
		self.feature_list=[]
		self.feature_code=[]
		self.watchdog=0
		self.timestr=''
		self.id=tid
		self.pw=tpw
		self.log=log
		self.tick_data=tick_data
		self.market_data=market_data
		self.sk_init()
		
	def sk_init(self):
		from comtypes.gen import SKCOMLib as sk
		self.skC=cc.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
		self.skQ=cc.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
		self.EventQ=self.skQ_events(self)
		self.ConnectionQ = cc.GetEvents(self.skQ, self.EventQ)

	def join(self):
		self.log.critical("[9]LeaveMonitor:", self.MSG(self.skQ.SKQuoteLib_LeaveMonitor()))	
		threading.Thread.join(self)

			
	def MSG(self,code):
		return self.skC.SKCenterLib_GetReturnCodeMessage(code)
	
	def step1(self):
		self.log.critical("[1]Login:", self.MSG(self.skC.SKCenterLib_Login(self.id,self.pw)))
		self.log.critical("[2]EnterMonitor:", self.MSG(self.skQ.SKQuoteLib_EnterMonitor()))
		
		
	def step2(self):
		import json,ctypes
		input_file = open ('market_info/feature_code.json')
		self.feature_code = json.load(input_file)
		input_file.close
		p=0
		for fc in self.feature_code:
			print(fc)
			self.log.critical("[3]RequestTick,", self.skQ.SKQuoteLib_RequestTicks(p, fc))
			self.log.critical("[4]RequestFutureTradeInfo,", self.skQ.SKQuoteLib_RequestFutureTradeInfo(ctypes.c_short(p),fc))
			p+=1

	def get_tick(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
		self.log.info(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		print(self.get_time(),self.timestr,sMarketNo, sStockIdx, nPtr, lTimehms, nClose, nQty,sep=",",file=self.tick_data)

	def get_market(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
		self.log.info(sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo)
		print(self.get_time(),self.timestr,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo,sep=",",file=self.market_data)

	def get_time(self):
		return datetime.now().strftime('%H:%M:%S.%f')[:-3]

	def check_alive(self,period=10000):
		self.watchdog+=1
		return self.watchdog<period
	
		
	
	def run(self):
		import winsound
		winsound.MessageBeep()
		if self.skQ.SKQuoteLib_IsConnected()==0: self.step1()
		#self.log.info("RequestTick,", self.MSG(self.skQ.SKQuoteLib_RequestTicks(0, 'TX00')[1]))		
		#log.info("RequestServerTime",self.MSG(self.skQ.SKQuoteLib_RequestServerTime()))
		self.step2()




if __name__ == '__main__':
	log = lu.Logger(level='crit')
	tick_data = open('data/'+datetime.now().strftime('%y%m%d_%H%M')+ '_tick.txt','a') 
	market_data = open('data/'+datetime.now().strftime('%y%m%d_%H%M')+ '_feature.txt','a') 

	#輸入身分證與密碼
	Id=getpass.getpass(prompt='ID= ')
	Pw=getpass.getpass(prompt='PW= ')
	
	while True:
		t1=CAP_Thread(Id,Pw,log,tick_data,market_data) 
		t1.start()
		while t1.check_alive():
			time.sleep(0.0001)
			pythoncom.PumpWaitingMessages()
		time.sleep(1)
		t1.join()
