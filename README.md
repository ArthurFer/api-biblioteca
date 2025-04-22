# 📚 Biblioteca Digital – FastAPI

Este é um projeto de biblioteca digital desenvolvido em [FastAPI](https://fastapi.tiangolo.com/) com SQLite como banco de dados. O objetivo é gerenciar livros, usuários, empréstimos e devoluções de forma simples e eficiente.

## 🚀 Tecnologias utilizadas

- Python 3.11+
- FastAPI
- SQLite
- SQLAlchemy
- Jinja2 (para templates HTML)
- CORS Middleware
- Uvicorn (servidor ASGI)

---

## ✅ Pré-requisitos

Antes de começar, você precisa ter o **Python 3.11+** instalado na sua máquina. Você pode verificar com:

```
python --version
```

📦 Como rodar o projeto localmente
  1. Crie e ative um ambiente virtual:

:penguin: Linux/macOS:


```
python3 -m venv venv
source venv/bin/activate
```

:window: Windows:

```
python -m venv venv
venv\Scripts\activate
```

 2. Instale as dependências:

```
pip install -r requirements.txt
```

 3. Rode o servidor com Uvicorn:

```
uvicorn main:app --reload
```

🌐 Acesse a aplicação
Página inicial: http://localhost:8000

Documentação Swagger: http://localhost:8000/docs

🧩 Estrutura do projeto

```
📦 seu-projeto/
┣ 📄 main.py              ← App principal FastAPI
┣ 📄 requirements.txt     ← Dependências do projeto
┣ 📁 static/              ← Arquivos CSS, JS, imagens
┣ 📁 templates/           ← Páginas HTML com Jinja2
┣ 📄 database.py          ← Conexão e models
┣ 📄 schemas.py           ← Schemas Pydantic
┣ 📄 routes.py            ← Rotas da aplicação
```

🛠️ Funcionalidades principais
- Cadastro de usuários
- Login com JWT
- Cadastro de livros
- Listagem de livros disponíveis
- Empréstimo e devolução de livros
- Frontend básico com HTML/CSS/JS

🧪 Testes

Em desenvolvimento.
