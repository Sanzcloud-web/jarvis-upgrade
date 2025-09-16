# -*- coding: utf-8 -*-
import os
import openai
from dotenv import load_dotenv
import requests
from typing import Optional, List, Dict, Any

class OpenAIClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        openai.api_key = self.api_key
        self.conversation_history = []

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Envoie un message à l'API OpenAI et retourne la réponse
        """
        try:
            # Ajouter le message utilisateur à l'historique
            self.conversation_history.append({"role": "user", "content": message})

            # Préparer les messages pour l'API
            messages = []

            # Ajouter le prompt système si fourni
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Ajouter l'historique de conversation
            messages.extend(self.conversation_history)

            # Appel à l'API OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            # Extraire la réponse
            ai_response = response.choices[0].message.content

            # Ajouter la réponse à l'historique
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            return ai_response

        except Exception as e:
            return f"Erreur lors de l'appel à l'API OpenAI: {str(e)}"

    def clear_history(self):
        """
        Efface l'historique de conversation
        """
        self.conversation_history = []

    def web_search(self, query: str) -> str:
        """
        Simule une recherche web (vous pouvez intégrer une vraie API de recherche)
        """
        try:
            # Pour l'instant, on utilise l'IA pour simuler une recherche
            search_prompt = f"L'utilisateur recherche des informations sur: {query}. Fournis des informations générales et utiles sur ce sujet."
            return self.chat(search_prompt)
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"

    def chat_with_web_context(self, message: str, search_query: Optional[str] = None) -> str:
        """
        Chat avec contexte de recherche web
        """
        if search_query:
            web_context = self.web_search(search_query)
            enhanced_message = f"Contexte web: {web_context}\n\nQuestion: {message}"
            return self.chat(enhanced_message)
        else:
            return self.chat(message)