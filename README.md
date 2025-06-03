# avaliação backfront to-do-list + crud
Aplicativo para validar a primeira avaliação de (back end para front end) em Flask com python, todolist com crud

#### # Testar manualmente 

1 - Clonar repositorio
`bash: git clone  https://github.com/ludhill/avbackfronttodolistcrud.git`
2 - instalar o venv
 `cmd: python3 -m venv .venv`

3 - Ativar o ambiente virtual source 

venv/bin/activate # Linux/macOS 
` venv:: .venv\Scripts\activate # Windows`

4 - Inicializar o banco de dados 
` venv: flask --app todo_app init-db`

5 - Executar a aplicação 
`venv: flask --app todo_app run --debug`

6 - Testar manualmente Acesse as rotas principais da aplicação no navegador:

/auth/register → Teste o cadastro de usuários.

/auth/login → Teste o login.

/todo/create → Teste a criação de tarefas.

/todo/ → Veja se as tarefas.

7 - Testar automaticamente 
`venv: pip install pytest pytest`
