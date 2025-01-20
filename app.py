import json
import traceback
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
from database import Database
from utils import logger
from task import TaskManager, task1_name, task2_name
from user import UserManager

app = Flask(__name__)

db = Database("user-study.sqlite3")

userManager = UserManager(db)

# 设置静态文件目录
app.static_folder = 'static'

def respond_with_error(message, code):
    return jsonify({
        'error': message,
    }), code

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/oops', methods=['GET'])
def oops():
    return render_template('oops.html')

@app.route('/end')
def end():
    try:
        id = request.cookies.get('id')
        if id == None:
            return redirect(url_for('oops', error="NO_COOKIE_ID"))
        return render_template('end.html')
    except Exception as e:
        logger.error(f"User '{id}' end error")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))

@app.route('/task')
def task():
    try:
        id = request.cookies.get('id')
        if id == None:
            return redirect(url_for('oops', error="NO_COOKIE_ID"))
        id = int(id)
        taskManager = userManager.get_task_manager(id)
        if taskManager is None:
            return redirect(url_for('oops', error="TASK_ERROR"))
        if taskManager.current_task_type() == 1:
            return render_template('task1.html')
        else:
            return render_template('task2.html')
    except Exception as e:
        logger.error(f"User '{id}' task error")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))

@app.route('/start', methods=['POST'])
def start():
    try:
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        id, status = userManager.add(name, gender, age)
        if status != None:
            return respond_with_error(status, 500)
        resp = make_response(redirect(url_for('task')))
        resp.set_cookie('id', f'{id}', max_age=240 * 60) # 限制完成时间为240分钟，过时将清除cookie
        return resp
    except Exception as e:
        logger.error("start error")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))

@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        id = request.cookies.get('id')
        if id == None:
            return redirect(url_for('oops', error="NO_COOKIE_ID"))
        id = int(id)
        taskManager = userManager.get_task_manager(id)
        if taskManager is None:
            return redirect(url_for('oops', error="TASK_ERROR"))
        cur_num = taskManager.current_task_idx()
        method, dataset = taskManager.current_task_info()
        logger.info(f"User '{id}', current task '{method}-{dataset}', {cur_num + 1}/{taskManager.total_len}")
        data = taskManager.current_data()
        if data == None:
            logger.info(f"User '{id}' back to task page after all tasks done.")
            return respond_with_error(str("已经完成所有任务，请退出系统"), 500)
        return jsonify({
            "uid": id,
            "cur_task": cur_num,
            "cur_method": method,
            "task_type": taskManager.current_task_type(),
            "data": data
        })
    except Exception as e:
        logger.error(f"User '{id}' get_data error")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))

@app.route('/start-task', methods=['GET'])
def start_task():
    try:
        id = request.cookies.get('id')
        if id == None:
            return redirect(url_for('oops', error="NO_COOKIE_ID"))
        id = int(id)
        taskManager = userManager.get_task_manager(id)
        if taskManager is None:
            return redirect(url_for('oops', error="TASK_ERROR"))
        # record start time only for first request
        taskManager.start_task()
        return redirect(url_for('get_data'))
    except Exception as e:
        logger.error(f"User '{id}' start_task error")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))

@app.route('/get-endinfo', methods=['GET'])
def get_endinfo():
    try:
        id = request.cookies.get('id')
        if id == None:
            return redirect(url_for('oops', error="NO_COOKIE_ID"))
        id = int(id)
        finish_time = userManager.resultsManager.get_finish_time(id)
        if finish_time == None:
            return respond_with_error(str("获取时间完成错误"), 500)
        finished_count = len(userManager.resultsManager.get_finished_users())
        return jsonify({
            "finish_time": finish_time,
            "finished_users_count": finished_count
        })
    except Exception as e:
        logger.error(f"User '{id}' get_totaltime error")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))

@app.route('/next-task', methods=['POST'])
def next_task():
    try:
        id = request.cookies.get('id')
        if id == None:
            return redirect(url_for('oops', error="NO_COOKIE_ID"))
        id = int(id)

        taskManager = userManager.get_task_manager(id)
        if taskManager is None:
            return redirect(url_for('oops', error="TASK_ERROR"))

        method, dataset = taskManager.current_task_info()
        finish_time = taskManager.end_task()


        if taskManager.current_task_type() == 1:
            top1 = int(request.form['top1-answer'])
            top2 = int(request.form['top2-answer'])
            top3 = int(request.form['top3-answer'])
            q1 = [top1, top2, top3]
            q2=None
        elif taskManager.current_task_type() == 2:
            q1 = str(request.form['answer'])
            q2 = request.form['q2']
            q2 = float(q2) if q2 != None and q2 != "" else 0

        new_result = { "method": method, "dataset": dataset, "q1": q1, "q2": q2, "finish_time": finish_time }

        is_final = taskManager.is_final_task()

        if taskManager.current_task_type() == 1:
            userManager.resultsManager.add_result(id, task1_name, new_result, is_final)
        else:
            userManager.resultsManager.add_result(id, task2_name, new_result, is_final)

        if taskManager.next():
            return redirect(url_for('task'))
        else:
            return redirect(url_for('end'))

    except Exception as e:
        logger.error(f"Error in next_task: {e}")
        traceback.print_exc()
        return redirect(url_for('oops', error=str(e)))


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0',port=18321)

    db.close()
