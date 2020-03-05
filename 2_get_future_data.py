import _config as conf
import lib.util as lu
import lib.quote as lq
import pythoncom,time,datetime,sys

def init():
	lu.Beep([20,40,60,80],120)
	tick_data = open('data/'+now+'_future_tick.txt','a')
	price_data = open('data/'+now+'_future_price.txt','a')
	market_data = open('data/'+now+'_future.txt','a') 
	stock_code = open('market_info/future_code.json','r')
	return tick_data,price_data,market_data,stock_code


if __name__ == '__main__':
	log = lu.Logger(level='crit')
	now = datetime.datetime.now().strftime('%y%m%d_%H%M')
	
	#輸入身分證與密碼
	Id=conf.getpass(prompt='ID= ')
	Pw=conf.getpass(prompt='PW= ')
	RedisHost=conf.get_redis_host()
	print('Redis host:',RedisHost)
	tid=0
	
	from_idx=0 if len(sys.argv)!=3 else sys.argv[1]
	to_idx=0 if len(sys.argv)!=3 else sys.argv[2]
	
	while True:
		tick_data,price_data,market_data,stock_code=init()
		t1=lq.CAP_Thread(Id,Pw,log,stock_code,price_data,tick_data,market_data,thread_id=tid,redis_host=RedisHost,from_idx=from_idx,to_idx=to_idx)
		t1.start()
		while t1.is_alive(deadline=10000):
			time.sleep(0.0001)
			pythoncom.PumpWaitingMessages()
		t1.join()
		time.sleep(2)
		tid+=1
		
		print('thread',tid,' has been dead!!,rebuild the new one')
		tick_data.close()
		price_data.close()
		market_data.close()
		stock_code.close()