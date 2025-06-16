import MySQLdb
import MySQLdb.cursors
import click
from flask import current_app, g
from urllib.parse import urlparse

def get_db_params_from_url(db_url):
    """Analisa a DATABASE_URL e retorna um dicionário de parâmetros de conexão."""
    if not db_url:
        raise ValueError("DATABASE_URL não está configurada.")
        
    url = urlparse(db_url)
    return {
        'host': url.hostname or 'localhost',
        'port': url.port or 3306,
        'user': url.username, # Deixa como None se não existir
        'password': url.password, # Deixa como None se não existir
        'database': url.path[1:] if url.path else None, # Remove o '/' inicial
    }

def get_db():
    if 'db' not in g:
        db_params = get_db_params_from_url(current_app.config['DATABASE_URL'])

        if not db_params.get('user') or not db_params.get('database'):
            raise ValueError("Usuário ou nome do banco de dados ausente na DATABASE_URL.")

        g.db = MySQLdb.connect(
            host=db_params['host'],
            user=db_params['user'],
            passwd=db_params['password'] or '',
            db=db_params['database'],
            port=db_params['port'],
            cursorclass=MySQLdb.cursors.DictCursor
        )
        g.cursor = g.db.cursor()

    return g.db, g.cursor


def close_db(e=None):
    """Fecha a conexão com o banco de dados MySQL."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Cria novas tabelas (adaptado para MySQL)."""
    db_params = get_db_params_from_url(current_app.config['DATABASE_URL'])
    
    # Conexão separada para inicialização para não interferir com o contexto 'g'
    conn = MySQLdb.connect(
        host=db_params['host'],
        user=db_params['user'],
        passwd=db_params['password'] or '',
        db=db_params['database'],
        port=db_params['port']
    )
    cur = conn.cursor()
    with current_app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')
        for statement in sql_script.split(';'):
            if statement.strip():
                cur.execute(statement)
    conn.commit()
    cur.close()
    conn.close()

@click.command('init-db')
def init_db_command():
    """Comando para limpar dados existentes e criar novas tabelas."""
    try:
        init_db()
        click.echo('Banco de dados MySQL inicializado com sucesso.')
    except Exception as e:
        click.echo(f'Ocorreu um erro ao inicializar o banco de dados: {e}', err=True)


def init_app(app):
    """Registra funções relacionadas ao banco de dados com a instância da aplicação Flask."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)