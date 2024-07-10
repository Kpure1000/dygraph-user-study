import json
import traceback
from database import Database
import threading
from utils import logger
from datetime import datetime
from task import TaskManager, task1_name, task2_name

class ResultsManager:
    def __init__(self, db:Database):
        self.db = db
        self.results = {}
        self.lock = threading.Lock()

    def add_result(self, id, task_name, result):
        with self.lock:
            if id not in self.results:
                self.results[id] = {
                    task1_name: [],
                    task2_name: [],
                }
            self.results[id][task_name].append(result)

    def is_saved(self, id):
        try:
            self.lock.acquire(True)
            status, res1, _ = self.db.exec(f'select id from results where id = {id}')
            if status != None:
                logger.error(f'Error select results for id {id}, info: {status}')
                traceback.print_exc()
                raise Exception(f'Error select results for id {id}, info: {status}')
            if len(res1) != 0:
                return True
            return False
        except Exception as e:
            logger.error(f'Error checking if results are saved: {e}')
            traceback.print_exc()
            raise Exception(f'Error checking if results are saved: {e}')
        finally:
            self.lock.release()

    def save_results(self, id):
        try:
            self.lock.acquire(True)
            if id not in self.results:
                logger.error(f'No results found for id {id}')
                traceback.print_exc()
                return
            status, _, _ = self.db.exec(f"insert into results (id, result) values ({id}, '{json.dumps(self.results[id])}')")
            if not status:
                logger.error(f'Error saving results for id {id}')
        except Exception as e:
            logger.error(f'Error saving results: {e}')
        finally:
            self.lock.release()

    def export_results(self, id):
        try:
            self.lock.acquire(True)
            if id not in self.results:
                logger.error(f'No results found for id {id}')
                traceback.print_exc()
                return
            status, res1, _ = self.db.exec(f'select result, submit_time from results where id = {id}')
            if status != None:
                logger.error(f'Error select results for id {id}, info: {status}')
                traceback.print_exc()
                return
            (results, submit_time) = res1[0]
            finish_time = datetime.strptime(submit_time, '%Y-%m-%d %H:%M:%S')
            status, res2, _ = self.db.exec(f'select name, gender, age, create_time from user where id = {id}')
            if status != None:
                logger.error(f'Error select user info for id {id}, info: {status}')
                return
            (name, gender, age, create_time) = res2[0]
            start_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
            final_result = {
                "id": id,
                "name": name,
                "gender": gender,
                "age": int(age),
                "finish_time": (finish_time - start_time).seconds,
                "results": json.loads(results)
            }
            logger.info(f'Exporting results for id {id}, results: {final_result}')
            with open(f'results/{id}.json', 'w') as f:
                json.dump(final_result, f, indent=4)
        except Exception as e:
            logger.error(f'Error saving results: {e}')
            traceback.print_exc()
        finally:
            self.lock.release()
