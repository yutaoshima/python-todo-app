import flask
import re
import os
import string
import random
import json
import requests

from datetime import datetime
from random import randint
from todos_store import Store

from rook import auto_start

app = flask.Flask(__name__, static_url_path='/static')

# unsafeRandId generates a random string composed from english upper case letters and digits
# it's called unsafe because it doesn't use a crypto random generator


url = "https://service.eu.apiconnect.ibmcloud.com/gws/apigateway/api/da713fba861ff19ef7cc15e87072dfd6ce556d30c2b0caac7f307ef844741e9a/281a066c-00fc-40a6-b272-0139a590ce7b/rookout"

def unsafeRandId(len):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len))


def cleanStr(str):
    return re.sub(r'[>|<|;|`|&|/|\\]', '', str)


@app.errorhandler(404)
def page_not_found(e):
    return '404 Page Not Found'


@app.errorhandler(500)
def internal_server_error(e):
    return '500 Internal Server Error'


@app.route("/error")
def render_bad_template():
    try:
        invalid_oper = 42 / 0
    except Exception as e:
        print('Operation failed to complete')
    animal_list = ['dog', 'cat', 'turtle', 'fish', 'bird', 'cow', 'sealion']
    time = datetime.now()
    number = 0.01 * randint(10, 200) + 0.1
    return flask.render_template('doesnotexist.html', animal_list=animal_list, time=time, number=number)


# redirect from base url to index.html
@app.route("/")
def index():
    return flask.redirect('/static/index.html')


@app.route('/todos/<todoId>', methods=['DELETE'])
def del_todo(todoId):
    todos = Store.getInstance().todos
    newTodos = [t for t in todos if t['id'] != todoId]
    todos = newTodos
    return ('', 204)


@app.route('/todos/clear_completed', methods=['DELETE'])
def clear_completed():
    todos = Store.getInstance().todos
    todo = [t for t in todos if not t['completed']]
    return ('', 204)


@app.route('/todos', methods=['UPDATE'])
def update_todo():
    todos = Store.getInstance().todos
    req = flask.request
    todo = req.get_json()
    for t in todos:
        if t['id'] == todo['id']:
            t['title'] = todo['title']
            t['completed'] = todo['completed']
            break
    return ('', 204)

# add a new todo action


@app.route('/todos', methods=['POST'])
def add_todo():
    todos = Store.getInstance().todos
    fr = flask.request
    req = fr.get_json()
    todoStr = cleanStr(req['title'])
    if not todoStr:
        return ('', 400)
    todo = {
        "title": cleanStr(req['title']),
        "id": unsafeRandId(10),
        "completed": False
    }
    todos.append(todo)
    return ('', 204)

@app.route('/todos/generate', methods=['POST'])
def generate_todo():

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        }

    response = requests.request("GET", url, headers=headers)


    todos = Store.getInstance().todos
    fr = flask.request
    req = fr.get_json()
    json_data = json.loads(response.text)
    todoStr = json_data['todo']

    todo = {
        "title": todoStr,
        "id": unsafeRandId(10),
        "completed": False
    }
    todos.append(todo)
    return ('', 204)


@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Store.getInstance().todos
    return json.dumps(todos)


@app.route('/todo/dup/<todoId>', methods=['POST'])
def duplicate_todo(todoId):
    todos = Store.getInstance().todos
    for todo in todos:
        if todoId == todo['id']:
            dup = {'title': todo['completed'],
                   'id': unsafeRandId(10),
                   'completed': todo['title']}
            todos.append(dup)
            break
    return ('', 204)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
