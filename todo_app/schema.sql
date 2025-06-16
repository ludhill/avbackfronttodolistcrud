SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS todo_list;
DROP TABLE IF EXISTS user;

SET FOREIGN_KEY_CHECKS=1;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    INDEX idx_username(username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE todo_list (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_id INT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    list_id INT NOT NULL,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES todo_list(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -- o de cima funcona para o MySql
-- errado
-- SET FOREIGN_KEY_CHECKS=0

-- -- Remove as tabelas existentes se elas já existirem
-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS todo_list;
-- DROP TABLE IF EXISTS task;

-- SET FOREIGN_KEY_CHECKS=1

-- -- Cria a tabela de usuários
-- CREATE TABLE `user` (
--     `id` INT AUTO_INCREMENT PRIMARY KEY,
--     `username` VARCHAR(80) UNIQUE NOT NULL,
--     password VARCHAR(255) NOT NULL,
--     INDEX `idx_username`(`username`) 
-- )ENGINE=InnoDB DDEFAULT CHARSET=utf8mb4
-- ;
 
-- -- Cria a tabela de listas de tarefas
-- CREATE TABLE `todo_list` (
--     `id` INT AUTO_INCREMENT PRIMARY KEY,
--     `user_id` INTEGER NOT NULL,
--     `name` VARCHAR(255) NOT NULL,
--     `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE 
-- )ENGINE=InnoDB DDEFAULT CHARSET=utf8mb4
-- ;

-- -- Cria a tabela de tarefas
-- CREATE TABLE task (
--     `id` INT AUTO_INCREMENT PRIMARY KEY,
--     `todolist_id` INTEGER NOT NULL,
--     `description` TEXT NOT NULL,
--     `completed` BOOLEAN NOT NULL DEFAULT 0, -- 0 para falso, 1 para verdadeiro
--     `due_date` TIMESTAMP NULL DEFAULT NULL,
--     `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (`todolist_id`) REFERENCES `todo_list` (`id`) ON DELETE CASCADE
-- )ENGINE=InnoDB DDEFAULT CHARSET=utf8mb4
-- ;
