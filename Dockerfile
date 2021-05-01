FROM python:3.9.4-alpine3.12 AS builder

RUN python -mvenv /venv
ENV PATH="/venv/bin:$PATH"

ADD requirements.txt /requirements.txt

RUN apk -X http://dl-cdn.alpinelinux.org/alpine/v3.12/main -X http://dl-cdn.alpinelinux.org/alpine/v3.12/community add --no-cache --virtual .build-deps build-base libxslt-dev libxslt && \
    # apk -X http://dl-cdn.alpinelinux.org/alpine/v3.12/community add --no-cache libxslt && \
    pip install -r requirements.txt && \
    apk del .build-deps

FROM python:3.9.4-alpine3.12
RUN apk -X http://dl-cdn.alpinelinux.org/alpine/v3.12/community add --no-cache libxslt

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="/venv/bin:$PATH"

RUN echo $PATH $VIRTUAL_ENV

ADD check.py /check.py

CMD [ "python", "/check.py" ]

