from langchain_community.document_loaders import PyMuPDFLoader  # Pour charger le fichier PDF
from langchain_ollama import OllamaLLM  # Pour utiliser un modèle LLM local via Ollama
from langchain.prompts import PromptTemplate  # Pour créer un prompt structuré pour le modèle
import json  # Pour travailler avec des objets JSON
import re  # Pour faire du nettoyage de texte avec des expressions régulières


def analyze_resume(file_path):
    # --- Étape 1 : Charger le fichier PDF ---
    loader = PyMuPDFLoader(file_path)
    docs = list(loader.lazy_load())  # On lit toutes les pages du CV dans une liste

    # --- Étape 2 : Préparer le modèle local ---
    llm = OllamaLLM(model="mistral")  # Modèle Ollama local

    # --- Étape 3 : Créer le prompt que l’on envoie au modèle ---
    prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
You are an expert career coach and resume analyst.

Given the resume below (which may be in any format), extract the following key information and return it as a clean JSON object:

{{
  "job_title": "...",
  "full_name": "...",
  "email": "...",
  "top_skills": ["...", "...", "..."],
  "experiences": [
    {{
      "job_title": "...",
      "company": "...",
      "years": "..."
    }}
  ],
  "education": [
    {{
      "degree": "...",
      "field": "...",
      "university": "..."
    }}
  ]
}}

⚠️ Important: Only return a valid JSON object. No comments, no extra text, no formatting.

---

Resume:
{resume_text}
        """
    )

    # --- Étape 4 : Interroger le modèle avec le contenu du CV ---
    chain = prompt | llm
    response = chain.invoke({"resume_text": docs[0].page_content}).strip()

    # --- Debug : afficher la réponse brute du modèle ---
    print("🔍 Raw LLM response:")
    print(response)

    try:
        # --- Étape 5 : Tenter de parser la réponse JSON ---
        data = json.loads(response)

        # On récupère le titre du poste tel que renvoyé par le modèle
        raw_title = data.get("job_title", "").strip()

        if raw_title:
            # Nettoyage : suppression de certains mots (optionnel)
            cleaned_title = re.sub(
                r"\b(senior|junior|freelance|expert|engineer|specialist)\b", "", raw_title.lower()
            ).strip()

            # Si le nettoyage supprime tout → on garde le titre brut
            job_keyword = cleaned_title or raw_title.lower()
        else:
            job_keyword = ""  # Si aucun titre trouvé, on retourne une chaîne vide

    except json.JSONDecodeError:
        # En cas d’erreur JSON, on retourne des données vides
        data = {}
        job_keyword = ""

    # --- Étape 6 : Retourner les données au format attendu ---
    return {
        "raw_profile": json.dumps(data, indent=2),  # JSON formaté pour affichage dans Streamlit
        "job_keyword": job_keyword  # Titre nettoyé utilisable pour rechercher des offres
    }
