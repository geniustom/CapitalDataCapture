# -*- coding: utf-8 -*-
import numpy as np
import time


END_K_INDEX = 295
STOP_LOSE = 40 #20點停損
#TRADE_LOSE = 5 #交易成本
DataCache={}
DataL2Cache={}

class timer:
	def __init__(self): 
		self.t=time.clock()
	def spendtime(self,msg=""):
		if msg=="":
			return str(time.clock()-self.t)
		else:
			return msg + " : " +str(time.clock()-self.t) + " secs"
			
class DBConn:
	def __init__(self,host,uid,pwd,cata):
		import win32com.client
		tt=timer()
		self.conn=win32com.client.Dispatch(r"ADODB.Connection")
		self.connstr= "Provider=SQLNCLI.1;Persist Security Info=True;Data Source="+host+";Initial Catalog="+cata+";User ID="+uid+";Password="+pwd+";"
		self.conn.Open(self.connstr)
		print (cata,tt.spendtime("DB Conn Time"))
		
class Query:
	def __init__(self,conn):
		import win32com.client
		self.cm = win32com.client.Dispatch(r"ADODB.Command")
		self.cm.CommandType = 1                     #adCmdText     #http://msdn2.microsoft.com/en-us/library/ms962122.aspx
		self.cm.ActiveConnection = conn
		self.cm.ActiveConnection.CursorLocation = 3 #static 可以使用 RecordCount 屬性
	def QueryDB(self,SQL_Str):
		self.cm.CommandText = SQL_Str
		self.cm.Parameters.Refresh()
		self.cm.Prepared = True
		(rs1, result) = self.cm.Execute() 
		return rs1, rs1.recordcount   
	def ExecDB(self,SQL_Str):
		self.cm.CommandText = SQL_Str
		self.cm.Parameters.Refresh()
		self.cm.Prepared = True
		return self.cm.Execute()


def seq_intg (x):
	y=np.zeros(x.shape,dtype=x.dtype)
	y[0]=x[0]
	for i in range(len(x)):  #從0開始
		if i>0: y[i]=x[i]+y[i-1]
	return y        
		
def seq_diff (x,x0=False):
	#return np.hstack((0,np.diff(x)))
	#return np.ediff1d(x, to_begin=0)
	y=np.zeros(x.shape,dtype=x.dtype)
	if x0:y[0]=x[0]
	for i in range(len(x)):  #從0開始
		if i>0: y[i]=x[i]-x[i-1]
	return y  



