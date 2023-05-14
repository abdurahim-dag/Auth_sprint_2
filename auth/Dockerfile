FROM python:3.10
ENV PYTHONUNBUFFERED 1

RUN useradd -U app && \
    mkdir /home/app && \
    chown app:root /home/app

USER app

WORKDIR /auth

RUN python -m venv /home/app/venv
ENV PATH="/home/app/venv/bin:$PATH"

COPY --chown=app requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    ssh-keygen -t rsa -N '' -b 4096 -m PEM -f /auth/private.key && \
    openssl rsa -in /auth/private.key -pubout -outform PEM -out /auth/public.key

COPY --chown=app wsgi_app.py .
COPY --chown=app run.sh .
RUN chmod +x run.sh

COPY --chown=app ./app ./app

ENTRYPOINT ["/auth/run.sh"]
