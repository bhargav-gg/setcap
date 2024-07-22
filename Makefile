compile: setcap.py
	pyinstaller -F setcap.py
	sudo mv ./dist/setcap /sbin/setcap

test: setcap.py
	chmod +x setcap.py
	sudo ./setcap.py

run: setcap.py
	sudo ./setcap.py

