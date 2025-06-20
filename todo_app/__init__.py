import os
from flask import Flask

def create_app(test_config=None):
    """
    Cria e configura a instância da aplicação Flask.
    Esta é a função de fábrica da aplicação.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Configurações padrão da aplicação
    app.config.from_mapping(
        SECRET_KEY='dev', # Chave secreta para desenvolvimento, deve ser alterada em produção
        DATABASE=os.path.join(app.instance_path, 'todo_app.sqlite'), # Caminho do arquivo do banco de dados SQLite
    )

    if test_config is None:
        # Carrega a configuração da instância, se existir, quando não estiver testando
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carrega a configuração de teste se for passada
        app.config.from_mapping(test_config)

    # Garante que a pasta da instância exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Uma página simples que diz olá (para testar se a aplicação está funcionando)
    @app.route('/hello')
    def hello():
        return 'Hello, World! This is your To-Do App.'

    # Importa e registra as funções do banco de dados
    from . import db
    db.init_app(app)

    # Importa e registra o blueprint de autenticação (será criado a seguir)
    from . import auth
    app.register_blueprint(auth.bp)

    # Importa e registra o blueprint de listas de tarefas (será criado a seguir)
    from . import todo
    app.register_blueprint(todo.bp)
    app.add_url_rule('/', endpoint='index') # Define a rota raiz para o índice das listas de tarefas

    return app



