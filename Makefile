.PHONY: all
all: send_daily_hours

.PHONY: install
install: requirements.txt
	pip3 install -r requirements.txt

.PHONY: send-daily-hours
send-daily-hours: .env main.py
	python3 main.py send_daily_hours

.PHONY: start-bot
start-bot: .env main.py
	python3 main.py telegram