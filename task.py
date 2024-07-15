import os.path
import glob
import json
import random
import time
import traceback
from utils import logger
from database import Database
from rls import random_latin_square

task1_name = "node"
task2_name = "cluster"

class Task:
    def __init__(self, name):
        try:
            self.rng = random.Random()
            self.rng.seed(time.time())
            root_path = f"data/{name}"
            method_folders = glob.glob(root_path + "/*")
            self.tasks = {}
            if len(method_folders) != 4:
                raise Exception(f"Task '{name}' init failed, method number is {len(method_folders)}, instead of 4")
            for m in method_folders:
                method = os.path.basename(m)
                self.tasks[method] = {}
                datasets = glob.glob(m + "/*.json")
                if len(datasets) != 4:
                    raise Exception(f"Task '{name}' init failed, dataset number is {len(datasets)}, instead of 4")
                for d in datasets:
                    dataset = os.path.splitext(os.path.basename(d))[0]
                    with open(d) as f:
                        self.tasks[method][dataset] = json.load(f)

            self.__latin_square__ = [
                0, 1+4, 2+8, 3+12,
                1, 2+4, 3+8, 0+12,
                2, 3+4, 0+8, 1+12,
                3, 0+4, 1+8, 2+12
            ]

            data_list = []

            for method in self.tasks:
                for dataset in self.tasks[method]:
                    data_list.append({
                        "method": method,
                        "dataset": dataset,
                    })

            self.data_list = [data_list[i] for i in self.__latin_square__]

            logger.info(f"Task '{name}' init with data list: \n{self.data_list}")

            logger.info(f"Task '{name}' init successful.")

        except Exception as e:
            logger.error(f"Failed to init task '{name}', info: {traceback.format_exc()}")
            raise e

    def get_data_list(self):
        return self.data_list
    
    def get_data(self, method, dataset):
        return self.tasks[method][dataset]

    def get_random_data_list(self):
        data_list = []

        for method in self.tasks:
            for dataset in self.tasks[method]:
                data_list.append({
                    "method": method,
                    "dataset": dataset,
                })

        self.rng.shuffle(data_list)

        return data_list
    

class Task1(Task):
    def __init__(self):
        super().__init__(task1_name)

class Task2(Task):
    def __init__(self):
        super().__init__(task2_name)


__task1__ = Task1()
__task2__ = Task2()


class TaskManager:
    def __init__(self, db:Database, id:int):

        try:
            self.db = db
            self.id = id

            task1_list = __task1__.get_data_list()
            task2_list = __task2__.get_data_list()

            self.__len_task1 = len(task1_list)
            self.__len_task2 = len(task2_list)

            self.total_len = self.__len_task1 + self.__len_task2
            self.__cur_idx__ = 0
            self.data_list = []

            # find if exist
            status, res, _ = self.db.exec(f'select task, current from tasks where id = {id}')
            if status != None:
                logger.error(f"Failed to get task for {self.id}, info: {status}")
                raise Exception(f"Failed to get task for {self.id}, info: {status}")
            if len(res) != 0: # exist
                # load
                self.data_list = json.loads(res[0][0])
                self.__cur_idx__ = res[0][1]
                logger.info(f"Task schedule for {self.id} exist, load from db. Current task index: {self.__cur_idx__}. List: \n{self.data_list}")
            else: # not exist
                self.data_list = task1_list + task2_list
                logger.info(f"Task schedule for {self.id} not exist, create new: \n Task1: {task1_list}\n  Task2: {task2_list}")
                # save
                status, res, _ = self.db.exec(f"insert into tasks (id, task, current) values ({id}, '{json.dumps(self.data_list)}', {self.__cur_idx__})")    
                if status != None:
                    logger.error(f"Failed to insert task, info: {status}")
                    raise Exception(f"Failed to insert task, info: {status}")
                logger.info(f"Task schedule for {self.id} saved")
                
        except Exception as e:
            logger.error(f"Failed to init task manager for {self.id}, info: {e}")
            raise Exception(f"Failed to init task manager for {self.id}, info: {traceback.format_exc()}")
        
    def current_task_idx(self):
        try:
            status, res, _ = self.db.exec(f'select current from tasks where id = {self.id}')
            if status != None:
                logger.error(f"Failed to get current number for {self.id}, info: {status}")
                traceback.print_exc()
                return None
            if len(res) == 0:
                logger.error(f"Failed to get current number for {self.id}")
                raise Exception(f"Failed to get current number for {self.id}")
            self.__cur_idx__ = int(res[0][0])
            return self.__cur_idx__
        except Exception as e:
            logger.error(f"Failed to get current number for {self.id}, info: {traceback.format_exc()}")
            raise Exception(f"Failed to get current number for {self.id}, info: {traceback.format_exc()}")
        
    def is_final_task(self):
        try:
            return self.__cur_idx__ == self.total_len - 1
        except Exception as e:
            logger.error(f"Failed to check final task for {self.id}, info: {traceback.format_exc()}")
            raise Exception(f"Failed to check final task for {self.id}, info: {traceback.format_exc()}")

    def next(self):
        try:
            if self.__cur_idx__ >= self.total_len - 1:
                return False
            self.__cur_idx__ += 1
            status, _, _ = self.db.exec(f"update tasks set current = {self.__cur_idx__} where id = {self.id}")
            if status != None:
                logger.error(f"Failed to update current number, info: {status}")
                traceback.print_exc()
                return False
            
            logger.info(f"Task index for {self.id} updated to {self.__cur_idx__}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to set next task for {self.id}, info: {traceback.format_exc()}")
            raise Exception(f"Failed to set next task for {self.id}, info: {traceback.format_exc()}")
    
    def current_data(self):
        try:
            cur = self.__cur_idx__
            if cur < self.__len_task1:
                return __task1__.get_data(self.data_list[cur]["method"], self.data_list[cur]["dataset"])
            elif cur < self.total_len:
                return __task2__.get_data(self.data_list[cur]["method"], self.data_list[cur]["dataset"])
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to get current data for {self.id}, info: {traceback.format_exc()}")
            raise Exception(f"Failed to get current data for {self.id}, info: {traceback.format_exc()}")
    
    def current_task(self):
        try:
            cur = self.__cur_idx__
            if cur < self.__len_task1:
                return 1
            else:
                return 2
        except Exception as e:
            logger.error(f"Failed to get current task for {self.id}, info: {traceback.format_exc()}")
            raise Exception(f"Failed to get current task for {self.id}, info: {traceback.format_exc()}")

    def current_task_info(self):
        try:
            cur = self.__cur_idx__
            return self.data_list[cur]["method"], self.data_list[cur]["dataset"]
        except Exception as e:
            logger.error(f"Failed to get current task info for {self.id}, info: {traceback.format_exc()}")
            raise Exception(f"Failed to get current task info for {self.id}, info: {traceback.format_exc()}")
