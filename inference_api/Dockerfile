FROM python:3.9

WORKDIR /app

# Copiar requerimientos y luego instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Crear una subcarpeta "inference_api" y copiar todo allí
RUN mkdir -p /app/inference_api
COPY . /app/inference_api

EXPOSE 8000

# El comando indica que uvicorn debe buscar el objeto "app" en el módulo "inference_api.inference_api"
CMD ["uvicorn", "inference_api.inference_api:app", "--host", "0.0.0.0", "--port", "8000"]
