#REF: https://easontseng.blogspot.com/2017/

import pythoncom, time, os,threading
import comtypes.client as cc
from datetime import datetime
import matplotlib.pyplot as plt
import _getpass as getpass
import logging
from logging import handlers

#輸入身分證與密碼
Id=getpass.getpass(prompt='ID= ')
Pw=getpass.getpass(prompt='Password= ')


class Logger(object):
	level_relations = {
		'debug':logging.DEBUG,
		'info':logging.INFO,
		'warning':logging.WARNING,
		'error':logging.ERROR,
		'crit':logging.CRITICAL
	}#日誌級別關係對映

	def __init__(self,filename='log/'+str(datetime.now().date())+'.log' ,level='info',when='D',backCount=30,fmt='[%(asctime)s][%(levelname)s]: %(message)s'):
		#fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
		self.logger = logging.getLogger(filename)
		format_str = logging.Formatter(fmt) 	#設定日誌格式
		self.logger.setLevel(self.level_relations.get(level)) 	#設定日誌級別
		sh = logging.StreamHandler() 	#往螢幕上輸出
		sh.setFormatter(format_str) 	#設定螢幕上顯示的格式
		th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往檔案裡寫入#指定間隔時間自動生成檔案的處理器
		#例項化TimedRotatingFileHandler
		#interval是時間間隔，backupCount是備份檔案的個數，如果超過這個個數，就會自動刪除，when是間隔的時間單位，單位有以下幾種：
		# S 秒 M 分 H 小時、 D 天、  W 每星期（interval==0時代表星期一）  midnight 每天凌晨
		th.setFormatter(format_str)#設定檔案裡寫入的格式
		self.logger.addHandler(sh) #把物件加到logger裡
		self.logger.addHandler(th) 
		

	def info(self,*msg): 		self.logger.info(' '.join(str(d) for d in msg))
	def debug(self,*msg): 		self.logger.debug(' '.join(str(d) for d in msg))
	def warning(self,*msg): 	self.logger.warning(' '.join(str(d) for d in msg))
	def error(self,*msg): 		self.logger.error(' '.join(str(d) for d in msg))
	def critical(self,*msg): 	self.logger.critical(' '.join(str(d) for d in msg))
	def fatal(self,*msg): 		self.logger.fatal(' '.join(str(d) for d in msg))
	def close(self): 			self.logger=None

class CAP_Thread(threading.Thread):
	#建立事件類別
	class skQ_events:
		def __init__(self, parent):
			self.MSG=parent.MSG
			self.parent=parent
		def OnConnection(self, nKind, nCode):
			log.critical('[e]OnConnection:', self.MSG(nKind),nKind, self.MSG(nCode))	
			if nKind==3003: self.parent.step2()
				
		def OnNotifyServerTime(self,sHour,sMinute,sSecond,nTotal):
			self.parent.watchdog=0 #log.info(sHour,":",sMinute,":",sSecond,"--",nTotal)
		def OnNotifyQuote(self, sMarketNo, sStockidx):
			log.info(sMarketNo,sStockidx)
		def OnNotifyHistoryTicks(self, sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			log.info(sMarketNo, sStockIdx, nPtr, lTimehms, nClose, nQty)
		def OnNotifyTicks(self,sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
			log.info(sMarketNo, sStockIdx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate)
		def OnNotifyKLineData(self,bstrStockNo,bstrData):
			log.info(bstrStockNo,bstrData)
		def OnNotifyFutureTradeInfo(self,bstrStockNo,sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty	,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount):
			log.info(sMarketNo,sStockidx,nBuyTotalCount,nSellTotalCount,nBuyTotalQty,nSellTotalQty,nBuyDealTotalCount,nSellDealTotalCount,bstrStockNo)
		def OnNotifyStockList(self,sMarketNo,bstrStockData):
			if self.parent.FilterStockList(sMarketNo,bstrStockData):	self.parent.step3()
		
	def __init__(self):
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
		
	def join(self):
		log.critical("[9]LeaveMonitor:", self.MSG(self.skQ.SKQuoteLib_LeaveMonitor()))	
		threading.Thread.join(self)

			
	def MSG(self,code):
		return self.skC.SKCenterLib_GetReturnCodeMessage(code)
	
	def step1(self):
		log.critical("[1]Login:", self.MSG(self.skC.SKCenterLib_Login(Id,Pw)))
		log.critical("[2]EnterMonitor:", self.MSG(self.skQ.SKQuoteLib_EnterMonitor()))	
		
	def step2(self):
		log.critical("[3]RequestFutureList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(2)))
		log.critical("[4]RequestOptionList:", self.MSG(self.skQ.SKQuoteLib_RequestStockList(3)))
		
	def step3(self):
		import ctypes
		#log.info(self.option_code)
		#log.info(self.feature_code)
		for fc in self.feature_code.split(","):
			r=self.skQ.SKQuoteLib_RequestTicks(-1, fc)
			log.debug("[5]RequestLiveTick:",fc, self.MSG(r[1]),r[0])
			#log.debug("[6]RequestFutureTradeInfo:",fc, self.MSG(self.skQ.SKQuoteLib_RequestFutureTradeInfo(ctypes.c_short(r[0]), fc)))
			
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




if __name__ == '__main__':
	log = Logger(level='crit')
	try:
		while 1:
			t1=None
			t1=CAP_Thread() 
			t1.start()
			while t1.check_alive():
				time.sleep(0.001)
				pythoncom.PumpWaitingMessages()
			t1.join()
	except KeyboardInterrupt:
		pass
	t1.join()
	log.close()

	