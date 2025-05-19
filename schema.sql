-- 删除表（如果已存在）
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS prompt_results;

-- 创建用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 创建Prompt表
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT NOT NULL,  -- 存储为JSON格式的标签数组
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 创建Prompt处理结果表
CREATE TABLE prompt_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    input_data TEXT NOT NULL,
    output_data TEXT NOT NULL,
    execution_time REAL NOT NULL,  -- 执行时间（毫秒）
    success BOOLEAN NOT NULL,      -- 处理是否成功
    error_message TEXT,            -- 如果处理失败，保存错误信息
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts (id)
);

-- 创建索引以提高查询性能
CREATE INDEX idx_prompts_user_id ON prompts(user_id);
CREATE INDEX idx_prompt_results_prompt_id ON prompt_results(prompt_id);
CREATE INDEX idx_prompts_category ON prompts(category);
CREATE INDEX idx_prompt_results_success ON prompt_results(success); 