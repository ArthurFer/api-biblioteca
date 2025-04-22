from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    autor = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True)
    disponivel = Column(Boolean, default=True)
    quantidade = Column(Integer, nullable=False)
    localizacao = Column(String(100), nullable=True)
    data_cadastro = Column(DateTime, default=datetime.now)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    ativo = Column(Boolean, default=True)
    password = Column(String(100), nullable=False)


class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    livro_id = Column(Integer, ForeignKey("livros.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    data_emprestimo = Column(DateTime, default=datetime.now)
    data_devolucao = Column(DateTime, nullable=True)

    livro = relationship("Livro", backref="emprestimos")
    usuario = relationship("Usuario", backref="emprestimos")
