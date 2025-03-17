import os
import mlflow
from fastapi import FastAPI
import pandas as pd

# Configurar variables de entorno para acceder a MinIO
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "supersecret"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://10.43.101.205:9000"

# Configurar la tracking URI de MLflow
mlflow.set_tracking_uri("http://10.43.101.205:5000")

app = FastAPI()

@app.get("/debug_experiment")
def debug_experiment():
    exp = mlflow.get_experiment_by_name("penguins_experiment")
    if exp is None:
        return {"error": "Experiment 'penguins_experiment' not found"}
    exp_dict = {
        "experiment_id": exp.experiment_id,
        "name": exp.name,
        "artifact_location": exp.artifact_location,
        "lifecycle_stage": exp.lifecycle_stage
    }
    return {"experiment": exp_dict}

@app.post("/predict")
def predict(data: dict):
    # Convertir el input en un DataFrame
    input_df = pd.DataFrame([data])
    
    # Aplicar mapeos para las columnas categóricas de entrada
    island_mapping = {"Biscoe": 0, "Dream": 1, "Torgersen": 2}
    sex_mapping = {".": 0, "FEMALE": 1, "MALE": 2}
    
    if "island" in input_df.columns:
        input_df["island"] = input_df["island"].map(island_mapping)
    if "sex" in input_df.columns:
        input_df["sex"] = input_df["sex"].map(sex_mapping)
    
    # Cargar el modelo desde el Model Registry
    model_name = "XGBoost_Best_Deployed"
    model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
    
    # Realizar la predicción
    prediction = model.predict(input_df)
    
    # Invertir el mapeo para la etiqueta de la especie
    species_mapping_inv = {0: "Adelie", 1: "Chinstrap", 2: "Gentoo"}
    predicted_class = int(prediction[0])
    predicted_species = species_mapping_inv.get(predicted_class, "Unknown")
    
    return {"prediction": predicted_species}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)






