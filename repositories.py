from sqlalchemy.orm import Session
from models import Livro, Usuario, Emprestimo
from typing import List, Optional
from datetime import datetime

from schemas import LivroAtualizarSchema


class LivroRepository:

    def __init__(self, db: Session):
        self.db = db

    def criar(self, livro: Livro) -> Livro:
        if self.buscar_por_isbn(livro.isbn):
            raise ValueError(f"ISBN {livro.isbn} já cadastrado")

        if livro.quantidade == 1:
            livro.disponivel = False

        try:
            self.db.add(livro)
            self.db.commit()
            self.db.refresh(livro)
            return livro
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError("Erro de integridade no banco de dados") from e
        
    def buscar_por_isbn(self, isbn: str) -> Optional[Livro]:
        return self.db.query(Livro).filter(Livro.isbn == isbn).first()

    def atualizar(self, isbn: str, dados: LivroAtualizarSchema) -> Livro:
        livro = self.db.query(Livro).filter(Livro.isbn == isbn).first()
        if not livro:
            raise ValueError(f"Livro com ISBN {isbn} não encontrado")

        livro.quantidade = dados.quantidade
        livro.localizacao = dados.localizacao

        self.db.commit()
        self.db.refresh(livro)
        return livro


class UsuarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def criar(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário no banco de dados"""
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca um usuário pelo ID"""
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Busca um usuário pelo email"""
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def listar_todos(self) -> List[Usuario]:
        """Lista todos os usuários cadastrados"""
        return self.db.query(Usuario).all()

    def atualizar(self, usuario_id: int,
                  usuario_data: dict) -> Optional[Usuario]:
        """Atualiza os dados de um usuário"""
        usuario = self.buscar_por_id(usuario_id)
        if usuario:
            for key, value in usuario_data.items():
                setattr(usuario, key, value)
            self.db.commit()
            self.db.refresh(usuario)
        return usuario

    def remover(self, usuario_id: int) -> bool:
        """Remove um usuário do banco de dados"""
        usuario = self.buscar_por_id(usuario_id)
        if usuario:
            self.db.delete(usuario)
            self.db.commit()
            return True
        return False

    def desativar(self, usuario_id: int) -> Optional[Usuario]:
        """Desativa um usuário (soft delete)"""
        usuario = self.buscar_por_id(usuario_id)
        if usuario:
            usuario.ativo = False
            self.db.commit()
            self.db.refresh(usuario)
        return usuario

class EmprestimoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_emprestimos_ativos(self):
        emprestimos = self.db.query(Emprestimo).join(Livro).join(Usuario).all()
        return [
            {
                "usuario_id": e.usuario_id,
                "nome_usuario": e.usuario.username,
                "livro_id": e.livro_id,
                "titulo_livro": e.livro.titulo,
                "data_emprestimo": e.data_emprestimo
            }
            for e in emprestimos
        ]

    def emprestar(self, livro_id: int, usuario_id: int) -> Emprestimo:
        """Realiza um empréstimo, mantendo 1 unidade para consulta local"""
        livro = self.db.query(Livro).filter(Livro.id == livro_id).first()
        if not livro:
            raise ValueError("Livro não encontrado")

        if livro.quantidade <= 1:
            raise ValueError("Livro indisponível para empréstimo – reservado para consulta local")

        # Cria o empréstimo
        emprestimo = Emprestimo(
            livro_id=livro_id,
            usuario_id=usuario_id,
            data_emprestimo=datetime.now()
        )

        # Atualiza quantidade (sem zerar completamente)
        livro.quantidade -= 1

        # Atualiza disponibilidade: só fica indisponível se quantidade for 1
        if livro.quantidade == 1:
            livro.disponivel = False

        self.db.add(emprestimo)
        self.db.commit()
        self.db.refresh(emprestimo)
        return emprestimo

    def devolver(self, usuario_id: int, livro_id: int):
        """Devolve um livro emprestado por um usuário"""
        emprestimo = (
            self.db.query(Emprestimo)
            .filter(Emprestimo.usuario_id == usuario_id, Emprestimo.livro_id == livro_id)
            .first()
        )

        if not emprestimo:
            raise ValueError("Este usuário não possui esse livro emprestado")

        livro = self.db.query(Livro).filter(Livro.id == livro_id).first()
        if not livro:
            raise ValueError("Livro não encontrado")

        # Atualiza quantidade
        livro.quantidade += 1

        # Se a quantidade ANTES da devolução era 1 e o livro estava indisponível, ele volta a estar disponível
        if livro.quantidade > 1 and not livro.disponivel:
            livro.disponivel = True

        # Remove o registro de empréstimo
        self.db.delete(emprestimo)

        self.db.commit()
        return {"mensagem": "Livro devolvido com sucesso"}