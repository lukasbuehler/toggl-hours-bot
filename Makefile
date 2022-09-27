.PHONY: all
all: start

.PHONY: install
install: requirements.txt
	pip3 install -r requirements.txt

.PHONY: start
start: .env main.py
	python3 main.py

.PHONY: start-bot
start-bot: .env telegram.py
	python3 telegram.py