FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
RUN mkdir ~/.streamlit
ADD config.toml .streamlit/config.toml
ADD credentials.toml .streamlit/credentials.toml
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["FromDawnTilDusk.py"]
#CMD streamlit run --server.enableCORS false --server.port 8501 visualisation.py