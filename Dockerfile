FROM python:3

COPY ./python_app.py /app.py

EXPOSE 5000

RUN pip3 install flask

WORKDIR /

CMD ["flask", "run"]
