import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
# Assumindo que você está usando mysqlclient. Se usar PyMySQL, o erro seria pymysql.IntegrityError
from MySQLdb import IntegrityError
from todo_app.db import get_db

# O Blueprint continua o mesmo
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    View para registro de novos usuários, adaptada para MySQL.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Nota: get_db() agora retorna um cursor para o MySQL
        conn, cursor = get_db()
        # A conexão está armazenada em g.db
        # conn = g.db
        error = None

        if not username:
            error = 'Nome de usuário é obrigatório.'
        elif not password:
            error = 'Senha é obrigatória.'

        if error is None:
            try:
                # MUDANÇA: Placeholders de '?' para '%s' e tabela 'user' entre crases.
                cursor.execute(
                    "INSERT INTO `user` (`username`, `password`) VALUES (%s, %s)",
                    (username, generate_password_hash(password)),
                )
                # MUDANÇA: Commit é chamado na conexão, não no cursor/db.
                conn.commit()
            # MUDANÇA: Exceção específica do conector MySQL.
            except IntegrityError:
                error = f"Usuário {username} já está registrado."
            else:
                flash("Registro bem-sucedido! Por favor, faça o login.")
                return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    View para login de usuários, adaptada para MySQL.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn, cursor = get_db()
        error = None
        
        # MUDANÇA: Placeholders de '?' para '%s' e tabela 'user' entre crases.
        cursor.execute(
            'SELECT * FROM `user` WHERE `username` = %s', (username,)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # MUDANÇA: Redireciona para a página das listas de tarefas, que é a página inicial da app logada.
            #return redirect(url_for('todolist.index'))
            return redirect(url_for('todo.index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    """
    Carrega o usuário logado antes de cada requisição, adaptado para MySQL.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn, cursor = get_db()
        # MUDANÇA: Placeholders de '?' para '%s' e tabela 'user' entre crases.
        cursor.execute(
            'SELECT * FROM `user` WHERE `id` = %s', (user_id,)
        )
        g.user = cursor.fetchone()

@bp.route('/logout')
def logout():
    """
    View para logout do usuário.
    """
    session.clear()
    flash("Você foi desconectado.")
    # MUDANÇA: Redireciona para a página de login após o logout.
    return redirect(url_for('auth.login'))

def login_required(view):
    """
    Decorador que exige que um usuário esteja logado. Nenhuma mudança necessária aqui.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
