# tools.py

from __future__ import annotations

import os
import base64
from typing import Any, Dict, Optional, Sequence, cast

from dotenv import load_dotenv
from elevenlabs.conversational_ai.conversation import ClientTools
from langchain_community.tools import DuckDuckGoSearchRun
from openai import OpenAI  # SDK OpenAI v1

load_dotenv()


def searchWeb(parameters: Dict[str, Any]) -> str:
    """
    Recherche web via DuckDuckGo (outil LangChain).
    parameters: {"query": "..."}
    Retour: str (résultats/texte agrégé)
    """
    query = str(parameters.get("query", "") or "")
    tool = DuckDuckGoSearchRun()
    return tool.run(query)


def save_to_txt(parameters: Dict[str, Any]) -> str:
    """
    Ajoute 'data' en fin de fichier 'filename'.
    parameters: {"filename": "path/vers/fichier.txt", "data": "contenu"}
    Retour: chemin absolu du fichier écrit.
    """
    filename = parameters.get("filename") or "output.txt"
    data = parameters.get("data") or ""
    folder = os.path.dirname(filename) or "."
    os.makedirs(folder, exist_ok=True)

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{data}\n")

    return os.path.abspath(filename)


def generate_images(parameters: Dict[str, Any]) -> str:
    """
    Génère une image avec OpenAI (DALL·E 3) et l’enregistre en local.
    parameters: {
        "prompt": "Description de l'image",
        "filename": "image.png",
        "size": "1024x1024",
        "save_dir": "images/"
    }
    Retour: chemin absolu du fichier créé.
    """
    prompt = parameters.get("prompt") or ""
    filename = parameters.get("filename") or "image.png"
    size = parameters.get("size") or "1024x1024"
    save_dir = parameters.get("save_dir") or "."

    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)

    # La clé API est lue depuis l'environnement (.env ou variables système)
    client = OpenAI()

    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
        response_format="b64_json",  # base64 -> plus fiable que les URL temporaires
    )

    # Garde-fous pour Pylance/robustesse: valider 'data' avant indexation
    data_any: Optional[object] = getattr(result, "data", None)
    if not isinstance(data_any, (list, tuple)) or len(data_any) == 0:
        raise RuntimeError("Réponse images invalide: champ 'data' manquant ou vide.")

    data: Sequence[Any] = cast(Sequence[Any], data_any)
    first = data[0]

    b64 = getattr(first, "b64_json", None)
    if b64:
        img_bytes = base64.b64decode(b64)
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        return os.path.abspath(filepath)

    # Fallback: certaines réponses historiques contenaient une URL
    url = getattr(first, "url", None)
    if url:
        try:
            import requests  # import local pour éviter une dépendance dure
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return os.path.abspath(filepath)
        except Exception as e:
            raise RuntimeError(f"Pas de base64 et échec du fallback URL: {e}")

    raise RuntimeError("Aucune image exploitable renvoyée (ni base64, ni url).")


# Enregistrement des outils (garde les noms utilisés dans ta vidéo/projet)
client_tools = ClientTools()
client_tools.register("searchWeb", searchWeb)
client_tools.register("saveToTxt", save_to_txt)        # camelCase (compat)
client_tools.register("generateImages", generate_images)
# Alias snake_case si besoin ailleurs
client_tools.register("save_to_txt", save_to_txt)
client_tools.register("generate_images", generate_images)
