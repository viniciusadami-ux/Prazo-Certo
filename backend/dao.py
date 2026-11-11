# dao.py — acesso ao SQLite.
# O DAO é o único lugar com SQL; models.py só guarda dados.

import sqlite3
from models import Atividade, Disciplina, Usuario

class DisciplinaDAO:
    def __init__(self, caminho_banco="../database/prazo_certo.db"):
        self.caminho_banco = caminho_banco

    def listar_por_usuario(self, id_usuario):
        # Devolve só as disciplinas do usuário logado.
        # O SELECT lista as colunas na mesma ordem do __init__ de Disciplina:
        # O ? evita SQL injection; (id_usuario,) é a tupla de valores.
        # fetchall() devolve tuplas; Disciplina(*linha) transforma cada uma em objeto.
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "SELECT id_disciplina, id_usuario, nome, professor FROM disciplina WHERE id_usuario = ?",
                (id_usuario,)
            )
            linhas = cursor.fetchall()
            return [Disciplina(*linha) for linha in linhas]

    def inserir(self, disciplina):
        # Insere uma disciplina do usuário dono do objeto.
        # id_disciplina não entra no INSERT: o SQLite gera com AUTOINCREMENT.
        # commit() grava; lastrowid devolve o id gerado.
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "INSERT INTO disciplina (id_usuario, nome, professor) VALUES (?, ?, ?)",
                (disciplina.id_usuario, disciplina.nome, disciplina.professor)
            )
            conexao.commit()
            return cursor.lastrowid

    def atualizar(self, disciplina):
        # Atualiza nome/professor só se a disciplina for do usuário informado.
        # O id_usuario no WHERE impede alterar disciplina de outra conta.
        # rowcount é quantas linhas mudaram; 0 = não existia ou não era do usuário.
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "UPDATE disciplina SET nome = ?, professor = ? WHERE id_disciplina = ? AND id_usuario = ?",
                (disciplina.nome, disciplina.professor, disciplina.id_disciplina, disciplina.id_usuario)
            )
            conexao.commit()
            return cursor.rowcount

    def remover(self, id_disciplina, id_usuario):
        # Remove só se a disciplina for do usuário.
        # rowcount 0 = nada foi removido (não existe ou é de outra conta).
        # O CASCADE das atividades só funciona com o PRAGMA ligado.
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "DELETE FROM disciplina WHERE id_disciplina = ? AND id_usuario = ?",
                (id_disciplina, id_usuario)
            )
            conexao.commit()
            return cursor.rowcount

class AtividadeDAO:
    def __init__(self, caminho_banco="../database/prazo_certo.db"):
        self.caminho_banco = caminho_banco

    def listar_por_usuario(self, id_usuario):
        
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "SELECT id_atividade, id_disciplina, titulo, tipo, descricao, data_prazo, status "
                "FROM atividade WHERE id_disciplina IN "
                "(SELECT id_disciplina FROM disciplina WHERE id_usuario = ?)",
                (id_usuario,)
            )
            linhas = cursor.fetchall()
            return [Atividade(*linha) for linha in linhas]

    def inserir(self, atividade, id_usuario):
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "SELECT 1 FROM disciplina WHERE id_disciplina = ? AND id_usuario = ?",
                (atividade.id_disciplina, id_usuario)
            )
            if cursor.fetchone() is None:
                return 0

            cursor.execute(
                "INSERT INTO atividade (id_disciplina, titulo, tipo, descricao, data_prazo, status) VALUES (?, ?, ?, ?, ?, ?)",
                (atividade.id_disciplina, atividade.titulo, atividade.tipo, atividade.descricao, atividade.data_prazo, atividade.status)
            )
            conexao.commit()
            return cursor.lastrowid

    def atualizar(self, atividade, id_usuario):
        
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "UPDATE atividade SET titulo = ?, tipo = ?, descricao = ?, data_prazo = ?, status = ? WHERE id_atividade = ? AND id_disciplina IN (SELECT id_disciplina FROM disciplina WHERE id_usuario = ?)",
                (atividade.titulo, atividade.tipo, atividade.descricao, atividade.data_prazo, atividade.status, atividade.id_atividade, id_usuario)
            )
            conexao.commit()
            return cursor.rowcount

    def remover(self, id_atividade, id_usuario):
        
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "DELETE FROM atividade WHERE id_atividade = ? AND id_disciplina IN (SELECT id_disciplina FROM disciplina WHERE id_usuario = ?)",
                (id_atividade, id_usuario)
            )
            conexao.commit()
            return cursor.rowcount

    def concluir(self, id_atividade, id_usuario):
        # Marca a atividade como concluída (status = 'concluida') se for do usuário.
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "UPDATE atividade SET status = 'concluida' WHERE id_atividade = ? AND id_disciplina IN (SELECT id_disciplina FROM disciplina WHERE id_usuario = ?)",
                (id_atividade, id_usuario)
            )
            conexao.commit()
            return cursor.rowcount

class UsuarioDAO:
    def __init__(self, caminho_banco="../database/prazo_certo.db"):
        self.caminho_banco = caminho_banco

    def inserir(self, usuario):
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
                (usuario.nome, usuario.email, usuario.senha_hash)
            )
            conexao.commit()
            return cursor.lastrowid

    def buscar_por_email(self, email):
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "SELECT id_usuario, nome, email, senha_hash, data_cadastro FROM usuario WHERE email = ?",
                (email,)
            )
            linha = cursor.fetchone()
            if linha:
                return Usuario(*linha)
            return None

    def buscar_por_id(self, id_usuario):
        with sqlite3.connect(self.caminho_banco) as conexao:
            cursor = conexao.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(
                "SELECT id_usuario, nome, email, senha_hash, data_cadastro FROM usuario WHERE id_usuario = ?",
                (id_usuario,)
            )
            linha = cursor.fetchone()
            if linha:
                return Usuario(*linha)
            return None