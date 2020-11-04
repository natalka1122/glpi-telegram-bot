FROM alpine

RUN apk add --no-cache build-base  python3 python3-dev && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

WORKDIR /project

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /data
VOLUME [ "/data" ]

COPY . .

ENTRYPOINT ["python", "main.py"]
