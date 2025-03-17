# MLflow Penguins Project

Este proyecto implementa un flujo completo de MLOps utilizando MLflow para el tracking y registro de modelos, MinIO como almacenamiento de artefactos, JupyterLab para la experimentación y entrenamiento, y una API de inferencia con FastAPI.

### Tabla de Contenidos

    - Descripción
    - Estructura del Proyecto
    - Requisitos
    - Configuración y Ejecución
        - Docker Compose
        - JupyterLab
        - MLflow Tracking Server
        - Inference API
    - Uso del Proyecto
        - Entrenamiento y Registro de Modelos
        - Consulta de Predicciones
    - Notas Adicionales

### Descripción

El proyecto permite:

    1. Entrenar modelos de clasificación sobre el dataset de pingüinos, utilizando experimentos con MLflow.
    2. Subir y almacenar artefactos (modelos, datasets, etc.) en MinIO.
    3. Registrar el mejor modelo en el Model Registry de MLflow.
    4. Exponer una API de inferencia mediante FastAPI para realizar predicciones con el modelo registrado.

### Estructura del Proyecto

    MLflow_Penguins/
    ├── docker-compose.yml         # Orquesta los contenedores: MySQL, MinIO, JupyterLab y API
    ├── Dockerfile                 # Dockerfile para JupyterLab
    ├── requirements.txt           # Requerimientos para JupyterLab (entrenamiento y experimentación)
    ├── mlflow_serv.service        # Archivo de configuración para levantar MLflow como servicio (opcional)
    └── inference_api/             # Servicio de API de inferencia
        ├── Dockerfile             # Dockerfile para la API de inferencia
        ├── inference_api.py       # Código FastAPI de la API
        └── requirements.txt       # Requerimientos para la API (incluye fastapi, uvicorn, mlflow, pandas, boto3)

### Requisitos

    Docker y Docker Compose instalados.
    (Opcional) Acceso a un servidor Linux para levantar MLflow como servicio con systemd.

### Configuración y Ejecución
Docker Compose

El archivo docker-compose.yml orquesta los siguientes servicios:

    1. MySQL: Para almacenar metadatos de MLflow.
    2. MinIO: Almacenamiento de artefactos S3-compatible.
    3. JupyterLab: Entorno de experimentación y entrenamiento.
    4. Inference API: Servicio FastAPI para realizar inferencias.

Asegúrate de tener el archivo en la raíz del proyecto. Puedes revisar y ajustar los puertos y variables de entorno según tu configuración.
JupyterLab

**Para construir y levantar JupyterLab, ejecuta en la raíz del proyecto:**

sudo docker-compose up --build jupyterlab

Accede a JupyterLab en http://<tu-ip>:8888.

**MLflow Tracking Server**

Asegúrate de que MLflow esté configurado para usar MinIO como artifact store (por ejemplo, con --default-artifact-root s3://mlflows3/artifacts) y que la tracking URI en los notebooks esté configurada a http://<tu-ip>:5000.
Inference API

El servicio de API se encuentra en la carpeta inference_api. Para levantarlo:

sudo docker-compose up --build inference_api

Accede a la documentación interactiva en http://<tu-ip>:8000/docs.

# Uso del Proyecto
## Entrenamiento y Registro de Modelos

    Preparación del Dataset:
    El notebook descarga el dataset (por ejemplo, penguins_size.csv) desde MinIO y lo procesa.

    Entrenamiento: 
    Se ejecutan varios experimentos (incluyendo DecisionTree y XGBoost) mediante MLflow.
    En los experimentos con XGBoost, se usa un nombre constante para el artefacto (penguins_xgboost_model) en cada run.

    Selección y Registro del Mejor Modelo: 
    Luego de ejecutar todos los experimentos, se selecciona el run con mayor precisión y se registra el modelo en el Model Registry con el nombre XGBoost_Best_Deployed.

    Un bloque de código en el notebook realiza lo siguiente:
        Recupera todos los runs del experimento.
        Ordena los runs por precisión.
        Selecciona el mejor run.
        Construye la URI del modelo (runs:/{best_run_id}/penguins_xgboost_model).
        Registra el modelo en el Model Registry.
        Finalmente, carga el modelo con mlflow.pyfunc.load_model("models:/XGBoost_Best_Deployed/latest").

## Consulta de Predicciones

La API de inferencia expone un endpoint /predict que:

    Recibe un JSON con las características del pingüino, por ejemplo:

    {
      "island": "Torgersen",
      "culmen_length_mm": 39.1,
      "culmen_depth_mm": 18.7,
      "flipper_length_mm": 181,
      "body_mass_g": 3750,
      "sex": "MALE"
    }

    Transforma las columnas categóricas usando el mismo mapeo que se usó en el entrenamiento:
        island: {"Biscoe": 0, "Dream": 1, "Torgersen": 2}
        sex: {".": 0, "FEMALE": 1, "MALE": 2}

    Carga el modelo registrado y realiza la predicción.

    Convierte la salida numérica de la predicción (por ejemplo, 0, 1 o 2) a la etiqueta original de la especie ({"Adelie": 0, "Chinstrap": 1, "Gentoo": 2}).

    Devuelve la predicción en formato JSON.

**Para probar la API, puedes usar cURL:**

curl -X POST "http://10.43.101.205:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"island": "Torgersen", "culmen_length_mm": 39.1, "culmen_depth_mm": 18.7, "flipper_length_mm": 181, "body_mass_g": 3750, "sex": "MALE"}'

La respuesta debería ser, por ejemplo:

{"prediction": "Adelie"}

## Notas Adicionales

**Volúmenes Compartidos:**
Asegúrate de que los directorios montados (por ejemplo, en JupyterLab) estén correctamente sincronizados entre el host y el contenedor.

**Dependencias:**
Si se presentan conflictos de versiones (por ejemplo, FastAPI vs. librerías de entrenamiento), considera aislar los entornos en contenedores separados, como se hizo en este proyecto.

**Configuración de MLflow y MinIO:**
Revisa que las variables de entorno (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MLFLOW_S3_ENDPOINT_URL) estén configuradas de forma consistente en todos los componentes.