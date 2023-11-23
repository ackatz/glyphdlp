FROM python:slim as builder

RUN apt-get update && apt-get install -y wget curl --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN SUPERCRONIC_RELEASE=$(curl -I https://github.com/aptible/supercronic/releases/latest | awk -F '/' '/^location/ {print  substr($NF, 1, length($NF)-1)}' | sed 's/%0D//g') \
    && wget https://github.com/aptible/supercronic/releases/download/$SUPERCRONIC_RELEASE/supercronic-linux-amd64 -O /usr/local/bin/supercronic && chmod +x "/usr/local/bin/supercronic"

COPY . /app


FROM python:slim

COPY --from=builder /usr/local/bin/supercronic /usr/local/bin/supercronic
COPY --from=builder /app /app
COPY . /app

ENV PATH="/home/app/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --group app --home /app

RUN apt update && apt install -y pkg-config default-libmysqlclient-dev ca-certificates build-essential libssl-dev libffi-dev libmagic1 --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade wheel
RUN pip install --upgrade -r /app/requirements/app.txt
RUN pip install --upgrade -r /app/requirements/tests.txt

RUN chmod +x /app/run.sh && mkdir /app/log && chown -R app:app /app

EXPOSE 8000

USER app

CMD [ "/app/run.sh" ]