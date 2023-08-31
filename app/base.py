#!/usr/bin/env python
import os
import sys

path = os.path.join(os.path.dirname(__file__), "../utils")
sys.path.insert(0, path)

import logging
from util import dir_path_check
import sqlite3


class Base:
    """
    This class is for logging and DB initilization
    """

    Save_path_db = "data/my_data.db"
    Save_dir = "data"
    Db_column = "Idx, Url, Date, Headline, Summarization"

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.path_db = os.path.join(self.base_path, os.path.pardir, self.Save_path_db)
        self.save_dir = os.path.join(self.base_path, os.path.pardir, self.Save_dir)
        self.logger = self.df_log()

    def load_db(self):
        # load db
        dir_path = os.path.dirname(self.path_db)
        dir_path_check(dir_path)
        self.conn = sqlite3.connect(self.path_db)
        self.c = self.conn.cursor()

    def create_db_table(self, table_name=None, overide=False):
        # check if task already exists
        self.c.execute("SELECT name from sqlite_master where type= 'table'")
        table_lists = self.c.fetchall()
        table_lists = [i[0] for i in table_lists]
        self.table_name = table_name

        if overide and self.table_name in table_lists:
            self.c.execute(f"DROP TABLE {self.table_name}")
            self.c.execute(f"""CREATE TABLE {self.table_name} ({self.Db_column})""")
        if self.table_name not in table_lists:
            self.c.execute(f"""CREATE TABLE {self.table_name} ({self.Db_column})""")

    def df_log(self):
        logger = logging.getLogger("my_news_summarizer")
        logger.setLevel(logging.DEBUG)

        log_path = os.path.join(self.base_path, "../data/crawler.log")
        dir_path_check(os.path.dirname(log_path))
        fh = logging.FileHandler(log_path, "a", "utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(fh)
            logger.addHandler(consoleHandler)

        logger.propagate = False

        return logger

    def close_log(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
