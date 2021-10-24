pyinstaller -F --add-data includes/config.json:includes --add-data includes/undelivered_help.pdf:includes -n pinpbc --distpath bin npbc.py
