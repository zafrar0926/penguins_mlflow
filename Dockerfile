FROM python:3.9

# Configuración de credenciales para MinIO y MLflow
ARG MLFLOW_S3_ENDPOINT_URL=http://10.43.101.205:9000
ARG AWS_ACCESS_KEY_ID=admin
ARG AWS_SECRET_ACCESS_KEY=supersecret

# Crear directorio de trabajo
RUN mkdir /work
WORKDIR /work

# Copiar archivos del proyecto
COPY . .

# Instalar JupyterLab y dependencias necesarias
RUN pip install --upgrade pip \
    && pip install jupyterlab==3.6.1 \
    && pip install -r requirements.txt

# Exponer el puerto para JupyterLab
EXPOSE 8888

# Comando de inicio para JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root"]



