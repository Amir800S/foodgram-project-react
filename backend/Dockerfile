FROM python:3.11-slim

WORKDIR /app

COPY foodgram/requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram/foodgram .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]

