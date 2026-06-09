from multiprocessing import Process
from telegram.ext import (
    Application,
    CommandHandler
)

running_bots = {}


async def start_cmd(update, context):
    await update.message.reply_text(
        "مرحباً بك في بوت الصيد"
    )


def run_child(token):

    app = Application.builder().token(token).build()

    app.add_handler(
        CommandHandler(
            "start",
            start_cmd
        )
    )

    app.run_polling()


def start_bot(user_id, token):

    if user_id in running_bots:
        return False

    p = Process(
        target=run_child,
        args=(token,)
    )

    p.start()

    running_bots[user_id] = p

    return True


def stop_bot(user_id):

    if user_id not in running_bots:
        return False

    running_bots[user_id].terminate()

    del running_bots[user_id]

    return True
