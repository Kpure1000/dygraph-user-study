import threading
import traceback
from database import Database
from utils import logger
from task import TaskManager
from results import ResultsManager

class UserManager:

    def __init__(self, db: Database):
        try:
            self.db = db
            self.taskManagers = {}
            self.resultsManager = ResultsManager(db)
            self.lock = threading.Lock()
        except Exception as e:
            logger.error(f"Error initializing user manager: {traceback.format_exc()}")
            raise Exception(f"Error initializing user manager: {traceback.format_exc()}")

    def add(self, name, gender, age):
        try:
            self.lock.acquire(True)
            status, _, lastrowid = self.db.exec(f"insert into user (name, gender, age) values ('{name}', '{gender}', {age})")
            if status != None:
                return None, status
            id = lastrowid
            self.taskManagers[id] = TaskManager(self.db, id)
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            traceback.print_exc()
            return None, e
        finally:
            self.lock.release()
        return id, status
    
    def get_task_manager(self, id) -> TaskManager:
        try:
            if self.resultsManager.is_saved(id):
                logger.info(f"User {id} has already saved results")
                raise Exception(f"User {id} has already saved results")
            if id not in self.taskManagers:
                self.taskManagers[id] = TaskManager(self.db, id)
            return self.taskManagers[id]
        except Exception as e:
            logger.error(f"Error getting task manager for id {id}, info: {e}")
            traceback.print_exc()
            return None
