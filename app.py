from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from sqlalchemy.exc import IntegrityError
from model import Session, Pokemon
from logger import logger
from schemas.pokemon import (
    PokemonSchema,
    PokemonViewSchema,
    PokemonBuscaSchema,
    PokemonDelSchema,
    ListaPokemonsSchema,
    ErrorSchema,
    PaginacaoSchema,
    PokemonTipoSchema,
    PokemonBuscaExternoSchema
)
from flask_cors import CORS
import requests
from pydantic import BaseModel
from typing import List

# Novo schema para resposta da PokéAPI
class PokemonExternoSchema(BaseModel):
    nome: str
    altura: int
    peso: int
    habilidades: List[str]

# Informações da API
info = Info(title="Pokédex API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Redireciona para a documentação")
pokemon_tag = Tag(name="Pokémons", description="Cadastro e gerenciamento de Pokémons")

# Redireciona para /openapi
@app.get('/', tags=[home_tag])
def home():
    return redirect('/openapi')

# Cadastro (POST)
@app.post('/cadastrar_pokemon', tags=[pokemon_tag],
          responses={"200": PokemonViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def cadastrar_pokemon(body: PokemonSchema):
    with Session() as session:
        try:
            pokemon = Pokemon(nome=body.nome, tipo=body.tipo, nivel=body.nivel)
            logger.debug(f"Adicionando Pokémon de nome: '{pokemon.nome}'")
            session.add(pokemon)
            session.commit()
            return PokemonViewSchema.from_orm(pokemon).model_dump(), 200
        except IntegrityError:
            session.rollback()
            return {"message": "Pokémon já cadastrado"}, 409
        except Exception as e:
            session.rollback()
            return {"message": str(e)}, 400

# Listar todos (GET)
@app.get('/pokemons', tags=[pokemon_tag],
         responses={"200": ListaPokemonsSchema, "400": ErrorSchema})
def listar_pokemons():
    with Session() as session:
        pokemons = session.query(Pokemon).all()
        return {
            "pokemons": [PokemonViewSchema.from_orm(p).model_dump() for p in pokemons]
        }, 200

# Buscar por ID (GET)
@app.get('/buscar_pokemon', tags=[pokemon_tag],
         responses={"200": PokemonViewSchema, "404": ErrorSchema})
def buscar_pokemon(query: PokemonBuscaSchema):
    with Session() as session:
        pokemon = session.query(Pokemon).filter(Pokemon.id == query.id).first()
        if not pokemon:
            return {"message": "Pokémon não encontrado"}, 404
        return PokemonViewSchema.from_orm(pokemon).model_dump(), 200

# Deletar (DELETE)
@app.delete('/deletar_pokemon', tags=[pokemon_tag],
            responses={"200": PokemonViewSchema, "404": ErrorSchema})
def deletar_pokemon(query: PokemonBuscaSchema):
    with Session() as session:
        pokemon = session.query(Pokemon).filter(Pokemon.id == query.id).first()
        if not pokemon:
            return {"message": "Pokémon não encontrado"}, 404
        session.delete(pokemon)
        session.commit()
        return PokemonViewSchema.from_orm(pokemon).model_dump(), 200

# Atualizar (PUT)
@app.put('/atualizar_pokemon', tags=[pokemon_tag],
         responses={"200": PokemonViewSchema, "404": ErrorSchema, "409": ErrorSchema, "400": ErrorSchema})
def atualizar_pokemon(body: PokemonSchema, query: PokemonBuscaSchema):
    with Session() as session:
        pokemon = session.query(Pokemon).filter(Pokemon.id == query.id).first()
        if not pokemon:
            return {"message": "Pokémon não encontrado"}, 404
        try:
            pokemon.nome = body.nome
            pokemon.tipo = body.tipo
            pokemon.nivel = body.nivel
            session.commit()
            return PokemonViewSchema.from_orm(pokemon).model_dump(), 200
        except IntegrityError:
            session.rollback()
            return {"message": "Já existe um Pokémon com esse nome"}, 409
        except Exception as e:
            session.rollback()
            return {"message": str(e)}, 400

# Buscar por tipo (GET)
@app.get('/pokemons_por_tipo', tags=[pokemon_tag],
         responses={"200": ListaPokemonsSchema, "400": ErrorSchema})
def pokemons_por_tipo(query: PokemonTipoSchema):
    with Session() as session:
        pokemons = session.query(Pokemon).filter(Pokemon.tipo == query.tipo).all()
        return {"pokemons": [PokemonViewSchema.from_orm(p).model_dump() for p in pokemons]}, 200

# Paginação (GET)
@app.get('/pokemons_paginados', tags=[pokemon_tag],
         responses={"200": ListaPokemonsSchema, "400": ErrorSchema})
def listar_pokemons_paginados(query: PaginacaoSchema):
    page = query.page
    limit = query.limit
    offset = (page - 1) * limit

    with Session() as session:
        pokemons = session.query(Pokemon).offset(offset).limit(limit).all()
        total = session.query(Pokemon).count()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "pokemons": [PokemonViewSchema.from_orm(p).model_dump() for p in pokemons]
        }, 200

# Consulta externa (GET)
@app.get('/pokemon_externo', tags=[pokemon_tag],
         responses={"200": PokemonExternoSchema, "404": ErrorSchema})
def pokemon_externo(query: PokemonBuscaExternoSchema):
    """Consultar dados de um Pokémon na PokéAPI"""
    url = f"https://pokeapi.co/api/v2/pokemon/{query.nome.lower()}"
    resposta = requests.get(url)

    if resposta.status_code != 200:
        return {"erro": "Pokémon não encontrado na PokéAPI"}, 404

    dados = resposta.json()
    return {
        "nome": dados["name"],
        "altura": dados["height"],
        "peso": dados["weight"],
        "habilidades": [h["ability"]["name"] for h in dados["abilities"]]
    }, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)




