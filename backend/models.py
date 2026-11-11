class Disciplina:
    def __init__(self, id_disciplina, id_usuario, nome, professor):
        self.id_disciplina = id_disciplina
        self.id_usuario = id_usuario
        self.nome = nome
        self.professor = professor

    def to_dict(self):
        return {
            'id_disciplina': self.id_disciplina,
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'professor': self.professor
        }

class Atividade:
    def __init__(self, id_atividade, id_disciplina, titulo, tipo, descricao, data_prazo, status):
        self.id_atividade = id_atividade
        self.id_disciplina = id_disciplina
        self.titulo = titulo
        self.tipo = tipo
        self.descricao = descricao
        self.data_prazo = data_prazo
        self.status = status

    def to_dict(self):
        return {
            'id_atividade': self.id_atividade,
            'id_disciplina': self.id_disciplina,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'data_prazo': self.data_prazo,
            'status': self.status
        }

class Usuario:
    def __init__(self, id_usuario, nome, email, senha_hash, data_cadastro):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.data_cadastro = data_cadastro

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'email': self.email,
            'data_cadastro': self.data_cadastro
        }