# -*- coding: utf-8 -*-
import lib.util as lu
import lib.capi as lc
import pythoncom, time, os,threading
import _getpass as getpass


if __name__ == '__main__':
	log = lu.Logger(level='crit')
	#輸入身分證與密碼
	Id=getpass.getpass(prompt='ID= ')
	Pw=getpass.getpass(prompt='Password= ')
	
	CA=lc.CAP_Agent(Id,Pw,log)
