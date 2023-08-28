import operator

participants = os.getenv("NAMES", "").split(",")

def _get_users_over_target(users):
    users_over_target = []

    for user in users:
        if user["eth_hours"] > user["day_target_hours"]:
            users_over_target.append(user["name"])

    return users_over_target


def _get_winner_and_loser(users):
    winner = ""
    winner_hours = 0
    loser = ""
    loser_hours = 0

    for user in users:
        if user["name"] not in participants:
            continue

        if not winner or winner_hours < user["eth_hours"]:
            winner = user["name"]
            winner_hours = user["eth_hours"]
        if not loser or loser_hours > user["eth_hours"]:
            loser = user["name"]
            loser_hours = user["eth_hours"]

    return winner, winner_hours, loser, loser_hours


def _motivational_message_for_user(name: str = "", eth_hours_today=-1, other_hours_today=-1) -> str:
    if not name:
        return ""

    message = ""

    eth_hours_today = round(eth_hours_today * 10) / 10
    other_hours_today = round(other_hours_today * 10) / 10

    if eth_hours_today > 7:
        message = f"Amazing work today {name}, you clocked in a whopping {eth_hours_today} hours for ETH today!"

    elif eth_hours_today > 6:
        message = f"Great work {name}! You did a total of {eth_hours_today} hours for ETH today. "

    elif eth_hours_today > 5:
        message = f"Good job {name}, you did {eth_hours_today} hours for ETH today and almost reached the daily target of 6 hours. "

    elif eth_hours_today > 4:
        message = f"{name}, you did ok with {eth_hours_today} hours tracked for ETH today. "

    elif eth_hours_today > 3:
        message = f"{name}, you only did a bit of work for ETH today, {eth_hours_today} hours to be exact. "

    elif eth_hours_today > 2:
        message = f"Ok, {name}, {eth_hours_today} hours for ETH today are not a lot, we know you can do better. "

    elif eth_hours_today > 1:
        message = f"{name}, did you forget to track some work today? Or are {eth_hours_today} hours for ETH the best you could do? "

    elif eth_hours_today >= 0:
        message = f"{name} took a break from ETH today. "


    if other_hours_today > 3:
        message += f"You also seemed to be pretty busy with other stuff, where you spent {other_hours_today} hours today."

    elif other_hours_today > 1:
        message += f"You also seemed preoccupied with some other stuff, where you spent {other_hours_today} hours today."

    return message


def make_day_recap_caption(today_data, week_data):

    today_data["user_hours"].sort(key=operator.itemgetter("eth_hours"), reverse=True)
    week_data["user_hours"].sort(key=operator.itemgetter("eth_hours"), reverse=True)

    #users_over_target = _get_users_over_target(today_data["user_hours"])

    caption = f"📅 The daily hours are in ✨\n"

    for user in today_data["user_hours"]:
        name = user['name'].split()[0]
        eth_hours = user['eth_hours']
        other_hours = user['other_hours']

        # add a special message for this user
        caption += _motivational_message_for_user(name, eth_hours_today=eth_hours, other_hours_today=other_hours) +"\n\n"

    return caption


def make_week_recap_caption(week_data):

    week_data["user_hours"].sort(key=operator.itemgetter("eth_hours"), reverse=True)

    caption = "📅 This week's results are in ✨\n"

    if not week_data["user_hours"] or len(week_data["user_hours"]) == 0:
        caption += "🦗 ... No one did any work this week ... 🦗"
        return caption

    week_winner, week_winner_hours, week_loser, week_loser_hours = _get_winner_and_loser(week_data["user_hours"])

    caption += f"Congratulations {week_winner}, you earned yourself a coffee! ☕\nPaid for you by {week_loser}.\n\n\n"

    caption += "These are the stats of this week:\n\n"


    for user in week_data["user_hours"]:
        name = user['name'].split()[0]
        eth_hours = round(user['eth_hours'] * 10) / 10
        other_hours = round(user['other_hours'] * 10) / 10

        caption += f"{name} did {eth_hours} hours for ETH (and tracked {other_hours} hours for other stuff)\n\n"

    return caption