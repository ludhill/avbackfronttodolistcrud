import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from todo_app.db import get_db

# Cria um Blueprint para autenticação com prefixo de URL '/auth'
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    View para registro de novos usuários.
    Permite GET para exibir o formulário e POST para processar o envio.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Nome de usuário é obrigatório.'
        elif not password:
            error = 'Senha é obrigatória.'

        if error is None:
            try:
                # Insere o novo usuário no banco de dados
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)), # Armazena a senha com hash
                )
                db.commit() # Confirma as alterações no banco de dados
            except db.IntegrityError:
                # Erro se o nome de usuário já existir
                error = f"Usuário {username} já está registrado."
            else:
                # Redireciona para a página de login após o registro bem-sucedido
                return redirect(url_for("auth.login"))
        
        # Exibe a mensagem de erro (se houver)
        flash(error)

    # Renderiza o template de registro
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    View para login de usuários existentes.
    Permite GET para exibir o formulário e POST para processar o envio.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # Busca o usuário pelo nome de usuário
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user['password'], password):
            # Verifica se a senha fornecida corresponde ao hash armazenado
            error = 'Senha incorreta.'

        if error is None:
            # Limpa a sessão anterior e armazena o ID do usuário logado
            session.clear()
            session['user_id'] = user['id']
            # Redireciona para a página principal (índice)
            return redirect(url_for('index'))
        
        # Exibe a mensagem de erro (se houver)
        flash(error)

    # Renderiza o template de login
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    """
    Carrega o usuário logado antes de cada requisição.
    Se um user_id estiver na sessão, carrega os dados do usuário para g.user.
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None # Nenhum usuário logado
    else:
        # Carrega os dados do usuário do banco de dados
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    """
    View para logout do usuário.
    Limpa a sessão e redireciona para a página principal.
    """
    session.clear() # Remove o user_id da sessão
    return redirect(url_for('index'))

def login_required(view):
    """
    Decorador que exige que um usuário esteja logado para acessar a view.
    Se o usuário não estiver logado, redireciona para a página de login.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login')) # Redireciona para login se não houver usuário
        return view(**kwargs) # Chama a view original se o usuário estiver logado
    return wrapped_view
