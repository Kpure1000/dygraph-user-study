import threading
import traceback
from database import Database
from utils import logger
from task import TaskManager

class UserManager:

    def __init__(self, db: Database):
        self.db = db
        self.users = {}
        self.lock = threading.Lock()

    def add(self, name, gender, age):
        try:
            self.lock.acquire(True)
            status, _, lastrowid = self.db.exec(f"insert into user (name, gender, age) values ('{name}', '{gender}', {age})")
            if status != None:
                return None, status
            id = lastrowid
            self.users[id] = TaskManager(self.db, id)
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            traceback.print_exc()
            return None, e
        finally:
            self.lock.release()
        return id, status
    
    def get_task_manager(self, id) -> TaskManager:
        if id in self.users:
            return self.users[id]
        else:
            return None
