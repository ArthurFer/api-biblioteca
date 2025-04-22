from pydantic import BaseModel, EmailStr
from datetime import datetime


class LivroSchema(BaseModel):
    titulo: str
    autor: str
    isbn: str
    quantidade: int
    localizacao: str

    class Config:
        from_attributes = True

class LivroAtualizarSchema(BaseModel):
    quantidade: int
    localizacao: str

class LivroSchemaOut(BaseModel):
    id: int
    titulo: str
    autor: str
    isbn: str
    disponivel: bool
    quantidade: int
    localizacao: str | None
    data_cadastro: datetime

    class Config:
        orm_mode = True

class UsuarioLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UsuarioSchema(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True

class UsuarioIdSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class EmprestimoSchema(BaseModel):
    livro_id: int
    usuario_id: int

    class Config:
        from_attributes = True

class DevolucaoSchema(BaseModel):
    usuario_id: int
    livro_id: int

class EmprestimoAtivoSchema(BaseModel):
    usuario_id: int
    nome_usuario: str
    livro_id: int
    titulo_livro: str
    data_emprestimo: datetime

    class Config:
        orm_mode = True

class MensagemSchema(BaseModel):
    mensagem: str