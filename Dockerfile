FROM python:3.11-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install poetry==1.4.2


# Define o diretório de trabalho no contêiner
WORKDIR /salvadorintegra

# Copia os arquivos necessários para o contêiner
COPY ./salvadorintegra/ /salvadorintegra
COPY ./entrypoint.sh /entrypoint.sh
COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock

RUN poetry config virtualenvs.create false
# Instala as dependências Python
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# Garante que o script de inicialização tenha permissões de execução
RUN chmod +x /entrypoint.sh

# Comando padrão para iniciar a aplicação
CMD ["/entrypoint.sh"]
