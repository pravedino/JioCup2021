import json


def reset_database(database):
    with open(database) as json_file:
        temp_database = json.load(json_file)
        for person in temp_database:
            person["Tele Handle"] = person["Tele Handle"].lower()
            person["Points"] = 0
            person["Level"] = 0
            person["Multiplier"] = [[2, 0, 3], [3, 0, 2]]
            # Points, People, Number
            person["Unique Interactions"] = [0, [person["Tele Handle"]], 1]
            person["Cumulative Points"] = 0
            person["Reached Level"] = [20210915, 0, 0, 0, 0, 0]

    json_object = json.dumps(temp_database, indent=10)

    # Writing to sample.json
    with open(database, "w") as outfile:
        outfile.write(json_object)


def restore_database(prev_database):
    prev_database_item = json.load(open(prev_database, ))
    json_object = json.dumps(prev_database_item, indent=10)

    # Writing to sample.json
    with open("database.json", "w") as outfile:
        outfile.write(json_object)


def write_to_database(database, database_string):
    json_object = json.dumps(database, indent=8)
    with open(database_string, "w") as outfile:
        outfile.write(json_object)


def process_chat(data):
    for message in data["messages"]:
        # Retrieve text portion of the message
        if message["type"] != "message":
            continue
        text_array = message["text"]
        if not isinstance(text_array, list):
            continue

        # Remove hyphens from date
        date_raw = message["date"][:4] + message["date"][5:7] + message["date"][8:10]
        date = int(date_raw)
        # Iterate through text portion of message
        for text_dictionary in text_array:
            if not isinstance(text_dictionary, dict):
                continue
            text_type = text_dictionary["type"]
            text = text_dictionary["text"]
            if text_type != "hashtag" or text.lower() != "#jioer":
                continue

            print(date)
            print("jio message from: " + message["from"])
            process_jio(text_array, date)
            calculate_unique_interactions_points()
            calculate_cumulative_and_levels(date)
            # give_multiplier()


def process_jio(text_array, date):
    list_of_jioers = []
    list_of_jioees = []
    list_of_hashtags = []
    is_jioer = False
    is_jioee = False
    for text_dictionary in text_array:
        if isinstance(text_dictionary, dict):
            text_type = text_dictionary["type"]
            text = text_dictionary["text"].lower()

            # Check if next hashtags are jioers or jioees or hashtags
            if text_type == "hashtag":
                if text == "#jioer" or text == "#jioers":
                    is_jioer = True
                    is_jioee = False
                elif text == "#jioee" or text == "#jioees":
                    is_jioee = True
                    is_jioer = False
                else:
                    if text in official_hashtags:
                        list_of_hashtags.append(text)

            # If next element is a mention, add person to relevant list
            if text_type == "mention":
                if text not in list_of_tele_handles:
                    print(text + " CHANGED TELE HANDLE PCB!!")
                    break
                if is_jioer:
                    list_of_jioers.append(text)
                if is_jioee:
                    list_of_jioees.append(text)

    # CATCH DUPLICATES AND ERASE
    set_of_jioers = set(list_of_jioers)
    set_of_jioees = set(list_of_jioees)
    list_of_jioers = list(set_of_jioers)
    list_of_jioees = list(set_of_jioees)


    # CAN BE DONE WITH SET SUBSTRACTION
    index = 0
    while index < len(list_of_jioers):
        jioer = list_of_jioers[index]
        for jioee in list_of_jioees:
            if jioer == jioee:
                list_of_jioers.pop(index)
        index += 1

    participant_list = [*list_of_jioers, *list_of_jioees]
    print("Participants: ", end='')
    print({"Jioer": list_of_jioers, "Jioees": list_of_jioees})
    print("Hashtags: ", end='')

    required_pax = 3
    if date < 20210917:
        required_pax = 4

    # For Twin Tuesday
    if date == 20210921 and "#shanday" in list_of_hashtags:
        required_pax = 2

    # For SMM CCB
    if date >= 20210927:
        required_pax = 2

    if len(participant_list) >= required_pax:
        process_points(list_of_jioers, list_of_jioees, list_of_hashtags, date)
        unique_interactions_accumulater(participant_list)
    else:
        print("This jio was not counted as it has too few ppl :(")

    print("\n")


def process_points(list_of_jioers, list_of_jioees, list_of_hashtags, date):
    # For each person, create a pair w tele handle and points (helps w multiplier later)
    participant_pair_list = []
    hashtag_points = len(list_of_hashtags)
    print(list_of_hashtags)

    # add 2 extra points for SHIMSHAMBONUS or excurSHAN
    if date >= 20210917:
        if "#shimshambonus" in list_of_hashtags:
            hashtag_points += 2
        if date == 20210922 and "#excurshan" in list_of_hashtags:
            hashtag_points += 2

    # add 1 extra point for gmbojio
    if "#gmbojio" in list_of_hashtags:
        hashtag_points += 1

    # add 2 extra points for shantastic4
    if "#shantastic4" in list_of_hashtags:
        if date >= 20210927:
            hashtag_points += 2

    # award jioer
    for jioer in list_of_jioers:
        participant_pair_list.append([jioer, 2])

    # award_jioees
    for jioee in list_of_jioees:
        participant_pair_list.append([jioee, 1])

    # award_hashtags
    for participant_pair in participant_pair_list:
        participant_pair[1] += hashtag_points

    apply_multiplier(participant_pair_list, date)


