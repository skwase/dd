-- Создание таблиц
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    full_name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'new',
    priority VARCHAR(20) DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    assignee_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Вставка начальных данных
INSERT INTO categories (name, description) VALUES 
    ('Электрика', 'Проблемы с электричеством, освещением'),
    ('Сантехника', 'Водоснабжение, канализация'),
    ('Мебель', 'Ремонт и замена мебели'),
    ('IT оборудование', 'Компьютеры, принтеры, сеть'),
    ('Уборка', 'Клининговые услуги');

-- Создание пользователей для теста
-- Пароли: admin123 / resp123
INSERT INTO users (username, email, password_hash, role, full_name) VALUES 
    ('admin', 'admin@system.com', 'scrypt:32768:8:1$MNTscFn6vZmRTduT$30a3535d2efd40923c27e35ec97a39a88ca1a31d053895d79c6f27a35a8e3b99759601e3c7770174b51e3fc960cc74c4c9b11f736c16ea66a4\n11e60fccf4c70d', 'admin', 'Системный администратор');

INSERT INTO users (username, email, password_hash, role, full_name) VALUES 
    ('responsible', 'responsible@system.com', 'scrypt:32768:8:1$KaJW93vaBVmvKMzb$1236b1e3e2da4c5066c40348bd57dcaa70b0d84c6a0e6a36a87eb033bb41ea67c9cce349cb73e5eaf2066a66be7aa0018eb02389b01354903cc359dcd12affa7', 'responsible', 'Ответственный');
