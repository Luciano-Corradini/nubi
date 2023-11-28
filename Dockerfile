FROM python:3.8

RUN wget -O /usr/local/bin/wait-for-it.sh \
    https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

WORKDIR /app

COPY ./challenge /app
COPY .env /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["sh", "-c", "export $(cat .env | xargs) && /usr/local/bin/wait-for-it.sh db:5432 -t 60 -- python3 manage.py migrate && python3 manage.py runserver $WEB_URL:$WEB_PORT"]