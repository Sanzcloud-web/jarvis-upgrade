#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Assistant IA avec OpenAI
Interface de chat simple pour conversations avec l'IA
"""

import sys
import os
from src.chat_interface import ChatInterface

def main():
    """
    Point d'entr�e principal du programme
    """
    try:
        # Cr�er et lancer l'interface de chat
        chat = ChatInterface()
        chat.run()

    except KeyboardInterrupt:
        print("\n\n=K Programme interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"L Erreur fatale: {str(e)}")
        print("V�rifiez votre fichier .env et votre connexion internet")
        sys.exit(1)

if __name__ == "__main__":
    main()