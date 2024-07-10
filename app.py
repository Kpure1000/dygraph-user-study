from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
from database import Database
from utils import logger
from task import TaskManager, task1_name, task2_name
from user import UserManager
from results import ResultsManager

app = Flask(__name__)

db = Database("user-study.sqlite3")

userManager = UserManager(db)
resultsManager = ResultsManager(db)

# 设置静态文件目录
app.static_folder = 'static'

def respond_with_error(message, code):
    return jsonify({
        'error': message,
    }), code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/task')
def task():
    id = int(request.cookies.get('id'))
    if id == None:
        return respond_with_error(str("刷新失败，请退出重新开始作答"), 500)
    taskManager = userManager.get_task_manager(id)
    if taskManager is None:
        return respond_with_error(str("用户记录错误，请退出重新开始作答"), 500)
    if taskManager.current_task() == 1:
        return render_template('task1.html')
    else:
        return render_template('task2.html')

@app.route('/end')
def end():
    id = int(request.cookies.get('id'))
    if id == None:
        return respond_with_error(str("刷新失败，请退出重新开始作答"), 500)
    if not resultsManager.is_saved(id):
        resultsManager.save_results(id)
        resultsManager.export_results(id)
    return render_template('end.html')

@app.route('/start', methods=['POST'])
def start():
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']
    # logger.info(f'name: {name}, gender: {gender}, age: {age}')
    id, status = userManager.add(name, gender, age)
    if status != None:
        return respond_with_error(status, 500)
    resp = make_response(redirect(url_for('task')))
    resp.set_cookie('id', f'{id}', max_age=3600)
    return resp

@app.route('/get-data', methods=['GET'])
def get_data():
    id = int(request.cookies.get('id'))
    if id == None:
        return respond_with_error(str("刷新失败，请退出重新开始作答"), 500)
    taskManager = userManager.get_task_manager(id)
    if taskManager is None:
        return respond_with_error(str("用户记录错误，请退出重新开始作答"), 500)
    cur_num = taskManager.current()
    tot_num = taskManager.total_len
    logger.info(f"current num: {taskManager.current()}")
    data = taskManager.current_data()
    if data == None:
        return respond_with_error(str("已经完成所有任务，请退出系统"), 500)
    return jsonify({
        "uid": id,
        "cur_task": cur_num,
        "total_task": tot_num,
        "data": data
    })

@app.route('/next-task', methods=['POST'])
def next_task():
    id = int(request.cookies.get('id'))
    if id == None:
        return respond_with_error(str("刷新失败，请退出重新开始作答"), 500)
    taskManager = userManager.get_task_manager(id)
    if taskManager is None:
        return respond_with_error(str("用户记录错误，请退出重新开始作答"), 500)
    q1 = str(request.form['answer'])
    q2 = request.form['q2']
    if (q2 == None or q2 == ""):
        q2 = 0
    else:
        q2 = int(q2)

    logger.info(f"q1: {q1}, q2: {q2}")
    
    method, dataset = taskManager.current_task_info()

    if taskManager.current_task() == 1:
        resultsManager.add_result(id, task1_name, { "method": method, "dataset": dataset, "q1": q1, "q2": q2 })
    else:
        resultsManager.add_result(id, task2_name, { "method": method, "dataset": dataset, "q1": q1, "q2": q2 })

    if taskManager.next():
        return redirect(url_for('task'))
    else:
        return redirect(url_for('end'))


if __name__ == '__main__':

    app.run(debug=True, port=18123)

    db.close()
