import sqlite3 as sl
import logging

def out(table: sl.Connection, name: str = '', const: str = ''):
    if name == '':
        tables = list(map(lambda x: x[1], table.execute("PRAGMA table_list;").fetchall()))
        texts = list(map(lambda x: out(table, x, const), tables))
        return '\n'.join(texts)

    data = [list(map(lambda x: x[1], table.execute(f"PRAGMA table_info({name})").fetchall()))]
    n_of_columns = len(data[0])
    data.extend(list(map(lambda x: list(map(str, x)), table.execute(f"SELECT * FROM {name} {const}"))))
    maxes = []
    for i in range(n_of_columns):
        maxes.append(max(list(map(lambda x: len(x[i]), data))))

    for i in range(n_of_columns):
        for j in range(len(data)):
            data[j][i] = data[j][i].__format__(f'<{maxes[i]}')
    text = f"{name} {len(data) - 1}\n"
    for i in data:
        text += ' '.join(map(str, i)) + '\n'
    text += "-" * (sum(maxes) + n_of_columns - 1)
    return text

def bot_start(log: logging.Logger, db: sl.Connection):
    log.info("Starting initial checking...")
    table_list = list(map(lambda x: x[1], db.execute("PRAGMA table_list;").fetchall()))
    if not "users" in table_list:
        log.debug(f"Table \"users\" does not exist, creating a new one...")
        try:
            db.execute("CREATE TABLE users (id INT PRIMARY KEY, dorm INT, admin INT)")
        except Exception as e:
            log.error(f"Table \"users\" didn't create successfully, error: {e}")
            return 1
        log.debug(f"Table \"users\" created successfully")
    if not "dorms" in table_list:
        log.debug(f"Table \"dorms\" does not exist, creating a new one...")
        try:
            db.execute("CREATE TABLE dorms (number INT PRIMARY KEY, cur_n INT, max_n INT)")
        except Exception as e:
            log.error(f"Table \"dorms\" didn't create successfully, error: {e}")
            return 1
        log.debug(f"Table \"dorms\" created successfully")
    for n in range(1, 8):
        dorm = db.execute("SELECT * FROM dorms WHERE number = ?", [n]).fetchone()
        if not dorm:
            log.debug(f"Table \"dorm_{n}\" does not exist, creating a new one...")
            db.execute("INSERT INTO dorms (number, cur_n, max_n) VALUES (?, ?, ?)", [n, 0, 0])
            log.debug(f"Table \"dorm_{n}\" created successfully")
    if not "tmp" in table_list:
        log.debug(f"Table \"tmp\" does not exist, creating a new one...")
        try:
            db.execute("CREATE TABLE tmp (id INT PRIMARY KEY, code INT, arg1 INT, arg2 INT)")
        except Exception as e:
            log.error(f"Table \"tmp\" didn't create successfully, error: {e}")
            return 1
        log.debug(f"Table \"tmp\" created successfully")
    log.info("Done")
    db.commit()
    return 0