class TradeData:
	def __init__(self,conn,market):
		import imp,lib.indicator as indl;       imp.reload(indl);
		self.dbconn=conn
		self.dt=Query(conn)
		self.market=market
		#self.sqlfield="Future_CurPrice,TDATETIME,Future_Volume,Future_TotalBuyVol, Future_TotalSellVol,FutureWant_TrustBuyVol,FutureWant_TrustSellVol,Future_Volume,FutureWant_TrustBuyCnt,FutureWant_TrustSellCnt,FutureWant_TotalBuyCnt,FutureWant_TotalSellCnt,RealWant_Uppers,RealWant_Downs,RealWant_UpperLimits,RealWant_DownLimits,RealWant_Steadys,FutureM_Volume,FutureM_TotalBuyVol, FutureM_TotalSellVol,FutureWantM_TrustBuyVol,FutureWantM_TrustSellVol,FutureM_Volume,FutureWantM_TrustBuyCnt,FutureWantM_TrustSellCnt,FutureWantM_TotalBuyCnt,FutureWantM_TotalSellCnt,Future_TF_Volume,FutureWant_TF_TrustBuyVol,FutureWant_TF_TrustSellVol,Future_TF_Volume,FutureWant_TF_TrustBuyCnt,FutureWant_TF_TrustSellCnt,FutureWant_TF_TotalBuyCnt,FutureWant_TF_TotalSellCnt,Future_TE_Volume,FutureWant_TE_TrustBuyVol,FutureWant_TE_TrustSellVol,Future_TE_Volume,FutureWant_TE_TrustBuyCnt,FutureWant_TE_TrustSellCnt,FutureWant_TE_TotalBuyCnt,FutureWant_TE_TotalSellCnt"
		#self.sqlfield="*"
	   
		self.sqlfield ="id,Market,Date,Time,InTime,TimsStamp,nBuyTotalQty,nSellTotalQty,nBuyTotalCount,nSellTotalCount,nBuyDealTotalCount,nSellDealTotalCount,PriceTime,nOpen,nHigh,nLow,nClose,nTQty"        

		r, rcnt = self.dt.QueryDB("SELECT [DATE] FROM (SELECT DISTINCT [DATE] FROM RawData WHERE [DATE]>'20/03/13' AND [Market]='"+self.market+"' AND [PriceTime]=[Time]) as NEW ORDER BY [DATE]")
		rr=r.GetRows(rcnt)   
		#print rr
		self.DateList=[]            #撈db抓到的所有tdate
		self.DateListStart=[]       #對應該tdate的起始索引位置
		self.DateListEnd=[]         #對應該tdate的結束索引位置
		self.AllData=None
		for i in range(len(rr[0])):
			self.DateList.append(rr[0][i][:8])
		self.DateCount=rcnt
		
	def QueryDBtoIndicators(self,SQL_Str,indGroup=None):
		import imp,lib.indicator as indl;       imp.reload(indl);
		self.Qy=Query(self.dbconn)
		print(SQL_Str)
		r, rcnt= self.Qy.QueryDB(SQL_Str)
		print ("Data count : " + str(rcnt))  #just for debug
		rr=r.GetRows(rcnt)        
		if indGroup is None:
			indGroup=indl.indicatorGroup()
		indGroup.names = [field.Name for field in r.Fields]
		i=0
		for field_name in indGroup.names:
			ind=indl.indicator()
			ind.name=field_name
			ind.data=np.array(rr[i])
			i+=1
			indGroup.ids.append(ind)
		return  indGroup
	
	def FetchDateByDB(self,day):      # 即時跑策略時用
		self.DaySQL = "Select " + self.sqlfield + " from RawData where [DATE]='" + day + "' AND [Market]='"+self.market+"' AND [PriceTime]=[Time] ORDER BY [TimsStamp]"
		indi=self.QueryDBtoIndicators(self.DaySQL)
		indi.GetBaseIndicator()
		return indi 

	def FetchDateByMem(self,day):     # 離線回測時用
		import imp,lib.indicator as indl;       imp.reload(indl);
		#沒資料時自動load資料
		if self.AllData==None:
			tt=timer()
			self.FetchAllData()
			print (tt.spendtime("DB Get All Data"))
		
		DayIndex=self.DateList.index(day)
		RecStart=self.DateListStart[DayIndex]
		RecEnd=self.DateListEnd[DayIndex]
		RecLen=RecEnd-RecStart
		indi=indl.indicatorGroup()
		for i in range(len(self.AllData.ids)):
			ids=indl.indicator()
			ids.count=RecLen
			ids.name=self.AllData.ids[i].name
			ids.data=self.AllData.ids[i].data[RecStart:RecEnd] #np.array(
			indi.ids.append(ids)
		#print self.AllData.ids[1][RecStart:RecEnd]
		#print indi.get("DATE",list_type=1)
		return indi

	def FetchAllData(self):
		# 420604 筆以上會出問題
		self.AllDataSQL = "Select " + self.sqlfield + " from RawData WHERE [DATE]>'20/03/13' AND [Market]='"+self.market+"'  AND [PriceTime]=[Time] ORDER BY [DATE],[TimsStamp]"
		indi=self.QueryDBtoIndicators(self.AllDataSQL)
		indi.GetBaseIndicator()    
		SearchIndex=0
		indiDayList=indi.get("DATE",list_type=1)
		for i in range(len(self.DateList)):          
			for j in range(SearchIndex,indi.len):
				if self.DateList[i]==indiDayList[j]:
					self.DateListStart.append(SearchIndex)
					break
				SearchIndex+=1
				
		for i in range(len(self.DateList)): 
			try:
				self.DateListEnd.append(self.DateListStart[i+1]-1)      #
			except:
				self.DateListEnd.append(indi.len)                            #最後
			
		self.AllData=indi        
		
		#indilist =indl.indicatorGroup()
		#indilist[i]
		
		
		
	


'''
if __name__ == '__main__':
	from PIL import Image
	import matplotlib.pyplot as plt
	timg=TradeImg(TopN=30,mode='test')
	timg.prepare_data()

	date="17/09/06"
	plt.imshow(timg.ShowImg(date,300)); plt.show();
	plt.plot(timg.GetPrice(date))
	plt.plot(timg.GetSellStopLose(date))
	m=timg.GetData(date,300)
	print(m)
'''