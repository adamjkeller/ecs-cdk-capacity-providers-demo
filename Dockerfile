FROM python:3.8

EXPOSE 5000

WORKDIR /

COPY ./python_app.py /app.py

RUN pip install flask

CMD ["flask", "run", "--host", "0.0.0.0"]
