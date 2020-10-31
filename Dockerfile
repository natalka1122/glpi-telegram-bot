FROM python:3.7.9 AS builder
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --user -r requirements.txt

FROM python:3.7.9-slim-buster

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-dev}
ENV TINI_VERSION="v0.19.0"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini


WORKDIR /project

RUN useradd -m -r user && chown user /project

USER user

COPY --from=builder /root/.local/bin ${$HOME}/.local
COPY . .

ENTRYPOINT ["/tini", "--", "python", "main.py"]