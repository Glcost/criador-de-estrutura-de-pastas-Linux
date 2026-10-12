# DevToolkit Linux

Kit modular de automacao para ambientes de desenvolvimento,
com foco inicial no Linux Mint.

## Requisitos

- Linux Mint
- Python 3.10 ou superior
- Git
- Terminal Bash

Node.js e npm sao opcionais e necessarios apenas para
executar os projetos Node.js gerados.

## Instalacao para desenvolvimento

Clone ou copie este repositorio e entre na pasta do projeto.

Crie um ambiente virtual:

    python3 -m venv .venv
    source .venv/bin/activate

Instale o projeto e as dependencias de desenvolvimento:

    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"

## Diagnostico

    devtoolkit doctor

O comando verifica o sistema operacional, ferramentas
disponiveis e espaco livre em disco.

## Criar projetos

Python:

    devtoolkit create minha-api --template python --dest ~/Projetos

Node.js:

    devtoolkit create meu-backend --template node --dest ~/Projetos

Web:

    devtoolkit create meu-site --template web --dest ~/Projetos

O destino deve ser uma pasta que possa ser escrita pelo usuario.
O programa nao sobrescreve projetos existentes.

## Testes

    python -m pytest

## Seguranca

- Nao execute o DevToolkit como root.
- A versao inicial nao instala pacotes automaticamente.
- Revise comandos antes de executa-los.
- Nunca armazene senhas, tokens ou credenciais no Git.

## Estrutura

- src/devtoolkit: codigo da aplicacao.
- tests: testes automatizados.
- pyproject.toml: configuracao e instalacao do pacote.

## Roadmap

- [x] CLI inicial
- [x] Diagnostico basico
- [x] Templates Python, Node.js e Web
- [x] Testes iniciais
- [ ] Instalacao de ferramentas com confirmacao
- [ ] Templates adicionais
- [ ] Integracao continua

## Interface web local

A interface web oferece um painel escuro para consultar o ambiente, escolher um template,
pré-visualizar os arquivos e criar projetos usando o mesmo gerador da CLI.

Instale as dependências opcionais da interface:

```bash
python -m pip install -e ".[web]"
```

Inicie a interface:

```bash
devtoolkit web
```

Abra `http://127.0.0.1:8765` no navegador. Para encerrar, use `Ctrl+C` no terminal.

A interface escuta somente em `127.0.0.1` e não fica acessível pela rede local.
A pasta de destino deve existir ou poderá ser criada pelo gerador; o projeto não será
sobrescrito se já existir. Para usar somente a CLI, não é necessário instalar `.[web]`.
