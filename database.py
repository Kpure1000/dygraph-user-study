import sqlite3
import threading
import traceback
from utils import logger

class Database:
    def __init__(self, name):
        try:
            self.conn = sqlite3.connect(name, timeout=10, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.lock = threading.Lock()
            logger.info(f"Database {name} connected")
        except Exception as e:
            logger.error(f"Database {name} connection failed: {e}")
            traceback.print_exc()
        
    def exec(self, cmd):
        status = None
        res = None
        lastrowid = None
        try:
            self.lock.acquire(True)
            logger.info(f"Executing command: {cmd}")
            self.cursor.execute(cmd)
            res = self.cursor.fetchall()
            lastrowid = self.cursor.lastrowid
            self.conn.commit()
            logger.info(f"Executed successfully.")
        except Exception as e:
            logger.error(f"Executed failed: {e}")
            traceback.print_exc()
            status = e
        finally:
            self.lock.release()

        return status, res, lastrowid

    def exec_many(self, command, values):
        status = None
        res = None
        try:
            self.lock.acquire(True)
            logger.info(f"Executing multi-command: {command}")
            self.cursor.executemany(command, values)
            res = self.cursor.fetchall()
            self.conn.commit()
            logger.info(f"Executed successfully.")
        except Exception as e:
            logger.error(f"Executed failed: {e}")
            traceback.print_exc()
            status = e            
        finally:
            self.lock.release()

        return status, res

    def close(self):
        self.conn.close()
        logger.info(f"Database closed")
