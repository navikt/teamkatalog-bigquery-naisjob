FROM navikt/python:3.9

USER root

# Install poetry
#RUN apt-get update -y && apt-get install -y curl && \
#    curl -sSL https://install.python-poetry.org | python3 -

RUN pip install poetry==1.8.4

COPY . .

# Install app
RUN export PATH=$PATH:$HOME/.local/bin && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

USER apprunner

CMD ["python", "main.py"]
