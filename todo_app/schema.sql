-- Remove as tabelas existentes se elas já existirem
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS todo_list;
DROP TABLE IF EXISTS task;

-- Cria a tabela de usuários
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Cria a tabela de listas de tarefas
CREATE TABLE todo_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user (id) ON DELETE CASCADE
);

-- Cria a tabela de tarefas
CREATE TABLE task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0, -- 0 para falso, 1 para verdadeiro
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES todo_list (id) ON DELETE CASCADE
);
