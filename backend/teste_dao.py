# teste_dao.py — script manual para verificar os DAOs.
# Não é usado pelo Flask. Rode com: python teste_dao.py
# Ele cria um banco temporário a partir do schema.sql e nao toca no prazo_certo.db.

import sqlite3
import tempfile
from pathlib import Path

from dao import AtividadeDAO, DisciplinaDAO
from models import Atividade, Disciplina

BASE_DIR = Path(__file__).resolve().parent
SCHEMA = BASE_DIR.parent / "database" / "schema.sql"

falhas = []


def check(nome, condicao, detalhe=""):
    if condicao:
        print(f"[OK] {nome}")
    else:
        print(f"[FALHOU] {nome} {detalhe}")
        falhas.append(nome)


def main():
    # O TemporaryDirectory apaga o banco de teste no final.
    with tempfile.TemporaryDirectory(prefix="prazo_certo_teste_", ignore_cleanup_errors=True) as pasta:
        caminho = Path(pasta) / "teste.db"

        with sqlite3.connect(caminho) as conexao:
            conexao.executescript(SCHEMA.read_text(encoding="utf-8"))

        disciplina_dao = DisciplinaDAO(str(caminho))
        atividade_dao = AtividadeDAO(str(caminho))

        # Dois usuários para testar o isolamento.
        with sqlite3.connect(caminho) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
                ("Ana", "ana@example.com", "hash"),
            )
            user1 = cursor.lastrowid
            cursor.execute(
                "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
                ("Bruno", "bruno@example.com", "hash"),
            )
            user2 = cursor.lastrowid
            conexao.commit()

        # Disciplinas: uma para cada usuário.
        id_disc1 = disciplina_dao.inserir(Disciplina(None, user1, "Banco de Dados", "Prof. A"))
        id_disc2 = disciplina_dao.inserir(Disciplina(None, user2, "POO", "Prof. B"))
        check("inserir disciplina do user1", id_disc1 > 0)
        check("inserir disciplina do user2", id_disc2 > 0)

        lista_disc1 = disciplina_dao.listar_por_usuario(user1)
        lista_disc2 = disciplina_dao.listar_por_usuario(user2)
        check("listar disciplinas do user1", len(lista_disc1) == 1 and lista_disc1[0].nome == "Banco de Dados")
        check("listar disciplinas do user2", len(lista_disc2) == 1 and lista_disc2[0].nome == "POO")

        check(
            "user2 nao atualiza disciplina do user1",
            disciplina_dao.atualizar(Disciplina(id_disc1, user2, "Invadida", "X")) == 0,
        )
        check(
            "user1 atualiza a propria disciplina",
            disciplina_dao.atualizar(Disciplina(id_disc1, user1, "BD", "Prof. A")) == 1,
        )

        # Atividades: uma para cada usuário.
        id_ativ1 = atividade_dao.inserir(
            Atividade(None, id_disc1, "Prova de SQL", "prova", "SELECT/JOIN", "2026-11-20", "pendente"),
            user1,
        )
        check("inserir atividade do user1", id_ativ1 > 0)

        check(
            "user2 nao insere na disciplina do user1",
            atividade_dao.inserir(
                Atividade(None, id_disc1, "Invasão", "trabalho", None, "2026-11-21", "pendente"),
                user2,
            ) == 0,
        )

        id_ativ2 = atividade_dao.inserir(
            Atividade(None, id_disc2, "Trabalho de POO", "trabalho", "Classes", "2026-11-22", "pendente"),
            user2,
        )
        check("inserir atividade do user2", id_ativ2 > 0)

        lista_ativ1 = atividade_dao.listar_por_usuario(user1)
        lista_ativ2 = atividade_dao.listar_por_usuario(user2)
        check(
            "listar atividades do user1",
            len(lista_ativ1) == 1 and lista_ativ1[0].titulo == "Prova de SQL",
            f"veio {[(a.id_atividade, a.titulo) for a in lista_ativ1]}",
        )
        check(
            "listar atividades do user2",
            len(lista_ativ2) == 1 and lista_ativ2[0].titulo == "Trabalho de POO",
            f"veio {[(a.id_atividade, a.titulo) for a in lista_ativ2]}",
        )

        check(
            "user2 nao atualiza atividade do user1",
            atividade_dao.atualizar(
                Atividade(id_ativ1, id_disc1, "Alterada", "prova", None, "2026-11-23", "pendente"),
                user2,
            ) == 0,
        )
        check(
            "user1 atualiza a propria atividade",
            atividade_dao.atualizar(
                Atividade(id_ativ1, id_disc1, "Prova de SQL 2", "prova", "JOIN", "2026-11-23", "pendente"),
                user1,
            ) == 1,
        )

        check("user2 nao conclui atividade do user1", atividade_dao.concluir(id_ativ1, user2) == 0)
        check("user1 conclui a propria atividade", atividade_dao.concluir(id_ativ1, user1) == 1)

        lista_ativ1 = atividade_dao.listar_por_usuario(user1)
        check(
            "status da atividade do user1",
            len(lista_ativ1) == 1 and lista_ativ1[0].status == "concluida",
            f"veio {[a.status for a in lista_ativ1]}",
        )

        check("user2 nao remove atividade do user1", atividade_dao.remover(id_ativ1, user2) == 0)
        check("user1 remove a propria atividade", atividade_dao.remover(id_ativ1, user1) == 1)
        check("user1 ficou sem atividades", len(atividade_dao.listar_por_usuario(user1)) == 0)

        # CASCADE: uma nova atividade deve sumir junto com a disciplina.
        atividade_dao.inserir(
            Atividade(None, id_disc1, "Nova atividade", "trabalho", None, "2026-11-24", "pendente"),
            user1,
        )
        check("user1 remove a propria disciplina", disciplina_dao.remover(id_disc1, user1) == 1)
        check("CASCADE removeu a atividade junto", len(atividade_dao.listar_por_usuario(user1)) == 0)


if __name__ == "__main__":
    main()
    if falhas:
        print(f"\n{len(falhas)} verificacao(oes) falharam.")
        raise SystemExit(1)
    print("\nTodas as verificacoes passaram.")
