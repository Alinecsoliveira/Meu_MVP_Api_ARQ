from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from model.pokemon import Pokemon

# --- Schemas principais ---

class PokemonSchema(BaseModel):
    """Schema para cadastrar ou atualizar um Pokémon"""
    nome: str
    tipo: str
    nivel: Optional[int] = None

class PokemonBuscaSchema(BaseModel):
    """Schema para buscar um Pokémon pelo ID"""
    id: int

class PokemonBuscaExternoSchema(BaseModel):
    """Schema para buscar um Pokémon na PokéAPI pelo nome"""
    nome: str

class PokemonTipoSchema(BaseModel):
    """Schema para buscar Pokémons por tipo"""
    tipo: str

class PaginacaoSchema(BaseModel):
    """Schema para paginação de Pokémons"""
    page: Optional[int] = 1
    limit: Optional[int] = 10

class ListaPokemonsSchema(BaseModel):
    """Schema para listagem de Pokémons"""
    pokemons: List[PokemonSchema]

class PokemonViewSchema(BaseModel):
    """Schema para visualizar um Pokémon completo"""
    id: int
    nome: str
    tipo: str
    nivel: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class PokemonDelSchema(BaseModel):
    """Schema para retorno após remoção de um Pokémon"""
    message: str
    nome: str

class ErrorSchema(BaseModel):
    """Schema para mensagens de erro"""
    message: str

# --- Funções auxiliares ---

def apresenta_pokemons(pokemons: List[Pokemon]):
    """Converte lista de objetos Pokemon em dict seguindo schema"""
    result = []
    for p in pokemons:
        result.append({
            "id": p.id,
            "nome": p.nome,
            "tipo": getattr(p, "tipo", None),
            "nivel": getattr(p, "nivel", None),
        })
    return {"pokemons": result}

def apresenta_pokemon(pokemon: Pokemon):
    """Converte objeto Pokemon em dict seguindo schema"""
    return {
        "id": pokemon.id,
        "nome": pokemon.nome,
        "tipo": getattr(pokemon, "tipo", None),
        "nivel": getattr(pokemon, "nivel", None)
    }



