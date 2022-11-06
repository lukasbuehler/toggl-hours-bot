.PHONY: all
all: send_daily_hours

.PHONY: install
install: requirements.txt
	pip3 install -r requirements.txt

.PHONY: day-recap
day-recap: .env main.py
	python3 main.py day-recap

.PHONY: week-recap
week-recap: .env main.py
	python3 main.py week-recap

.PHONY: month-recap
month-recap: .env main.py
	python3 main.py month-recap

.PHONY: start-bot
start-bot: .env main.py
	python3 main.py telegram