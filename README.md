# SWAPI API - Flask

API RESTful em Flask que funciona como um proxy para a [Star Wars API (SWAPI)](https://swapi.dev/), com funcionalidades de filtragem dinâmica, paginação automática, ordenação e carregamento de dados relacionais.

---


## Stack utilizada

- **Python 3.9+**
- **Flask**: microframework web
- **Requests**: chamadas HTTP para SWAPI
- **JSON**: manipulação e resposta em formato JSON


## Rodando localmente

Clone o projeto

```bash
  git clone https://github.com/PauloHGR/swapi.git
```

Entre no diretório do projeto

```bash
  cd my-project
```

Crie e ative o ambiente virtual
```bash
  python3 -m venv venv
  source venv/bin/activate     # Linux/macOS
  venv\Scripts\activate        # Windows
```

Instale as dependências

```bash
  pip3 install -r requirements.txt
```

Execute a aplicação

```bash
  python3 app.py
```


## Funcionalidades

- Busca dados de diferentes recursos da SWAPI: people, films, species, planets, starships e vehicles.
- Aplicação de filtros dinâmicos via query params.
- Ordenação de resultados.
- Inclusão de dados relacionais (ex: filmes relacionados a um personagem).
- Endpoint flexível para recursos e IDs específicos.


## Documentação da API

#### Retorna todos os itens

```http
  GET {url}/${entidade}
  
  Ex.: GET {url}/people
```
#### Retorna todos os itens utilizando filtragem

```http
  GET {url}/${entidade}?query=value

  Ex.: GET {url}/people?name=luke
```

| Parâmetro   | Tipo       | Descrição                           |
| :---------- | :--------- | :---------------------------------- |
| `name` | `string` | Filtrar pessoas pelo nome |

#### Retorna um item

```http
  GET {url}/${entidade}/${id}

  Ex.: GET {url}/films/4

```

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `id`      | `string` | O ID do item que você quer |

#### Incluir dados relacionais (exemplo: filmes relacionados a uma pessoa)

```http
  GET {url}/${entidade}?${entidade_relacionada}=true

  Ex.: GET /people?films=true

```

#### Ordenar resultados

```http
  GET {url}/${entidade}?sort_by=${field}&sort_dir=[asc,desc]

  Ex.: GET /people?sort_by=name&sort_dir=desc

```
## Rodando os testes

Utilizamos pytest com unittest.mock para testar endpoints e mocks das requisições externas. Para rodar os testes, rode o seguinte comando

```bash
  pytest file.py
```

