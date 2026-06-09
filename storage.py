import json

FILE = "bots.json"

def save_token(user_id, token):
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    data[str(user_id)] = token

    with open(FILE, "w") as f:
        json.dump(data, f)
