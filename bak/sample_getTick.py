import pythoncom, time, os
import comtypes.client as cc
from datetime import datetime
import matplotlib.pyplot as plt
import getpass

#%matplotlib auto
#發現在jupyter notebook用了 %matplotlib auto後, 就不用 pythoncom.PumpWaitingMessages() 來顯示 event
#在我的例子裡, 如果有顯示 Using matplotlib backend: Qt4Agg, 就會自動 pump Event了
cc.GetModule(os.path.split(os.path.realpath(__file__))[0] + r'\SKCOM.dll')
#第一次用 GetModule 會在comtypes.gen 資料夾下產生 SKCOMLib.py, 及 XXXXX一長字串.py 的檔案
#comtypes 將dll轉換成python可用的module了，GetModule理論上執行過一次即可，
#若有更新群益 API， 要將gen裡的cache檔案都清除，再執行 GetModule
#可以借下列方法將SKCOMLib import, 即可使用了

from comtypes.gen import SKCOMLib as sk
#建立物件
skC=cc.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
skQ=cc.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)

#輸入身分證與密碼
Id=getpass.getpass(prompt='ID= ')
Pw=getpass.getpass(prompt='Password= ')


#建立事件類別
class skQ_events:
	def OnConnection(self, nKind, nCode):
		print('OnConnection nKind, nCode', nKind, nCode)
	def OnNotifyTicks(self, sMarketNo, sIndex, nPtr, nTimehms, nTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
		print(sMarketNo, sIndex, nPtr, nTimehms, nClose, nQty)
	def OnNotifyServerTime(self,sHour,sMinute,sSecond,nTotal):
		print(sHour,sMinute,sSecond,nTotal)

		   
		
#Event sink, 事件實體  
EventQ=skQ_events()
#make connection to event sink
ConnectionQ = cc.GetEvents(skQ, EventQ)        
#Login
print("Login,", skC.SKCenterLib_GetReturnCodeMessage(skC.SKCenterLib_Login(Id,Pw)))
print("EnterMonitor,", skC.SKCenterLib_GetReturnCodeMessage(skQ.SKQuoteLib_EnterMonitor()))
#登錄商品
strStocks='TX00'
print("RequestTick,", strStocks, skC.SKCenterLib_GetReturnCodeMessage(skQ.SKQuoteLib_RequestTicks(1, strStocks)[1]))
print("RequestServerTime",skC.SKCenterLib_GetReturnCodeMessage(skQ.SKQuoteLib_RequestServerTime()))
while 1:
	time.sleep(1)
	pythoncom.PumpWaitingMessages()