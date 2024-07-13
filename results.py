import json
import traceback
from database import Database
from utils import logger
from datetime import datetime

class ResultsManager:
    def __init__(self, db:Database):
        self.db = db

    def is_saved(self, id):
        try:
            status, res, _ = self.db.exec(f'select is_saved from results where id = {id}')
            if status != None:
                raise Exception(f'Error select results for id {id}, info: {status}')
            if len(res) == 0:
                return False
            return res[0][0]
        except Exception as e:
            logger.error(f'Error checking if results are saved for id {id}, info: {traceback.format_exc()}')
            raise Exception(f'Error checking if results are saved for id {id}, info: {traceback.format_exc()}')

    def add_result(self, id, task_name, result, final:bool):
        try:
            status, res_id, _ = self.db.exec(f"select id from tasks where id = {id}")
            if status != None:
                raise Exception(f'Error select tasks for id {id}, info: {status}')
            if len(res_id) == 0:
                raise Exception(f'Task with id {id} not found')
            status, res, _ = self.db.exec(f'select result, is_saved from results where id = {id}')
            if status != None:
                raise Exception(f'Error select results for id {id}, info: {status}')
            if len(res) == 0:
                results = {task_name: [result]}
                status, _, _ = self.db.exec(f"insert into results (id, result, is_saved) values ({id}, '{json.dumps(results)}', {final})")
                if status != None:
                    raise Exception(f'Error inserting results for id {id}, info: {status}')
                
                logger.info(f"Results for id {id} created")

            else:
                (results, is_saved) = res[0]
                if bool(is_saved):
                    logger.warn(f"Results for id {id} are already saved")
                    return
                results = json.loads(results)
                if (task_name not in results):
                    results[task_name] = []
                results[task_name].append(result)
                status, _, _ = self.db.exec(f"update results set result='{json.dumps(results)}', is_saved={final} where id = {id}")
                if status != None:
                    raise Exception(f'Error updating results for id {id}, info: {status}')
                
                logger.info(f"Results for id {id} updated, is {' NOT ' if not final else ' '}final.")

        except Exception as e:
            logger.error(f'Error adding result for id {id}, info: {e}')
            raise Exception(f'Error adding result for id {id}, info: {traceback.format_exc()}')

    def get_finish_time(self, id):
        try:
            status, res1, _ = self.db.exec(f'select submit_time, is_saved from results where id = {id}')
            if status != None:
                logger.error(f'Errir selecting results for id {id}, info: {status}')
                raise Exception(f'Error selecting results for id {id}, info: {status}')
            if len(res1) == 0:
                logger.error(f'Connot find results for id {id}, info: {status}')
                raise Exception(f'Connot find results for id {id}, info: {status}')
            (submit_time, is_saved) = res1[0]
            if not bool(is_saved):
                logger.error(f'Results for id {id} are not saved')
                raise Exception(f'Results for id {id} are not saved')
            end_time = datetime.strptime(submit_time, '%Y-%m-%d %H:%M:%S')
            status, res2, _ = self.db.exec(f'select create_time from user where id = {id}')
            if status != None:
                logger.error(f'Connot find user info for id {id}, info: {status}')
                raise Exception(f'Connot find user info for id {id}, info: {status}')
            if len(res2) == 0:
                logger.error(f'Connot find user info for id {id}')
                raise Exception(f'Connot find user info for id {id}')
            create_time = res2[0][0]
            start_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
            return (end_time - start_time).seconds
        except Exception as e:
            logger.error(f'Error getting time: {traceback.format_exc()}')
            traceback.print_exc()
            return None
        
    def get_finished_users(self):
        try:
            status, res, _ = self.db.exec('select id from results where is_saved = 1')
            if status != None:
                logger.error(f'Error selecting finished users, info: {status}')
                raise Exception(f'Error selecting finished users, info: {status}')
            return [user[0] for user in res]
        except Exception as e:
            logger.error(f'Error getting finished users: {traceback.format_exc()}')
            traceback.print_exc()
            return None
