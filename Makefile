compile: setcap.py
	pyinstaller -F setcap.py
	sudo mv ./dist/setcap /sbin/setcap

view:
	cat /etc/setcap.ini