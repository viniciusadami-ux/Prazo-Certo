# Roteiro do `app.py`

Este arquivo é direção, não código pronto. O `app.py` é seu: escreva uma parte,
teste, me mande e eu reviso (2 acertos, 1 correção, 1 pergunta).

## Ordem de construção

1. Configuração + servir o frontend.
2. Cadastro, login, logout e `/api/me`.
3. Decorator de login.
4. Disciplinas.
5. Atividades.
6. Relatório (só se sobrar tempo).

Não comece pelas atividades. Sem sessão funcionando, toda rota protegida vira
teste de adivinhação.

## 1. Configuração

- Imports: `os`, `sqlite3`, `datetime`, `functools.wraps`, Flask
  (`Flask`, `jsonify`, `request`, `session`, `send_from_directory`, `abort`),
  `werkzeug.security` (`generate_password_hash`, `check_password_hash`),
  `models` e `dao`.
- Calcule os caminhos a partir de `Path(__file__).resolve().parent`, não de
  `os.getcwd()`: o app precisa rodar de `backend/` e também de outro diretório.
  - `BASE_DIR` = pasta `backend/`.
  - `DB_PATH` = `BASE_DIR.parent / "database" / "prazo_certo.db"`.
  - `FRONTEND_DIR` = `BASE_DIR.parent` (a raiz do app).
- Passe `DB_PATH` para os DAOs: `DisciplinaDAO(DB_PATH)`, etc. O construtor já
  aceita o caminho.
- `app = Flask(__name__, static_folder=None)`: o Flask não deve servir a pasta
  inteira, porque `backend/`, `database/` e `docs/` ficam dentro dela.
- `SECRET_KEY`: `os.getenv("SECRET_KEY")`. Se vier `None`, pare com um erro
  claro. Nunca escreva a chave no código.
- Cookies de sessão: `SESSION_COOKIE_HTTPONLY = True`,
  `SESSION_COOKIE_SAMESITE = "Lax"`. `SECURE` fica `False` no localhost.
- Em produção seria HTTPS + `SECURE=True`; aqui não há deploy.

## 2. Servir o frontend

Rotas públicas, separadas por pasta:

| Método | URL | O que devolve |
|---|---|---|
| GET | `/` | `index.html` |
| GET | `/css/<path:arquivo>` | arquivo de `css/` |
| GET | `/js/<path:arquivo>` | arquivo de `js/` |
| GET | `/pages/<path:arquivo>` | arquivo de `pages/` |
| GET | `/img/<path:arquivo>` | arquivo de `img/` |

Use `send_from_directory`. Não crie uma rota `/<path:arquivo>` que sirva
qualquer coisa: ela abriria `backend/dao.py`, `database/prazo_certo.db` e
`docs/`. Teste no navegador:

- `/` abre a landing.
- `/css/estilo.css` abre o CSS.
- `/backend/dao.py` e `/database/prazo_certo.db` devem dar 404.

## 3. Autenticação

### `POST /api/usuarios`

Corpo JSON: `nome`, `email`, `senha`.

Validação no backend:

- `nome`: texto, sem espaços nas pontas, não vazio.
- `email`: texto, com `@`, sem espaços; o banco tem `UNIQUE COLLATE NOCASE`.
- `senha`: mínimo 6 caracteres.
- `request.get_json(silent=True) or {}`: se o corpo não for JSON, trate como
  inválido em vez de estourar erro.

Fluxo:

1. Validar.
2. `senha_hash = generate_password_hash(senha)`.
3. Criar `Usuario(None, nome, email, senha_hash, None)`.
4. `UsuarioDAO.inserir(usuario)`.
5. Responder 201 com `id_usuario`, `nome`, `email` e `data_cadastro`; **nunca**
   devolver `senha_hash`.
6. Capturar `sqlite3.IntegrityError` para e-mail duplicado e responder 400 com
   mensagem clara.

### `POST /api/login`

Corpo: `email`, `senha`.

1. Buscar por e-mail com `UsuarioDAO.buscar_por_email`.
2. Se não existir **ou** `check_password_hash` falhar, responder 401 com a
   mesma mensagem: `"E-mail ou senha inválidos."` Não diga qual dos dois errou.
3. Se ok, `session["id_usuario"] = usuario.id_usuario`.
4. Responder 200 com os dados públicos do usuário (sem `senha_hash`).

### `POST /api/logout`

`session.clear()` e 204. Sem corpo.

