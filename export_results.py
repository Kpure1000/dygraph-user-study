import traceback
from logger import getLogger
from datetime import datetime
import json
from database import Database

logger = getLogger("exporter")

def get_finished_users(db):
    try:
        status, res, _ = db.exec('select id from results where is_saved = 1')
        if status != None:
            logger.error(f'Error selecting finished users, info: {status}')
            raise Exception(f'Error selecting finished users, info: {status}')
        return [user[0] for user in res]
    except Exception as e:
        logger.error(f'Error getting finished users: {traceback.format_exc()}')
        raise e

def export_results(db, id):
    try:
        status, res1, _ = db.exec(f'select result, submit_time, is_saved from results where id = {id}')
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
        status, res2, _ = db.exec(f'select name, gender, age, create_time from user where id = {id}')
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
        logger.info(f'Saving results for id {id}, results: {final_result}')
        with open(f'results/result-{id}.json', 'w', encoding='utf-8') as f:
            json.dump(obj=final_result, fp=f, indent=4, ensure_ascii=False)
        logger.info(f'Exported results for id {id} successfully')
        return True
    except Exception as e:
        logger.error(f'Error exporting results for id {id}, info: {traceback.format_exc()}')
        return False

if __name__ == '__main__':
    db = Database("user-study.sqlite3")

    uids = get_finished_users(db)

    logger.info(f'Finished users: {uids}')

    logger.info(f'Exporting results for {len(uids)} users.')

    count = 0

    for uid in uids:
        if export_results(db, uid):
            count += 1

    logger.info(f'Results exported finished: {count} success, {len(uids) - count} failed.')
