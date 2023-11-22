FROM python:3.8

RUN mkdir /app
WORKDIR /app

COPY . .

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["sh", "-c", "export $(cat .env | xargs) && python3 manage.py migrate && python3 manage.py runserver $WEB_URL:$WEB_PORT"]