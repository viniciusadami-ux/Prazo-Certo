PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS atividade;
DROP TABLE IF EXISTS disciplina;
DROP TABLE IF EXISTS usuario;
PRAGMA foreign_keys = ON;

CREATE TABLE usuario(
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    nome TEXT(100) NOT NULL,
    email TEXT(150) UNIQUE NOT NULL COLLATE NOCASE,
    senha_hash TEXT(255) NOT NULL, 
    data_cadastro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE disciplina(
    id_disciplina INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    nome TEXT(100) NOT NULL,
    professor TEXT(100),
    id_usuario INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE atividade(
    id_atividade INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    titulo TEXT(150) NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('prova', 'trabalho')),
    descricao TEXT,
    data_prazo TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN ('pendente', 'concluida')),
    id_disciplina INTEGER NOT NULL,
    FOREIGN KEY (id_disciplina) REFERENCES disciplina(id_disciplina) ON DELETE CASCADE  
);