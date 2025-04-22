from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import Livro, Usuario, Emprestimo
from schemas import LivroSchema, UsuarioSchema, EmprestimoSchema, UsuarioLoginSchema, LivroAtualizarSchema, \
    LivroSchemaOut, UsuarioIdSchema, DevolucaoSchema, EmprestimoAtivoSchema, MensagemSchema
from repositories import LivroRepository, EmprestimoRepository, UsuarioRepository
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import jwt
import datetime
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Cria as tabelas
Base.metadata.create_all(bind=engine)

# Configuração do JWT e do CryptContext para senha
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# origins = [
#     "http://localhost:5500",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota para servir o index.html
@app.get("/", response_class=HTMLResponse)
def index():
    return Path("templates/index.html").read_text(encoding="utf-8")

# Se houver outras rotas, como o painel
@app.get("/painel", response_class=HTMLResponse)
def painel():
    return Path("templates/painel.html").read_text(encoding="utf-8")

# -----------------------------------------------------------------------------------------------------------
# Rotas para Livros
@app.post("/livros", response_model=LivroSchema)
def criar_livro(livro: LivroSchema, db: Session = Depends(get_db)):
    repo = LivroRepository(db)
    livro_db = Livro(**livro.model_dump())

    try:
        return repo.criar(livro_db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlalchemy.exc.IntegrityError as e:
        if "UNIQUE constraint failed: livros.isbn" in str(e):
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um livro com o ISBN {livro.isbn}"
            )
        raise HTTPException(status_code=500, detail="Erro no banco de dados")

@app.put("/livros/atualizar/{isbn}", response_model=LivroAtualizarSchema)
def atualizar_livro(isbn: str, livro: LivroAtualizarSchema, db: Session = Depends(get_db)):
    repo = LivroRepository(db)
    try:
        return repo.atualizar(isbn, livro)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/livros/listar", response_model=List[LivroSchemaOut])
def listar_livros(db: Session = Depends(get_db)):
    livros = db.query(Livro).all()
    return livros

@app.get("/livros/{isbn}", response_model=LivroSchema)
def buscar_livro(isbn: str, db: Session = Depends(get_db)):
    repo = LivroRepository(db)
    livro = repo.buscar_por_isbn(isbn)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

@app.get("/livros/verificar-isbn/{isbn}")
def verificar_isbn(isbn: str, db: Session = Depends(get_db)):
    repo = LivroRepository(db)
    if repo.buscar_por_isbn(isbn):
        return {"disponivel": False}
    return {"disponivel": True}
    
# -----------------------------------------------------------------------------------------------------------
# Rotas para Empréstimos
@app.post("/emprestimos", response_model=EmprestimoSchema)
def emprestar_livro(emprestimo: EmprestimoSchema, db: Session = Depends(get_db)):
    repo = EmprestimoRepository(db)
    try:
        return repo.emprestar(emprestimo.livro_id, emprestimo.usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/emprestimos/{emprestimo_id}/devolver", response_model=EmprestimoSchema)
def devolver_livro(emprestimo_id: int, db: Session = Depends(get_db)):
    repo = EmprestimoRepository(db)
    try:
        return repo.devolver(emprestimo_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/emprestimos/ativos", response_model=list[EmprestimoAtivoSchema])
def listar_emprestimos_ativos(db: Session = Depends(get_db)):
    repo = EmprestimoRepository(db)
    return repo.listar_emprestimos_ativos()

@app.post("/emprestimos/devolver", response_model=MensagemSchema)
def devolver_livro(body: DevolucaoSchema, db: Session = Depends(get_db)):
    repo = EmprestimoRepository(db)
    try:
        repo.devolver(body.usuario_id, body.livro_id)
        return {"mensagem": "Livro devolvido com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
# -----------------------------------------------------------------------------------------------------------
# Rotas para Usuários

# Função para gerar o token
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Função para verificar a senha
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Função para criptografar a senha
def get_password_hash(password):
    return pwd_context.hash(password)


# Rota para criar o usuário
@app.post("/usuarios", response_model=UsuarioSchema)
def criar_usuario(usuario: UsuarioSchema, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    usuario_db = Usuario(
        username=usuario.username,
        email=usuario.email,
        password=get_password_hash(usuario.password)  # Criptografando a senha
    )
    return repo.criar(usuario_db)


# Rota de login
@app.post("/login")
def login(usuario: UsuarioLoginSchema, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    usuario_db = repo.buscar_por_email(usuario.email)  # Buscar usuário pelo email
    if not usuario_db or not verify_password(usuario.password, usuario_db.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Gerar token
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": usuario_db.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


# Outras rotas de usuários
@app.get("/usuarios/{usuario_id}", response_model=UsuarioSchema)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    usuario = repo.buscar_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.get("/usuarios", response_model=List[UsuarioIdSchema])
def listar_usuarios(db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    return repo.listar_todos()


@app.put("/usuarios/{usuario_id}", response_model=UsuarioSchema)
def atualizar_usuario(usuario_id: int, usuario_data: UsuarioSchema, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    usuario_atualizado = repo.atualizar(usuario_id, usuario_data.model_dump())
    if not usuario_atualizado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_atualizado


@app.delete("/usuarios/{usuario_id}")
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    if not repo.remover(usuario_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido com sucesso"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
