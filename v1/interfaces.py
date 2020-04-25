# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import sqlite3

#
# database
#
class Database:
    def __init__(self,filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)

    def __enter__(self):
        self.crsr = self.conn.cursor()
        return self.crsr

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.crsr = None

    def commit(self):
        self.conn.commit()

#
# abstract modem
#
class Modem:
    def emit(self,s): raise NotImplementedError
    def readline(self): raise NotImplementedError
    def accept_call(self): raise NotImplementedError
    def reject_call(self,hard): raise NotImplementedError

