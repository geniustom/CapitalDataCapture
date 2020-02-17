#REF: https://easontseng.blogspot.com/2017/
# -*- coding: utf-8 -*-
import lib.util as lu
import _getpass as getpass
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
			self.parent.log.critical('[v]OnConnection:', self.MSG(nKind),nKind, self.MSG(nCode))	
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
		cc.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\lib\SKCOM.dll')
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
		self.status=[False,False,False,False]
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
		self.log.critical("[3]RequestStock0List:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(0)))
		self.log.critical("[4]RequestStock1List:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(1)))
		self.log.critical("[5]RequestFutureList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(2)))
		self.log.critical("[6]RequestOptionList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(3)))


	def FilterStockList(self,sMarketNo,bstrStockData):
		import json
		tmp_dict=bstrStockData.split(';')
		market_dict=[]
		market_code=[]
		for m in tmp_dict:
			if not('購' in m) and not('售' in m) and (',' in m): 
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)

		if len(market_dict)>0:
			self.stock_list+=market_dict
			self.stock_code+=market_code
			with open('market_info/stock_list.json', 'w', encoding='utf-8') as j: j.write(json.dumps(self.stock_list,ensure_ascii=False))
			with open('market_info/stock_code.json', 'w', encoding='utf-8') as j: j.write(json.dumps(self.stock_code,ensure_ascii=False))
			print('[v]Get stock market done',len(market_dict),len(self.stock_list))
			self.status[sMarketNo]=True

	
	def FilterFeatureList(self,bstrStockData):
		import json
		today = date.today()
		M0=str(today.month)
		M1=str((today.month+1)%12)
		tmp_dict=bstrStockData.split(';')
		market_dict=[]
		market_code=[]
		if len(tmp_dict)>500 or len(tmp_dict)<70: return 	 #忽略股票與外幣期貨
		for m in tmp_dict:
			if (M0 in m or M1 in m) and (',' in m) and not('/' in m) and not('AM' in m): 
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)

		if len(market_dict)>0:
			self.feature_list+=market_dict
			self.feature_code+=market_code
			with open('market_info/feature_list.json', 'w', encoding='utf-8') as j: j.write(json.dumps(self.feature_list,ensure_ascii=False))
			with open('market_info/feature_code.json', 'w', encoding='utf-8') as j: j.write(json.dumps(self.feature_code,ensure_ascii=False))
			print('[v]Get future market done',len(market_dict),len(self.feature_list))
			self.status[2]=True
	
				
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
		#print(CM0,CM1,CM2,PM0,PM1,PM2,Y0,Y1,Y2)
		for m in tmp_dict:
			if ('TX' in m) and (',' in m) and (not('/' in m)) and (not('AM' in m)) and ((CM0+Y0 in m) or (CM1+Y1 in m) or (CM2+Y2 in m) or (PM0+Y0 in m) or (PM1+Y1 in m) or (PM2+Y2 in m)): 
				c=m.split(',')[0]
				market_dict.append(m)
				market_code.append(c)
		
		if len(market_dict)>0:
			self.option_list+=market_dict
			self.option_code+=market_code
			with open('market_info/option_list.json', 'w', encoding='utf-8') as j: j.write(json.dumps(self.option_list,ensure_ascii=False))
			with open('market_info/option_code.json', 'w', encoding='utf-8') as j: j.write(json.dumps(self.option_code,ensure_ascii=False))
			print('[v]Get option market done',len(market_dict),len(self.option_list))
			self.status[3]=True
		
	
	def check_alive(self,period=10000):
		self.watchdog+=1
		return self.watchdog<period
	
	def check_all_ready(self):
		#print(self.status)
		return self.status[0] and self.status[1] and self.status[2] and self.status[3]
		
	
	def run(self):
		import winsound
		winsound.MessageBeep()
		if self.skQ.SKQuoteLib_IsConnected()==0: self.step1()
		#self.log.info("RequestTick,", self.MSG(self.skQ.SKQuoteLib_RequestTicks(0, 'TX00')[1]))		
		#log.info("RequestServerTime",self.MSG(self.skQ.SKQuoteLib_RequestServerTime()))



if __name__ == '__main__':
	log = lu.Logger(level='crit')
	#輸入身分證與密碼
	Id=getpass.getpass(prompt='ID= ')
	Pw=getpass.getpass(prompt='PW= ')
	
	t1=CAP_Thread(Id,Pw,log) 
	t1.start()
	while t1.check_alive():
		time.sleep(0.0001)
		pythoncom.PumpWaitingMessages()
		if t1.check_all_ready()==True:break
	time.sleep(1)
	t1.join()
	t1=None