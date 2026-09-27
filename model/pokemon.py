from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from typing import Union
from model import Base

class Pokemon(Base):
    __tablename__ = 'pokemon'

    id = Column("pk_pokemon", Integer, primary_key=True, autoincrement=True)
    nome = Column(String(140), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    nivel = Column(Integer, nullable=False)
    data_insercao = Column(DateTime, default=datetime.now)

    def __init__(self, nome: str, tipo: str, nivel: int,
                 data_insercao: Union[DateTime, None] = None):
        """
        Cria um Pokémon da Pokédex

        Arguments:
            nome: nome do Pokémon.
            tipo: tipo do Pokémon (ex: Elétrico, Fogo, Água)
            nivel: nível do Pokémon
            data_insercao: data de quando o Pokémon foi inserido à base
        """
        self.nome = nome
        self.tipo = tipo
        self.nivel = nivel

        if data_insercao:
            self.data_insercao = data_insercao



