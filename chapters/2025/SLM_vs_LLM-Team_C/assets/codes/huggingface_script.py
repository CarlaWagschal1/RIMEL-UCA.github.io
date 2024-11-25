import requests
import pandas as pd
import json
import os.path

# Variables
api_url = "https://huggingface.co/api/models"
headers = {"Authorization": "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"}
params = {"limit": 10}

output_file = "huggingface_models.json"
models = None

# Récupération des données
if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as file:
        models = json.load(file)
else:
    response = requests.get(api_url, headers=headers,params=params)
    models = response.json()
    if response.status_code == 200:
        data = response.json()

        # Sauvegarder les données dans un fichier JSON
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Données sauvegardées dans le fichier '{output_file}'.")
    else:
        print(f"Erreur lors de la requête API : {response.status_code}")


i = 0
for model in models:
    i+=1

print(f"Nombre de modèles : {i}")

models_datas = []

# Extraction des tags principaux
data = []
for model in models:
    data.append({
        "name": model.get("modelId"),
        "type": model.get("pipeline_tag"),
        "downloads": model.get("downloads", 0),
        "likes": model.get("likes", 0),
        "tags": ", ".join(model.get("tags", []))
    })
    response = requests.get(
    "https://huggingface.co/api/models/"+model.get("id"),
    params={"full":"True"},
    headers={"Authorization":"Bearer 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"}
    )
    models_datas.append(response.json())

# Enregistrement des données dans un fichier JSON
with open("models_datas.json", "w", encoding="utf-8") as file:
    json.dump(models_datas, file, ensure_ascii=False, indent=4)

# Création d'un DataFrame pour analyse
df = pd.DataFrame(data)

# Statistiques simples
print("Types de modèles les plus fréquents :")
print(df['type'].value_counts())

print("\nModèles les plus téléchargés :")
print(df.sort_values(by='downloads', ascending=False).head(10))

print("\nTags les plus fréquents :")
print(pd.Series(", ".join(df['tags']).split(", ")).value_counts().head(10))

#
#import matplotlib.pyplot as plt

# Comptage des types de modèles
#type_counts = df['type'].value_counts()

# Graphique
#type_counts.plot(kind='bar', figsize=(10, 6), title="Distribution des types de modèles")
#plt.xlabel("Type de modèle")
#plt.ylabel("Nombre de modèles")
#plt.show()