def apply_multiplier(participant_pair_list, date):
    for participant_pair in participant_pair_list:
        tele_handle = participant_pair[0]
        points = participant_pair[1]
        total_multiplier = 1
        for person in global_database:
            if person["Tele Handle"] == tele_handle:
                if amplificaSHAN_date <= date:
                    if person["Level"] < 3:
                        total_multiplier *= 2

                # Give Multipliers as prizes for levels
                # for multiplier_list in person["Multiplier"]:
                #     multiplier = multiplier_list[0]
                #     start_date = multiplier_list[1]
                #     duration = multiplier_list[2]
                #     end_date = calculate_end_date(start_date, duration)
                #
                #     if start_date <= date <= end_date:
                #         total_multiplier *= multiplier

                if tele_handle == "@jobeet":
                    print(person["Points"])
                    print(total_multiplier)

                person["Points"] += (points * total_multiplier)


def calculate_end_date(start_date, duration):
    # CUSTOMISED FOR SEPTEMBER ONLY
    return start_date + duration - 1


def give_multiplier():
    for person in global_database:
        reached_level_list = person["Reached Level"]
        # VERY IFFY DESIGN
        # Assume first multiplier is lvl 3 and second is lvl 5
        if reached_level_list[3] != 0:
            person["Multiplier"][0][1] = reached_level_list[3]

        if reached_level_list[5] != 0:
            person["Multiplier"][1][1] = reached_level_list[5]


def unique_interactions_accumulater(participants_list):
    if len(participants_list) > 5:
        return None
    else:
        for participant in participants_list:
            for person in global_database:
                if person["Tele Handle"] == participant:
                    for participant_2 in participants_list:
                        add_to_unique_interactions = True
                        unique_interactions_list = person["Unique Interactions"][1]
                        for interaction in unique_interactions_list:
                            if participant_2 == interaction:
                                add_to_unique_interactions = False

                        if add_to_unique_interactions:
                            unique_interactions_list.append(participant_2)


def calculate_unique_interactions_points():
    for person in global_database:
        unique_interactions_list = person["Unique Interactions"][1]
        list_length = len(unique_interactions_list)
        person["Unique Interactions"][2] = list_length
        point_count = 0
        points_system = [15, 12, 10, 10, 10, 10, 10, 10]
        while list_length > 0:
            for points in points_system:
                if list_length >= points:
                    point_count += 2
                list_length -= points

        person["Unique Interactions"][0] = point_count


def calculate_cumulative_and_levels(date):
    for person in global_database:
        person["Cumulative Points"] = person["Points"] + person["Unique Interactions"][0]
        cumulative = person["Cumulative Points"]
        current_level = person["Level"]
        for level in reversed(level_system):
            if current_level >= int(level):
                break
            level_points = level_system[level]
            if level_points > cumulative:
                continue
            else:
                person["Level"] = int(level)
                person["Reached Level"][int(level)] = date
                break


def print_leaderboard():
    points_leaderboard = []
    unique_interactions_leaderboard = []
    for person in global_database:
        points_entry = [person["Cumulative Points"], person["Name"]]
        UI_entry = [person["Unique Interactions"][2], person["Unique Interactions"][1], person["Name"]]
        points_leaderboard.append(points_entry)
        unique_interactions_leaderboard.append(UI_entry)

    points_leaderboard.sort(reverse=True)
    unique_interactions_leaderboard.sort(reverse=True)
    print("POINTS LEADERBOARD")
    print("\n")
    for points_list in points_leaderboard:
        print(points_list[1] + ": " + str(points_list[0]))
    print("\n")
    print("UNIQUE INTERACTIONS LEADERBOARD")
    print("\n")
    for UI_list in unique_interactions_leaderboard:
        print(UI_list[2] + ": " + str(UI_list[0]))


reset_database("database.json")

# Opening JSON file
f = open('till 30 chat.json', encoding="utf8")
d = open('database.json', )
# returns JSON object as a dictionary
chat = json.load(f)
global_database = json.load(d)

# Global variables
list_of_tele_handles = []
for person_dict in global_database:
    list_of_tele_handles.append(person_dict["Tele Handle"])
official_hashtags = ["#shantastic4", "#shanday", "#gmbojio", "#shimshambonus", "#excurshan"]
amplificaSHAN_date = 20210927
level_system = {"0": 0,
                "1": 10,
                "2": 25,
                "3": 35,
                "4": 50,
                "5": 65
                }

# Calculation of points
process_chat(chat)
write_to_database(global_database, "database.json")
print_leaderboard()
