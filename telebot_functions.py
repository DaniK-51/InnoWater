import datetime
import os.path
import re
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import sqlite3 as sl
import logging

async def refill_cmd(message: types.Message, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"refill_cmd {message.from_user.id}")
    user = db.execute("SELECT id, dorm, admin FROM users WHERE id = ?", [message.from_user.id]).fetchone()
    if not user:
        await bot.send_message(message.chat.id, "Use /start first")
    else:
        user_id, dorm_number, admin = user
        if admin:
            pre, number, dorm = message.text.split(' ')
            db.execute("UPDATE dorms SET cur_n = ?, max_n = ? WHERE number = ?", [int(number), int(number), int(dorm)])
            db.commit()

        await start_cmd(message, bot, log, db)

async def set_cmd(message: types.Message, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"set_cmd {message.from_user.id}")
    user = db.execute("SELECT id, dorm, admin FROM users WHERE id = ?", [message.from_user.id]).fetchone()
    if not user:
        await bot.send_message(message.chat.id, "Use /start first")
    else:
        user_id, dorm_number, admin = user
        if admin:
            pre, number, dorm = message.text.split(' ')
            db.execute("UPDATE dorms SET cur_n = ? WHERE number = ?", [int(number), int(dorm)])
            db.commit()

        await start_cmd(message, bot, log, db)

async def start_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"start {callback.from_user.id}")
    user = db.execute("SELECT id, dorm FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        db.execute("INSERT INTO users (id) VALUES (?)", [callback.from_user.id])
        db.commit()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Assign to dorm", callback_data="assign_to_dorm"))
        await bot.edit_message_text("Hello", callback.message.chat.id, callback.message.id, reply_markup=markup)
    else:
        user_id, dorm_number = user
        text = ''
        dorms = db.execute("SELECT number, cur_n, max_n FROM dorms ORDER BY number ASC").fetchall()
        for dorm in dorms:
            text += f"Dorm {dorm[0]}{">" if dorm_number == dorm[0] else ":"} {dorm[1]}/{dorm[2]} ({"{:.1%}".format((dorm[1] / dorm[2]) if dorm[2] else 0)})\n"
        markup = types.InlineKeyboardMarkup()
        if dorm_number:
            markup.add(types.InlineKeyboardButton("Consume from my dorm", callback_data=f"consume_{dorm_number}"),
                       types.InlineKeyboardButton("Consume from another dorm", callback_data=f"consume_chose"))
        else:
            markup.add(types.InlineKeyboardButton("Assign to dorm", callback_data="assign_to_dorm"),
                       types.InlineKeyboardButton("Consume bottle", callback_data=f"consume_chose"))
        markup.row(types.InlineKeyboardButton("Send a photo", callback_data="send_photo_chose"))
        await bot.edit_message_text(text, callback.message.chat.id, callback.message.id, reply_markup=markup)


async def start_cmd(message: types.Message, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"start {message.from_user.id}")
    user = db.execute("SELECT id, dorm FROM users WHERE id = ?", [message.from_user.id]).fetchone()
    if not user:
        db.execute("INSERT INTO users (id) VALUES (?)", [message.from_user.id])
        db.commit()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Assign to dorm", callback_data="assign_to_dorm"))
        await bot.send_message(message.chat.id, "Hello", reply_markup=markup)
    else:
        user_id, dorm_number = user
        text = ''
        dorms = db.execute("SELECT number, cur_n, max_n FROM dorms ORDER BY number ASC").fetchall()
        for dorm in dorms:
            text += f"Dorm {dorm[0]}{">" if dorm_number == dorm[0] else ":"} {dorm[1]}/{dorm[2]} ({"{:.1%}".format((dorm[1]/dorm[2]) if dorm[2] else 0)})\n"
        markup = types.InlineKeyboardMarkup()
        if dorm_number:
            markup.add(types.InlineKeyboardButton("Consume from my dorm", callback_data=f"consume_{dorm_number}"),
                       types.InlineKeyboardButton("Consume from another dorm", callback_data=f"consume_chose"))
        else:
            markup.add(types.InlineKeyboardButton("Assign to dorm", callback_data="assign_to_dorm"),
                       types.InlineKeyboardButton("Consume bottle", callback_data=f"consume_chose"))
        markup.row(types.InlineKeyboardButton("Send a photo", callback_data="send_photo_chose"))
        await bot.send_message(message.chat.id, text, reply_markup=markup)

async def assign_to_dorm_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"assign_to_dorm_btn {callback.from_user.id}")
    user = db.execute("SELECT id, dorm FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        await bot.send_message(callback.message.chat.id, "Use /start first")
    else:
        user_id, dorm_number = user
        text = ''
        if dorm_number:
            text += f"Current dorm: {dorm_number}\n"
        text += f"Chose new dorm number"
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("1", callback_data="assign_to_1"),
                   types.InlineKeyboardButton("2", callback_data="assign_to_2"),
                   types.InlineKeyboardButton("3", callback_data="assign_to_3"),
                   types.InlineKeyboardButton("4", callback_data="assign_to_4"))
        markup.row(types.InlineKeyboardButton("5", callback_data="assign_to_5"),
                   types.InlineKeyboardButton("6", callback_data="assign_to_6"),
                   types.InlineKeyboardButton("7", callback_data="assign_to_7"))
        markup.row(types.InlineKeyboardButton("⏎ Back", callback_data=f"start"))
        await bot.edit_message_text(text, callback.message.chat.id, callback.message.id, reply_markup=markup)

