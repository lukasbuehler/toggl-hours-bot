# Toggl Hours Bot

WIP

## Installation

### Environment variables

#### Toggl API

After cloning this repository, duplicate the file `default.env` and name it
`.env`.

Enter your Toggl API tokens of all the profiles that you want to get the hours
for, seperated by commas after `TOGGL_API_TOKENS`, like so:

```.env
TOGGL_API_TOKENS=YOUR_TOKEN_HERE,YOUR_OTHER_TOKEN_HERE,YOUR_OTHER_OTHER_TOKEN_HERE
```

#### Telegram Bot

After creating a new bot using the BotFather, copy the bot username and bot
token after the corresponding env vars:

```.env
TELEGRAM_BOT_USERNAME=
TELEGRAM_BOT_TOKEN=
```

### Python and pip dependencies

Install all the python and pip dependencies using this make command:

```
make install
```

## Running

Start the bot using

```
make start
```

### Daily hours

To send the daily hours to the group chat use this make target:

```
make send_daily_hours
```

Add a cronjob like this

```
0 23 * * * cd ~/projects/toggl-hours-bot && make send-daily-hours
```
