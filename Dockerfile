# ------Python Build Image-----------
FROM python:alpine3.18 AS builder

COPY requirements.txt /

RUN pip install --user -r /requirements.txt --no-cache-dir --no-warn-script-location

#------ Python Run Image
FROM python:alpine3.18
LABEL maintainer="tchatziantoniou@gmail.com"

RUN apk add --no-cache \
      vim \
      aws-cli

ENV PYTHONPATH=/app/.local
ENV PATH=$PATH:/app/.local/bin

RUN addgroup --system --gid 500 app && \
    adduser --system --uid 500 --home /app --disabled-password --no-create-home --ingroup app app

RUN mkdir /app && \
    chown -R app:app /app

COPY --from=builder --chown=app:app /root/.local /app/.local
COPY --chown=app:app aws_credentials.py app/.local/bin
COPY --chown=app:app credentials app/.aws/

WORKDIR /app
USER app

CMD [ "tail", "-f", "/dev/null" ]
