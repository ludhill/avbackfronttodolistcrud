from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from todo_app.auth import login_required
from todo_app.db import get_db

# Cria um Blueprint para as funcionalidades de lista de tarefas
bp = Blueprint('todo', __name__)

def get_todo_list(list_id, check_author=True):
    """
    Obtém uma lista de tarefas pelo ID e, opcionalmente, verifica o autor.
    Aborta com 404 se a lista não existir, ou 403 se o usuário não for o autor.
    """
    todo_list = get_db().execute(
        'SELECT tl.id, title, created, author_id, username'
        ' FROM todo_list tl JOIN user u ON tl.author_id = u.id'
        ' WHERE tl.id = ?',
        (list_id,)
    ).fetchone()

    if todo_list is None:
        abort(404, f"Lista de tarefas com id {list_id} não encontrada.")

    if check_author and todo_list['author_id'] != g.user['id']:
        abort(403, "Você não tem permissão para acessar esta lista de tarefas.")

    return todo_list

def get_task(task_id, list_id, check_author=True):
    """
    Obtém uma tarefa pelo ID e ID da lista, e opcionalmente, verifica o autor da lista.
    Aborta com 404 se a tarefa não existir, ou 403 se o usuário não for o autor da lista.
    """
    task = get_db().execute(
        'SELECT t.id, description, completed, t.created, list_id, tl.author_id'
        ' FROM task t JOIN todo_list tl ON t.list_id = tl.id'
        ' WHERE t.id = ? AND t.list_id = ?',
        (task_id, list_id)
    ).fetchone()

    if task is None:
        abort(404, f"Tarefa com id {task_id} na lista {list_id} não encontrada.")

    if check_author:
        # Verifica se o autor da lista à qual a tarefa pertence é o usuário logado
        if task['author_id'] != g.user['id']:
            abort(403, "Você não tem permissão para acessar esta tarefa.")

    return task

@bp.route('/')
def index():
    """
    Exibe todas as listas de tarefas do usuário logado.
    """
    db = get_db()
    # Busca todas as listas de tarefas do usuário logado, ordenadas pela mais recente
    todo_lists = db.execute(
        'SELECT tl.id, title, created, author_id, username'
        ' FROM todo_list tl JOIN user u ON tl.author_id = u.id'
        ' WHERE tl.author_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],) if g.user else (-1,) # Retorna vazio se não houver usuário logado
    ).fetchall()
    return render_template('todo/index.html', todo_lists=todo_lists)

@bp.route('/create_list', methods=('GET', 'POST'))
@login_required # Exige autenticação para criar uma lista
def create_list():
    """
    Cria uma nova lista de tarefas.
    """
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'O título da lista é obrigatório.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO todo_list (title, author_id) VALUES (?, ?)',
                (title, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index')) # Redireciona para a página principal após a criação

    return render_template('todo/create_list.html')

@bp.route('/<int:list_id>/update_list', methods=('GET', 'POST'))
@login_required # Exige autenticação para atualizar uma lista
def update_list(list_id):
    """
    Atualiza uma lista de tarefas existente.
    """
    todo_list = get_todo_list(list_id) # Obtém a lista e verifica o autor

    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'O título da lista é obrigatório.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE todo_list SET title = ? WHERE id = ?',
                (title, list_id)
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update_list.html', todo_list=todo_list)

@bp.route('/<int:list_id>/delete_list', methods=('POST',))
@login_required # Exige autenticação para deletar uma lista
def delete_list(list_id):
    """
    Deleta uma lista de tarefas.
    """
    get_todo_list(list_id) # Obtém a lista e verifica o autor
    db = get_db()
    db.execute('DELETE FROM todo_list WHERE id = ?', (list_id,))
    db.commit()
    return redirect(url_for('todo.index'))

@bp.route('/<int:list_id>/tasks')
@login_required # Exige autenticação para ver as tarefas de uma lista
def tasks(list_id):
    """
    Exibe as tarefas de uma lista de tarefas específica.
    """
    todo_list = get_todo_list(list_id) # Obtém a lista e verifica o autor
    db = get_db()
    tasks = db.execute(
        'SELECT id, description, completed, created'
        ' FROM task'
        ' WHERE list_id = ?'
        ' ORDER BY created ASC',
        (list_id,)
    ).fetchall()
    return render_template('todo/tasks.html', todo_list=todo_list, tasks=tasks)

@bp.route('/<int:list_id>/create_task', methods=('GET', 'POST'))
@login_required # Exige autenticação para criar uma tarefa
def create_task(list_id):
    """
    Cria uma nova tarefa para uma lista de tarefas específica.
    """
    todo_list = get_todo_list(list_id) # Garante que a lista existe e o usuário é o autor

    if request.method == 'POST':
        description = request.form['description']
        error = None

        if not description:
            error = 'A descrição da tarefa é obrigatória.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (list_id, description) VALUES (?, ?)',
                (list_id, description)
            )
            db.commit()
            return redirect(url_for('todo.tasks', list_id=list_id))

    return render_template('todo/create_tasks.html', todo_list=todo_list)

@bp.route('/<int:list_id>/<int:task_id>/update_task', methods=('GET', 'POST'))
@login_required # Exige autenticação para atualizar uma tarefa
def update_task(list_id, task_id):
    """
    Atualiza uma tarefa existente.
    """
    task = get_task(task_id, list_id) # Obtém a tarefa e verifica o autor da lista

    if request.method == 'POST':
        description = request.form['description']
        completed = 'completed' in request.form # Verifica se o checkbox foi marcado
        error = None

        if not description:
            error = 'A descrição da tarefa é obrigatória.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET description = ?, completed = ? WHERE id = ?',
                (description, 1 if completed else 0, task_id)
            )
            db.commit()
            return redirect(url_for('todo.tasks', list_id=list_id))

    return render_template('todo/update_task.html', todo_list=get_todo_list(list_id, check_author=False), task=task)

@bp.route('/<int:list_id>/<int:task_id>/toggle_task', methods=('POST',))
@login_required # Exige autenticação para alternar o status da tarefa
def toggle_task(list_id, task_id):
    """
    Alterna o status de conclusão de uma tarefa (concluída/não concluída).
    """
    task = get_task(task_id, list_id) # Obtém a tarefa e verifica o autor da lista
    db = get_db()
    new_status = 0 if task['completed'] else 1 # Inverte o status
    db.execute(
        'UPDATE task SET completed = ? WHERE id = ?',
        (new_status, task_id)
    )
    db.commit()
    return redirect(url_for('todo.tasks', list_id=list_id))

@bp.route('/<int:list_id>/<int:task_id>/delete_task', methods=('POST',))
@login_required # Exige autenticação para deletar uma tarefa
def delete_task(list_id, task_id):
    """
    Deleta uma tarefa.
    """
    get_task(task_id, list_id) # Obtém a tarefa e verifica o autor da lista
    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (task_id,))
    db.commit()
    return redirect(url_for('todo.tasks', list_id=list_id))
