call C:%HomePath%\Anaconda3\Scripts\activate.bat

:go
python 0_redis_to_db.py
timeout /t 10

goto go
