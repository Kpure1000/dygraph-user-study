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
            status, res, _ = self.db.exec(f'select result, is_saved from results where id = {id}')
            if status != None:
                raise Exception(f'Error select results for id {id}, info: {status}')
            if len(res) == 0:
                results = {task_name: [result]}
                status, _, _ = self.db.exec(f"insert into results (id, result, is_saved) values ({id}, '{json.dumps(results)}', {final})")
                if status != None:
                    raise Exception(f'Error inserting results for id {id}, info: {status}')
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
        except Exception as e:
            logger.error(f'Error adding result for id {id}, info: {e}')
            raise Exception(f'Error adding result for id {id}, info: {traceback.format_exc()}')

    def export_results(self, id):
        try:
            status, res1, _ = self.db.exec(f'select result, submit_time, is_saved from results where id = {id}')
            if status != None:
                logger.error(f'Error select results for id {id}, info: {status}')
                raise Exception(f'Error select results for id {id}, info: {status}')
            if len(res1) == 0:
                logger.error(f'No results found for id {id}')
                raise Exception(f'No results found for id {id}')
            (results, submit_time, is_saved) = res1[0]
            if not bool(is_saved):
                logger.error(f'Results for id {id} are not saved')
                raise Exception(f'Results for id {id} are not saved')
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
            logger.error(f'Error saving results for id {id}, info: {e}')
            raise Exception(f'Error saving results for id {id}, info: {traceback.format_exc()}')

    def get_finish_time(self, id):
        try:
            status, res1, _ = self.db.exec(f'select submit_time from results where id = {id}')
            if status != None:
                logger.error(f'Errir selecting results for id {id}, info: {status}')
                raise Exception(f'Error selecting results for id {id}, info: {status}')
            if len(res1) == 0:
                logger.error(f'Connot find results for id {id}, info: {status}')
                raise Exception(f'Connot find results for id {id}, info: {status}')
            submit_time = res1[0][0]
            end_time = datetime.strptime(submit_time, '%Y-%m-%d %H:%M:%S')
            status, res2, _ = self.db.exec(f'select create_time from user where id = {id}')
            if status != None:
                logger.error(f'Connot find user info for id {id}, info: {status}')
                raise Exception(f'Connot find user info for id {id}, info: {status}')
            (create_time) = res2[0]
            start_time = datetime.strptime(create_time[0], '%Y-%m-%d %H:%M:%S')
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
