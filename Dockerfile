# Dockerfile

FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["streamlit", "run", "dashboard/streamlit_app.py"]