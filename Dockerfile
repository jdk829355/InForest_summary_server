FROM python:3.13

COPY . /src
WORKDIR /src

RUN pip install -r requirements.txt
RUN pip install uvicorn

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]