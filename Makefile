compile: setcap.py
	pyinstaller -F setcap.py

test: setcap.py
	chmod +x setcap.py
	sudo ./setcap.py

run: setcap.py
	./dist/setcap

