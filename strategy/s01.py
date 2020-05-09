# coding=UTF-8
import imp,sys;	sys.path.append("../")
import lib.indicator as ind; 	imp.reload(ind);  
############################################################################### 
def s1(self,PRICE,i,I):
    baseT= 15
    if i< (baseT) : return
    aa=I.get("成筆差")[i-1]
    
    if aa>1 : self.EnterShort(PRICE)
    if aa<0 : self.EnterLong(PRICE)
    self.CheckDailyExitAll(I.get("TIME")[i],PRICE)
     
############################################################################### 
import os
STittle=u"[s01]成筆差"
Market='TX00'
DorN='D'
FName=os.path.split(__file__)[1].split('.')[0]
if __name__ == '__main__':
    exec(open(os.path.split(os.path.realpath(__file__))[0]+'\\init.py').read())