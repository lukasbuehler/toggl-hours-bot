
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
        if not winner or winner_hours < user["eth_hours"]:
            winner = user["name"]
            winner_hours = user["eth_hours"]
        if not loser or loser_hours > user["eth_hours"]:
            loser = user["name"]
            loser_hours = user["eth_hours"]

    return winner, winner_hours, loser, loser_hours




def make_day_recap_caption(today_data, week_data):

    users_over_target = _get_users_over_target(today_data["user_hours"])

    caption = f"📅 The daily hours are in ✨\n"

    if len(users_over_target) >= 1:
        caption += f"Well done {', '.join(users_over_target)} you have achieved the daily goal!\n"
    else:
        caption += "You were all a bunch of lazy fucks today! No one achieved the daily target of 6h.\n"

    #today_winner, today_winner_hours, today_loser, today_loser_hours = _get_winner_and_loser(data["user_hours"])



    # Congratulate the winner if the target was met 
    # If not motivate them
    # Shame the loser
    
    
    

    #caption = f"Most hours today: {today_winner} ({round(today_winner_hours * 10)/10}h)\n" \
    #    + f"Least hours today: {today_loser} ({round(today_loser_hours * 10)/10}h)\n" \
    #    + f"Most hours this week: {week_winner} ({round(week_winner_hours * 10)/10}h)\n" \
    #    + f"Least hours this week: {week_loser} ({round(week_loser_hours * 10)/10}h)\n" \


    return caption


def make_week_recap_caption(week_data):
    caption = "📅 This week's results are in ✨\n"

    if not week_data["user_hours"] or len(week_data["user_hours"]) == 0:
        caption += "🦗 ... No one did any work this week ... 🦗"
        return caption

    week_winner, week_winner_hours, week_loser, week_loser_hours = _get_winner_and_loser(week_data["user_hours"])

    caption += f"Congratulations {week_winner}, you earned yourself a coffee! ☕\nPaid for you by {week_loser}.\n\n\n"

    caption += "These are the stats of this week:\n\n"

    for user in week_data["user_hours"]:
        name = user['name']
        eth_hours = round(user['eth_hours'] * 10) / 10
        other_hours = round(user['other_hours'] * 10) / 10

        caption += f"{name} did {eth_hours} hours for ETH (and tracked {other_hours} hours for other stuff)\n\n"

    return caption