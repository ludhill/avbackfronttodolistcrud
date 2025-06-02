import sqlite3
import click
from flask import current_app, g
from datetime import datetime

def get_db():
    """
    Retorna uma conexão com o banco de dados.
    A conexão é armazenada no objeto 'g' para ser reutilizada durante a mesma requisição.
    """
    if 'db' not in g:
        # Conecta ao banco de dados especificado na configuração da aplicação
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES # Permite que o SQLite detecte tipos de dados
        )
        # Configura as linhas retornadas para se comportarem como dicionários
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Fecha a conexão com o banco de dados se ela existir.
    Esta função é registrada para ser chamada automaticamente após cada requisição.
    """
    db = g.pop('db', None) # Remove a conexão do objeto 'g'

    if db is not None:
        db.close()

def init_db():
    """
    Inicializa o banco de dados executando o script SQL de esquema.
    """
    db = get_db()
    # Abre o arquivo schema.sql relativo ao pacote todo_app
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8')) # Executa os comandos SQL

# Registra um conversor para timestamps para que sejam lidos como objetos datetime
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

@click.command('init-db')
def init_db_command():
    """
    Comando de linha de comando para limpar os dados existentes e criar novas tabelas.
    Executável com 'flask init-db'.
    """
    init_db()
    click.echo('Banco de dados inicializado.')

def init_app(app):
    """
    Registra as funções de banco de dados com a aplicação Flask.
    """
    app.teardown_appcontext(close_db) # Garante que close_db seja chamado após cada requisição
    app.cli.add_command(init_db_command) # Adiciona o comando 'init-db' à CLI do Flask
