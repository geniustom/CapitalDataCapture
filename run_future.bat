call C:%HomePath%\Anaconda3\Scripts\activate.bat

:go

python 1_get_market_info.py
python 2_get_future_data.py %1 %2

goto go