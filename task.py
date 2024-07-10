import os.path
import glob
import json
import traceback
from utils import logger
from database import Database

task1_name = "task1"
task2_name = "task2"

class Task:
    def __init__(self, name):
        root_path = f"data/{name}"
        method_folders = glob.glob(root_path + "/*")
        self.tasks = {}
        for m in method_folders:
            method = os.path.basename(m)
            self.tasks[method] = {}
            for d in glob.glob(m+"/*"):
                dataset = os.path.splitext(os.path.basename(d))[0]
                with open(d) as f:
                    self.tasks[method][dataset] = json.load(f)

    def get_data_list(self):
        data_list = []

        for method in self.tasks:
            for dataset in self.tasks[method]:
                data_list.append({
                    "method": method,
                    "dataset": dataset,
                })

        return data_list
    
    def get_data(self, method, dataset):
        return self.tasks[method][dataset]


class Task1(Task):
    def __init__(self):
        super().__init__("node")

class Task2(Task):
    def __init__(self):
        super().__init__("cluster")


__task1__ = Task1()
__task2__ = Task2()


class TaskManager:
    def __init__(self, db:Database, id:int):
        self.db = db
        self.id = id
        task1_list = __task1__.get_data_list()
        self.__len_task1 = len(task1_list)

        status, res, _ = self.db.exec(f'select task from tasks where id = {id}')
        if status != None:
            logger.error(f"Failed to get task, info: {status}")
            raise Exception(f"Failed to get task, info: {status}")
        if len(res) != 0:
            self.data_list = json.loads(res[0][0])
        else:
            # TODO Latin square
            self.data_list = task1_list + __task2__.get_data_list()
            status, res, _ = self.db.exec(f"insert into tasks (id, task, current) values ({id}, '{json.dumps(self.data_list)}', 0)")    
            if status != None:
                logger.error(f"Failed to insert task, info: {status}")
                raise Exception(f"Failed to insert task, info: {status}")
        
        self.total_len = len(self.data_list)


    def next(self):
        cur = self.current()
        if cur >= self.total_len - 1:
            return False
        cur += 1
        status, res, _ = self.db.exec(f"update tasks set current = {cur} where id = {self.id}")
        if status != None:
            logger.error(f"Failed to update current number, info: {status}")
            traceback.print_exc()
            return False
        return True
    
    def current(self):
        status, res, _ = self.db.exec(f'select current from tasks where id = {self.id}')
        if status != None:
            logger.error(f"Failed to get current number, info: {status}")
            traceback.print_exc()
            return None
        return int(res[0][0])
        
    def current_data(self):
        cur = self.current()
        if cur < self.__len_task1:
            return __task1__.get_data(self.data_list[cur]["method"], self.data_list[cur]["dataset"])
        elif cur < self.total_len:
            return __task2__.get_data(self.data_list[cur]["method"], self.data_list[cur]["dataset"])
        else:
            return None
    
    def current_task(self):
        cur = self.current()
        if cur < self.__len_task1:
            return 1
        else:
            return 2

    def current_task_info(self):
        cur = self.current()
        return self.data_list[cur]["method"], self.data_list[cur]["dataset"]
