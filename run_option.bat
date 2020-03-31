call C:%HomePath%\Anaconda3\Scripts\activate.bat


:go
python 3_get_option_data.py %1 %2
goto go