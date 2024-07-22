compile: setcap.py
	pyinstaller -F setcap.py
	sudo mv ./dist/setcap /sbin/setcap

