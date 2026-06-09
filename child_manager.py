running_bots = {}


def start_bot(user_id, token):

    if not token:
        return False

    running_bots[user_id] = token

    return True


def stop_bot(user_id):

    if user_id in running_bots:
        del running_bots[user_id]

        return True

    return False
