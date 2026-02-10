import asyncio
import re
from telebot.async_telebot import AsyncTeleBot
import settings
import sqlite3 as sl
import logging
import other_functions
import telebot_functions

logging.basicConfig(filename=r"main.log", encoding="utf-8", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger()

bot = AsyncTeleBot(settings.TOKEN)

db = sl.connect("database.db")

if other_functions.bot_start(log, db):
    log.error("Somthing went wrong")
    exit(1)

def arg_expend(func):
    async def func1(data):
        await func(data, bot, log, db)

    return func1

bot.message_handler(["start"])(arg_expend(telebot_functions.start_cmd))
bot.message_handler(["refill"])(arg_expend(telebot_functions.refill_cmd))
bot.message_handler(["set"])(arg_expend(telebot_functions.set_cmd))
bot.callback_query_handler(func=lambda x: re.fullmatch("start", x.data))(arg_expend(telebot_functions.start_btn))
bot.callback_query_handler(func=lambda x: re.fullmatch("assign_to_dorm", x.data))(arg_expend(telebot_functions.assign_to_dorm_btn))
bot.callback_query_handler(func=lambda x: re.fullmatch("assign_to_[1-7]", x.data))(arg_expend(telebot_functions.assign_to_btn))
bot.callback_query_handler(func=lambda x: re.fullmatch("consume_chose", x.data))(arg_expend(telebot_functions.consume_chose_btn))
bot.callback_query_handler(func=lambda x: re.fullmatch("consume_[1-7]", x.data))(arg_expend(telebot_functions.consume_btn))

asyncio.run(bot.infinity_polling(skip_pending=True))
