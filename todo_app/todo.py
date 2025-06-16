from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from todo_app.auth import login_required
from todo_app.db import get_db

bp = Blueprint('todo', __name__)

def get_todo_list(list_id, check_author=True):
    conn, cursor = get_db()
    cursor.execute(
        'SELECT tl.id, title, created, author_id, username '
        'FROM todo_list tl JOIN user u ON tl.author_id = u.id '
        'WHERE tl.id = %s',
        (list_id,)
    )
    todo_list = cursor.fetchone()

    if todo_list is None:
        abort(404, f"Lista de tarefas com id {list_id} não encontrada.")

    if check_author and todo_list['author_id'] != g.user['id']:
        abort(403, "Você não tem permissão para acessar esta lista de tarefas.")

    return todo_list

def get_task(task_id, list_id, check_author=True):
    conn, cursor = get_db()
    cursor.execute(
        'SELECT t.id, description, completed, t.created, list_id, tl.author_id '
        'FROM task t JOIN todo_list tl ON t.list_id = tl.id '
        'WHERE t.id = %s AND t.list_id = %s',
        (task_id, list_id)
    )
    task = cursor.fetchone()

    if task is None:
        abort(404, f"Tarefa com id {task_id} na lista {list_id} não encontrada.")

    if check_author and task['author_id'] != g.user['id']:
        abort(403, "Você não tem permissão para acessar esta tarefa.")

    return task

@bp.route('/')
def index():
    conn, cursor = get_db()
    cursor.execute(
        'SELECT tl.id, title, created, author_id, username '
        'FROM todo_list tl JOIN user u ON tl.author_id = u.id '
        'WHERE tl.author_id = %s '
        'ORDER BY created DESC',
        (g.user['id'],) if g.user else (-1,)
    )
    todo_lists = cursor.fetchall()
    return render_template('todo/index.html', todo_lists=todo_lists)

@bp.route('/create_list', methods=('GET', 'POST'))
@login_required
def create_list():
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'O título da lista é obrigatório.'

        if error:
            flash(error)
        else:
            conn, cursor = get_db()
            cursor.execute(
                'INSERT INTO todo_list (title, author_id) VALUES (%s, %s)',
                (title, g.user['id'])
            )
            conn.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create_list.html')

@bp.route('/<int:list_id>/update_list', methods=('GET', 'POST'))
@login_required
def update_list(list_id):
    todo_list = get_todo_list(list_id)

    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'O título da lista é obrigatório.'

        if error:
            flash(error)
        else:
            conn, cursor = get_db()
            cursor.execute(
                'UPDATE todo_list SET title = %s WHERE id = %s',
                (title, list_id)
            )
            conn.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update_list.html', todo_list=todo_list)

@bp.route('/<int:list_id>/delete_list', methods=('POST',))
@login_required
def delete_list(list_id):
    get_todo_list(list_id)
    conn, cursor = get_db()
    cursor.execute('DELETE FROM todo_list WHERE id = %s', (list_id,))
    conn.commit()
    return redirect(url_for('todo.index'))

@bp.route('/<int:list_id>/tasks')
@login_required
def tasks(list_id):
    todo_list = get_todo_list(list_id)
    conn, cursor = get_db()
    cursor.execute(
        'SELECT id, description, completed, created '
        'FROM task '
        'WHERE list_id = %s '
        'ORDER BY created ASC',
        (list_id,)
    )
    tasks = cursor.fetchall()
    return render_template('todo/tasks.html', todo_list=todo_list, tasks=tasks)

@bp.route('/<int:list_id>/create_task', methods=('GET', 'POST'))
@login_required
def create_task(list_id):
    todo_list = get_todo_list(list_id)

    if request.method == 'POST':
        description = request.form['description']
        error = None

        if not description:
            error = 'A descrição da tarefa é obrigatória.'

        if error:
            flash(error)
        else:
            conn, cursor = get_db()
            cursor.execute(
                'INSERT INTO task (list_id, description) VALUES (%s, %s)',
                (list_id, description)
            )
            conn.commit()
            return redirect(url_for('todo.tasks', list_id=list_id))

    return render_template('todo/create_tasks.html', todo_list=todo_list)

@bp.route('/<int:list_id>/<int:task_id>/update_task', methods=('GET', 'POST'))
@login_required
def update_task(list_id, task_id):
    task = get_task(task_id, list_id)

    if request.method == 'POST':
        description = request.form['description']
        completed = 'completed' in request.form
        error = None

        if not description:
            error = 'A descrição da tarefa é obrigatória.'

        if error:
            flash(error)
        else:
            conn, cursor = get_db()
            cursor.execute(
                'UPDATE task SET description = %s, completed = %s WHERE id = %s',
                (description, 1 if completed else 0, task_id)
            )
            conn.commit()
            return redirect(url_for('todo.tasks', list_id=list_id))

    return render_template('todo/update_task.html', todo_list=get_todo_list(list_id, check_author=False), task=task)

@bp.route('/<int:list_id>/<int:task_id>/toggle_task', methods=('POST',))
@login_required
def toggle_task(list_id, task_id):
    task = get_task(task_id, list_id)
    conn, cursor = get_db()
    new_status = 0 if task['completed'] else 1
    cursor.execute(
        'UPDATE task SET completed = %s WHERE id = %s',
        (new_status, task_id)
    )
    conn.commit()
    return redirect(url_for('todo.tasks', list_id=list_id))

@bp.route('/<int:list_id>/<int:task_id>/delete_task', methods=('POST',))
@login_required
def delete_task(list_id, task_id):
    get_task(task_id, list_id)
    conn, cursor = get_db()
    cursor.execute('DELETE FROM task WHERE id = %s', (task_id,))
    conn.commit()
    return redirect(url_for('todo.tasks', list_id=list_id))