### `GET /api/me`

Se houver sessão, devolver o usuário; se não, 401. Ajuda o frontend a saber se
deve mostrar login ou dashboard.

## 4. Decorator de login

Crie `login_obrigatorio(funcao)` com `functools.wraps`.

- Se `session.get("id_usuario")` não existir, `jsonify({"erro": "Não autenticado."}), 401`.
- Se existir, chama a função.

Use em todas as rotas de disciplinas, atividades e relatório. O `id_usuario`
vem **da sessão**, nunca do corpo JSON; senão qualquer um editaria a conta do
outro.

## 5. Disciplinas

| Método | URL | Sucesso | Erros |
|---|---|---|---|
| GET | `/api/disciplinas` | 200 lista | 401 |
| POST | `/api/disciplinas` | 201 objeto | 400, 401 |
| PUT | `/api/disciplinas/<id>` | 200 objeto | 400, 401, 404 |
| DELETE | `/api/disciplinas/<id>` | 204 | 401, 404 |

- `nome` obrigatório; `professor` opcional.
- No PUT, o DAO usa `id_usuario` no `WHERE`; `rowcount == 0` vira 404.
- No DELETE, idem; o `CASCADE` remove as atividades.
- Depois do 204, não devolva JSON.

## 6. Atividades

| Método | URL | Sucesso | Erros |
|---|---|---|---|
| GET | `/api/atividades` | 200 lista | 401 |
| POST | `/api/atividades` | 201 objeto | 400, 401 |
| PUT | `/api/atividades/<id>` | 200 objeto | 400, 401, 404 |
| PATCH | `/api/atividades/<id>/concluir` | 200 | 401, 404 |
| DELETE | `/api/atividades/<id>` | 204 | 401, 404 |

Validação:

- `titulo`: não vazio.
- `tipo`: `"prova"` ou `"trabalho"`.
- `data_prazo`: `datetime.strptime(valor, "%Y-%m-%d")`; data inválida → 400.
- `id_disciplina`: inteiro; a disciplina precisa ser do usuário logado.
- `status`: no POST, `"pendente"`; não aceite status arbitrário do corpo.
- `descricao`: opcional.

No POST, `AtividadeDAO.inserir(atividade, id_usuario)` devolve `0` quando a
disciplina não é do usuário; traduza para 400/404, não para 500.

Até o bloco de integração (14/11), `AtividadeDAO.listar_por_usuario` devolve
`id_disciplina`, mas não `nome_disciplina`. O frontend pode cruzar com
`/api/disciplinas`. No JOIN, o DAO passa a devolver o nome e os filtros
`disciplina`, `tipo` e `status`; a rota só repassa a query string.

## 7. Testes manuais

Com o venv ativo e `SECRET_KEY` definida:

```powershell
python app.py
```

Em outro terminal:

```powershell
# cadastro
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/usuarios `
  -ContentType "application/json" `
  -Body '{"nome":"Ana","email":"ana@example.com","senha":"123456"}'

# login (guarde o cookie de sessão)
Invoke-WebRequest -Method Post -Uri http://localhost:5000/api/login `
  -ContentType "application/json" `
  -Body '{"email":"ana@example.com","senha":"123456"}' `
  -SessionVariable s

# disciplinas com a sessão
Invoke-RestMethod -Uri http://localhost:5000/api/disciplinas -WebSession $s
```

Teste também: senha errada (401), e-mail duplicado (400), data `2026-13-40`
(400), atividade em disciplina de outro usuário (400) e acesso sem sessão
(401).

## 8. Perguntas que a defesa pode fazer

- Por que a senha é guardada como hash e não em texto puro?
- Por que o login não pode dizer se o e-mail existe?
- Por que o `id_usuario` vem da sessão e não do `request.json`?
- Qual a diferença entre 401, 403 e 404? Qual você usou e por quê?
- Por que o Flask não pode servir `backend/`, `database/` e `docs/`?
- Por que o `DELETE` devolve 204 e não 200?
- Por que o `PRAGMA foreign_keys = ON` precisa estar em cada conexão do DAO?
- O que o `rowcount == 0` significa no `UPDATE` e no `DELETE`?

## O que eu reviso quando você mandar

- 2 acertos concretos.
- 1 correção prioritária.
- 1 pergunta de "por que você fez assim?".

Se o arquivo não rodar, o primeiro retorno é o erro exato e o trecho, não uma
reescrita completa.
