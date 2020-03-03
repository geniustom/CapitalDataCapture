call C:%HomePath%\Anaconda3\Scripts\activate.bat

:go

python 1_get_market_info.py
python 3_get_option_data.py

goto go