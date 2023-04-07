.PHONY: all
all: strat-bot

.PHONY: install
install: requirements.txt
	pip3 install -r requirements.txt

.PHONY: day-recap
day-recap: .env recap.py
	python3 recap.py day-recap

.PHONY: week-recap
week-recap: .env recap.py
	python3 recap.py week-recap

.PHONY: month-recap
month-recap: .env recap.py
	python3 recap.py month-recap

.PHONY: start-bot
start-bot: .env telegram_handler.py
	python3 telegram_handler.py start