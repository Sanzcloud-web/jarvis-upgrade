# -*- coding: utf-8 -*-
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from .tools import ToolManager

class OpenAIClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []

        # Initialiser le gestionnaire d'outils
        self.tool_manager = ToolManager()
        self.tools = self.tool_manager.get_all_tools_schema()

        # Prompt système pour JARVIS
        self.system_prompt = """Tu es JARVIS, un assistant IA français intelligent et serviable.

CAPACITÉS DISPONIBLES :
- 📁 Gestion complète des fichiers et dossiers (créer, éditer, déplacer, supprimer, etc.)
- 📝 Éditeur de texte avancé (recherche/remplacement, insertion de lignes, etc.)  
- ⚙️ Commandes système (informations PC, mémoire, processus, ouvrir applications/URLs)
- 🕒 Outils de date/heure (calendrier, calculs d'âge, ajouts de temps)
- 🧮 Calculatrice avancée (expressions mathématiques, conversions d'unités, pourcentages)

INSTRUCTIONS IMPORTANTES :
1. Tu peux utiliser PLUSIEURS outils en séquence pour accomplir des tâches complexes
2. Pour ouvrir des applications, utilise execute_command avec des commandes de recherche intelligente
3. Utilise execute_command pour des tâches système flexibles (recherche de fichiers, etc.)
4. Ne crée jamais de fichiers de test automatiquement - seulement si l'utilisateur le demande explicitement
5. Sois proactif : si l'utilisateur demande "crée un dossier avec un fichier dedans", fais les deux actions

EXEMPLES D'UTILISATION MULTI-OUTILS :
- "Crée un dossier 'test' avec un fichier 'histoire.txt' dedans" → create_directory puis create_file
- "Trouve et ouvre Chrome" → execute_command pour chercher puis execute_command pour ouvrir
- "Montre-moi les gros fichiers du bureau" → list_files puis filtrage

Réponds toujours en français avec des explications claires de ce que tu fais."""

    def chat(self, message: str, use_tools: bool = True) -> str:
        """
        Envoie un message à l'API OpenAI avec support des tools
        """
        try:
            # Ajouter le message utilisateur à l'historique
            self.conversation_history.append({"role": "user", "content": message})

            # Préparer les messages pour l'API
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history)

            # Paramètres de base pour l'appel API
            api_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }

            # Ajouter les tools si activés
            if use_tools:
                api_params["tools"] = self.tools
                api_params["tool_choice"] = "auto"

            # Appel à l'API OpenAI
            response = self.client.chat.completions.create(**api_params)

            # Vérifier si l'IA veut utiliser des outils
            message_obj = response.choices[0].message

            if message_obj.tool_calls:
                # Traiter les appels d'outils
                for tool_call in message_obj.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Exécuter l'outil
                    result = self.tool_manager.execute_tool(tool_name, tool_args)

                    # Ajouter l'appel d'outil à l'historique
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call.model_dump()]
                    })

                    # Ajouter le résultat de l'outil à l'historique
                    self.conversation_history.append({
                        "role": "tool",
                        "content": json.dumps(result, ensure_ascii=False),
                        "tool_call_id": tool_call.id
                    })

                # Faire un second appel pour obtenir la réponse finale
                messages = [{"role": "system", "content": self.system_prompt}]
                messages.extend(self.conversation_history)

                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )

                ai_response = final_response.choices[0].message.content
            else:
                # Réponse simple sans outils
                ai_response = message_obj.content

            # Ajouter la réponse finale à l'historique
            if ai_response:
                self.conversation_history.append({"role": "assistant", "content": ai_response})

            return ai_response or "J'ai exécuté votre demande."

        except Exception as e:
            return f"Erreur lors de l'appel à l'API OpenAI: {str(e)}"

    def clear_history(self):
        """
        Efface l'historique de conversation
        """
        self.conversation_history = []