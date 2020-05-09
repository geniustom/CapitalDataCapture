# -*- coding: utf-8 -*-
import sys   
sys.path.append("..") 

import lib.dblib as dl
import lib.indicator as il
import lib.strategy_lib as sl
import lib.tracking as tl
import lib.analytics as an

import numpy as np
import pylab as pl
import scipy as sc
import matplotlib.pyplot as plt


Market='TX00'
DorN='N'
dbt = dl.DBConn(host="192.168.1.102",uid="sa",pwd="geniustom",cata="FutureData")
tdt=dl.TradeData(dbt.conn,Market,DorN)
dayindi=il.indicatorGroup()


#=========================================================================
#dayindi=tdt.FetchDateByDB("20/03/13")  #D:
#dayindi=tdt.FetchDateByDB("20/03/16")  #D:
#dayindi=tdt.FetchDateByDB("20/03/17")  #D:
#dayindi=tdt.FetchDateByDB("20/03/18")  #D:
#dayindi=tdt.FetchDateByDB("20/03/20")  #D:
#dayindi=tdt.FetchDateByDB("20/03/23")  #D:
#dayindi=tdt.FetchDateByDB("20/03/24")  #D:
#dayindi=tdt.FetchDateByDB("20/03/25")  #D:
#dayindi=tdt.FetchDateByDB("20/03/26")  #D:
#dayindi=tdt.FetchDateByDB("20/03/27")  #D:
#dayindi=tdt.FetchDateByDB("20/03/30")  #D:
#dayindi=tdt.FetchDateByDB("20/04/01")  #D:
#dayindi=tdt.FetchDateByDB("20/04/06")  #D:跌200,漲200 N:漲175
#dayindi=tdt.FetchDateByDB("20/04/07")  #D:漲60,跌100,漲100  N:漲100跌175
#dayindi=tdt.FetchDateByDB("20/04/08")  #D:一路上漲170點   N:殺80後再漲100
#dayindi=tdt.FetchDateByDB("20/04/09")  #D:漲100,跌150,再漲100  N:跌100,漲60,再跌100
#dayindi=tdt.FetchDateByDB("20/04/10")  # D:一路上漲100點   N:漲80點又跌回收上影線
dayindi=tdt.FetchDateByDB("20/04/23")  



il.GetSpecialIndicator(dayindi)
diff=dl.seq_intg(dl.seq_diff(dayindi.get(u"指數")))
bidiff=dl.seq_intg(dayindi.get(u"純賣成筆")-dayindi.get(u"純買成筆"))
vol=dayindi.get(u"純成交量")
#=========================================================================
plt.subplot(211)
plt.plot(diff,"b")
#plt.show()
plt.subplot(212)
#a=dayindi.get(u"成筆差")
#b=dayindi.get(u"純買成筆")*(dayindi.get(u"純成交量")/dayindi.get(u"純賣成筆"))-dayindi.get(u"純買成筆")*(dayindi.get(u"純成交量")/dayindi.get(u"純買成筆"))
#plt.plot(a-b,"b")
plt.plot(dayindi.get(u"純賣成筆")/diff-dayindi.get(u"純買成筆")/diff,"g")
#plt.plot(dayindi.get(u"純買成筆")/diff,"r")
plt.show()
#=========================================================================
plt.subplot(211)
plt.plot(diff,"b")
#plt.show()
plt.subplot(212)
#a=dayindi.get(u"成筆差")
#b=dayindi.get(u"純買成筆")*(dayindi.get(u"純成交量")/dayindi.get(u"純賣成筆"))-dayindi.get(u"純買成筆")*(dayindi.get(u"純成交量")/dayindi.get(u"純買成筆"))
#plt.plot(a-b,"b")
plt.plot((dayindi.get(u"純成交量")/dayindi.get(u"純買成筆"))[100:],"r")
plt.plot((dayindi.get(u"純成交量")/dayindi.get(u"純賣成筆"))[100:],"g")
plt.show()
#=========================================================================

#plt.plot(dayindi.get(u"成筆差"),"b")
#plt.show()

'''
ax=plt.subplot(211);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
plt.plot(dayindi.get(u"指數波動"),"b")
plt.show()
'''

#print ("通道")
#ax=plt.subplot(211);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
#plt.plot(dayindi.get(u"指數波動"),"b")
#ax=plt.subplot(212);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
#plt.plot(dayindi.get(u"小台純主力作為")-dayindi.get(u"小台純散戶作為"),"r")
#plt.plot(dayindi.get(u"小台未純化大單作為"),"b")
#plt.plot(dayindi.get(u"小台未純化大單作為高通道"),"r")
#plt.plot(dayindi.get(u"小台未純化大單作為低通道"),"g")
#plt.show()
#
#print ("小台贏家00")
#ax=plt.subplot(211);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
#plt.plot(dayindi.get(u"指數波動"),"b")
#ax=plt.subplot(212);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
#il.GetIndicatorByType(dayindi,"小台贏家00")
#plt.plot(dayindi.get(u"小台贏家00"),"b")
#plt.plot(dayindi.get(u"小台贏家00高通道"),"r")
#plt.plot(dayindi.get(u"小台贏家00低通道"),"g")
#plt.show()

#plt.plot(dayindi.get(u"大台主力"),"b")
#plt.plot(dayindi.get(u"大台主力高通道"),"r")
#plt.plot(dayindi.get(u"大台主力低通道"),"g")
#plt.show()


#print ("大 主力/散戶")
#ax=plt.subplot(211);ax.yaxis.tick_right();
#plt.plot(dayindi.get(u"大台指數"),"b")
#plt.plot(dayindi.get(u"大台主力買作為價"),"r")
#plt.plot(dayindi.get(u"大台主力賣作為價"),"g")
#ax=plt.subplot(212);ax.yaxis.tick_right();
#plt.plot(dayindi.get(u"大台指數"),"b")
#plt.plot(dayindi.get(u"大台散戶買作為價"),"g")
#plt.plot(dayindi.get(u"大台散戶賣作為價"),"r")
#plt.show()

'''
ax=plt.subplot(111);ax.yaxis.tick_right();
plt.plot(dayindi.get(u"大台指數"),"b")
plt.show()
ax=plt.subplot(211);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
#plt.plot(dayindi.get(u"大台散戶")-dayindi.get(u"小台散戶"),"b")
plt.plot(dayindi.get(u"大台散戶"),"b")
plt.plot(dayindi.get(u"小台散戶"),"r")
ax=plt.subplot(212);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
plt.plot(dayindi.get(u"大台黑手"),"b")
plt.plot(dayindi.get(u"小台黑手"),"r")
plt.show()
ax=plt.subplot(211);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
il.GetIndicatorByType(dayindi,"小台未純化大單作為")
il.GetIndicatorByType(dayindi,"小台未純化大單企圖")
plt.plot(dayindi.get("小台未純化大單作為"),"r")
plt.plot(dayindi.get("小台未純化大單企圖"),"b")
ax=plt.subplot(212);ax.yaxis.tick_right();plt.plot(np.zeros(300),"m")
plt.plot((dayindi.get("大台委買口")-dayindi.get("小台委買口"))-(dayindi.get("大台委賣口")-dayindi.get("小台委賣口")),"r")
plt.plot((dayindi.get("大台委買筆")-dayindi.get("小台委買筆"))-(dayindi.get("大台委賣筆")-dayindi.get("小台委賣筆")),"b")
#plt.plot(dayindi.get(u"上漲家數")-dayindi.get(u"下跌家數"),"r")
'''