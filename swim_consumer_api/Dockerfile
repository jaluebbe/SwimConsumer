FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend_fastapi.py /code/

EXPOSE 80

CMD ["uvicorn", "backend_fastapi:app", "--host", "0.0.0.0", "--port", "80"]
