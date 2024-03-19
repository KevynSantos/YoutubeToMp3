Criando executavel do echobot

pyinstaller --onefile --hidden-import=telegram echobot.py

pyinstaller --onefile --hidden-import=telegram examples/echobot.py