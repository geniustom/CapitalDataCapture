# -*- coding: utf-8 -*-
#REF: https://easontseng.blogspot.com/2017/

import pythoncom, time, os,threading
import comtypes.client as cc
from datetime import datetime,date
import matplotlib.pyplot as plt
from logging import handlers

# AM 14:30~05:00


class CAP_Thread(threading.Thread):
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
			print((sMarketNo, sStockIdx, nPtr, lTimehms, nClose, nQty))
		def OnNotifyKLineData(self,bstrStockNo,bstrData):
			self.parent.log.info(bstrStockNo,bstrData)
		def OnNotifyFutureTradeInfo(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
			self.parent.log.info(sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo)
		def OnNotifyStockList(self,sMarketNo,bstrStockData):
			if sMarketNo==0: self.parent.FilterStockList(sMarketNo,bstrStockData)
			elif sMarketNo==1: self.parent.FilterStockList(sMarketNo,bstrStockData)
			elif sMarketNo==2: self.parent.FilterFeatureList(bstrStockData)
			elif sMarketNo==3: self.parent.FilterOptionList(bstrStockData)
			#if ret==True: self.parent.step3()
		
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
		self.stock_list=[]
		self.feature_code=[]
		self.option_code=[]
		self.stock_code=[]
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
		self.log.critical("[3]RequestFutureList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(0)))
		self.log.critical("[4]RequestFutureList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(1)))
		self.log.critical("[5]RequestFutureList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(2)))
		self.log.critical("[6]RequestOptionList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(3)))
		
	def step3(self):
		import ctypes
#		self.log.info("RequestTick,", self.MSG(self.skQ.SKQuoteLib_RequestLiveTick(0, 'TX00')[1]))
#		self.log.critical(self.option_code)
#		self.log.critical(self.feature_code)
#		for fc in self.feature_code.split(","):
#			r=self.skQ.SKQuoteLib_RequestTicks(-1, fc)
#			self.log.critical("[5]RequestLiveTick:",fc, self.MSG(r[1]),r[0])
#			self.log.critical("[6]RequestFutureTradeInfo:",fc, self.MSG(self.skQ.SKQuoteLib_RequestFutureTradeInfo(ctypes.c_short(r[0]), fc)))
	
	def FilterStockList(self,sMarketNo,bstrStockData):
		import json
		tmp_dict=bstrStockData.split(';')
		market_dict=[]
		market_code=[]
		for m in tmp_dict:
			if not('購' in m) and not('售' in m) and (',' in m): 
				print(m)
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)
		self.stock_list=market_dict
		self.stock_code=",".join(market_code)

		with open('stock_list'+str(sMarketNo)+'.json', 'w') as j: j.write(json.dumps(self.stock_list))
		with open('stock_code'+str(sMarketNo)+'.json', 'w') as j: j.write(json.dumps(self.stock_code))
		return len(market_dict)>0	
	
	def FilterFeatureList(self,bstrStockData):
		import json
		tmp_dict=bstrStockData.split(';')
		market_dict=[]
		market_code=[]
		for m in tmp_dict:
			if ('TX' in m) and (',' in m) and not('/' in m) and not('AM' in m): 
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)
		self.feature_list=market_dict
		self.feature_code=",".join(market_code)

		with open('feature_list.json', 'w') as j: j.write(json.dumps(self.feature_list))
		with open('feature_code.json', 'w') as j: j.write(json.dumps(self.feature_code))
		return len(market_dict)>0
	
				
	def FilterOptionList(self,bstrStockData):	
		import json
		today = date.today()
		#   NA  1   2   3   4   5   6   7   8   9   10  11  12  1   2
		C=[' ','A','B','C','D','E','F','G','H','I','J','K','L','A','B']
		P=[' ','M','N','O','P','Q','R','S','T','U','V','W','X','M','N']
		Y0=str(today.year % 10)
		Y1=Y0 if today.month<12 else str(int(Y0)+1%10)
		Y2=Y0 if today.month<11 else str(int(Y0)+1%10)
		CM0,CM1,CM2=C[today.month],C[today.month+1],C[today.month+2]
		PM0,PM1,PM2=P[today.month],P[today.month+1],P[today.month+2]
		tmp_dict=bstrStockData.split(';')
		market_dict=[]
		market_code=[]
		print(CM0,CM1,CM2,PM0,PM1,PM2,Y0,Y1,Y2)
		for m in tmp_dict:
			if ('TX' in m) and (',' in m) and (not('/' in m)) and (not('AM' in m)) and ((CM0+Y0 in m) or (CM1+Y1 in m) or (CM2+Y2 in m) or (PM0+Y0 in m) or (PM1+Y1 in m) or (PM2+Y2 in m)): 
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)
		self.option_list=market_dict
		self.option_code=",".join(market_code)
		
		with open('option_list.json', 'w') as j: j.write(json.dumps(self.option_list))
		with open('option_code.json', 'w') as j: j.write(json.dumps(self.option_code))
		return len(market_dict)>0
		
	
	def check_alive(self,period=10000):
		self.watchdog+=1
		return self.watchdog<period
	
	def run(self):
		import winsound
		winsound.MessageBeep()
		if self.skQ.SKQuoteLib_IsConnected()==0: self.step1()
		#self.log.info("RequestTick,", self.MSG(self.skQ.SKQuoteLib_RequestTicks(0, 'TX00')[1]))		
		#log.info("RequestServerTime",self.MSG(self.skQ.SKQuoteLib_RequestServerTime()))



class CAP_Agent():
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
	