async def assign_to_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"assign_to_btn {callback.from_user.id}")
    number = int(re.fullmatch("assign_to_([1-7])", callback.data)[1])
    user = db.execute("SELECT id, dorm FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        await bot.send_message(callback.message.chat.id, "Use /start first")
    else:
        db.execute("UPDATE users SET dorm = ? WHERE id = ?", [number, callback.from_user.id])
        db.commit()

        await start_btn(callback, bot, log, db)

async def consume_chose_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"consume_chose_btn {callback.from_user.id}")
    user = db.execute("SELECT id, dorm FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        await bot.send_message(callback.message.chat.id, "Use /start first")
    else:
        user_id, dorm_number = user
        text = f"Chose dorm number"
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("1", callback_data="consume_1"),
                   types.InlineKeyboardButton("2", callback_data="consume_2"),
                   types.InlineKeyboardButton("3", callback_data="consume_3"),
                   types.InlineKeyboardButton("4", callback_data="consume_4"))
        markup.row(types.InlineKeyboardButton("5", callback_data="consume_5"),
                   types.InlineKeyboardButton("6", callback_data="consume_6"),
                   types.InlineKeyboardButton("7", callback_data="consume_7"))
        markup.row(types.InlineKeyboardButton("⏎ Back", callback_data=f"start"))
        await bot.edit_message_text(text, callback.message.chat.id, callback.message.id, reply_markup=markup)

async def consume_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    dorm_number = int(re.fullmatch("consume_([1-7])", callback.data)[1])
    log.debug(f"assign_to_dorm_btn {callback.from_user.id}")
    user = db.execute("SELECT id FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        await bot.send_message(callback.message.chat.id, "Use /start first")
    else:
        user_id = user[0]
        dorm_cur_n = db.execute("SELECT cur_n FROM dorms WHERE number = ?", [dorm_number]).fetchone()[0]
        db.execute("UPDATE dorms SET cur_n = ? WHERE number = ?", [dorm_cur_n - 1, dorm_number])
        db.commit()
        await start_btn(callback, bot, log, db)

async def send_photo_chose_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"send_photo_chose_btn {callback.from_user.id}")
    user = db.execute("SELECT id, dorm FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        await bot.send_message(callback.message.chat.id, "Use /start first")
    else:
        user_id, dorm_number = user
        text = f"Chose dorm number"
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("1", callback_data="send_photo_1"),
                   types.InlineKeyboardButton("2", callback_data="send_photo_2"),
                   types.InlineKeyboardButton("3", callback_data="send_photo_3"),
                   types.InlineKeyboardButton("4", callback_data="send_photo_4"))
        markup.row(types.InlineKeyboardButton("5", callback_data="send_photo_5"),
                   types.InlineKeyboardButton("6", callback_data="send_photo_6"),
                   types.InlineKeyboardButton("7", callback_data="send_photo_7"))
        markup.row(types.InlineKeyboardButton("⏎ Back", callback_data=f"start"))
        await bot.edit_message_text(text, callback.message.chat.id, callback.message.id, reply_markup=markup)

async def send_photo_btn(callback: types.CallbackQuery, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"send_photo_btn {callback.from_user.id}")
    dorm_number = int(re.fullmatch("send_photo_([1-7])", callback.data)[1])
    user = db.execute("SELECT id FROM users WHERE id = ?", [callback.from_user.id]).fetchone()
    if not user:
        await bot.send_message(callback.message.chat.id, "Use /start first")
    else:
        user_id = user[0]
        try:
            db.execute("INSERT INTO tmp (id, code, arg1) VALUES (?, 1, ?)", [callback.from_user.id, dorm_number])
        except sl.IntegrityError:
            db.execute("UPDATE tmp SET id = ?, code = 1, arg1 = ?", [callback.from_user.id, dorm_number])
        db.commit()
        text = "Please, send a photo of a water storage room. I will count how many of bottles left by my self)"
        await bot.send_message(callback.message.chat.id, text)

async def any_photo(message: types.Message, bot: AsyncTeleBot, log: logging.Logger, db: sl.Connection):
    log.debug(f"any_photo {message.from_user.id}")
    user = db.execute("SELECT id FROM users WHERE id = ?", [message.from_user.id]).fetchone()
    if not user:
        await bot.send_message(message.chat.id, "Use /start first")
    else:
        user_id = user[0]
        tmp = db.execute("SELECT code, arg1, arg2 FROM tmp WHERE id = ?", [message.from_user.id]).fetchone()
        if tmp:
            code, arg1, arg2 = tmp
            if code == 1:
                photo_id = db.execute("INSERT INTO photos (dorm, author_id, date) VALUES (?, ?, ?)", [arg1, message.from_user.id, datetime.date.today()]).lastrowid
                db.commit()
                file = await bot.get_file(message.photo[-1].file_id)
                f = await bot.download_file(file.file_path)
                filename = f"{photo_id}.jpg"
                # try:
                open(f"documents/{filename}", 'wb').write(f)
                # except Exception:
                #     os.mkdir("documents")
                #     open(f"documents/{filename}", 'wb').write(f)
                await bot.send_message(message.chat.id, "Uploaded successfully!")
                await start_cmd(message, bot, log, db)
