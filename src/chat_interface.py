# -*- coding: utf-8 -*-
import sys
import os
from typing import Optional
from .openai_client import OpenAIClient
from .voice_manager import VoiceManager

class ChatInterface:
    def __init__(self):
        self.client = OpenAIClient()
        self.voice_manager = None
        self.voice_mode = False
        self.running = True

        # Initialiser automatiquement le mode vocal
        self.auto_init_voice()

    def auto_init_voice(self):
        """Initialise automatiquement le mode vocal au démarrage"""
        print("🔄 Initialisation automatique du mode vocal...")

        if self.init_voice_manager():
            self.voice_mode = True
            print("✅ Mode vocal activé par défaut !")
            print("💡 Tapez 'text' pour basculer en mode texte si nécessaire")
        else:
            print("⚠️ Impossible d'activer le mode vocal - basculement en mode texte")
            self.voice_mode = False

    def display_welcome(self):
        """
        Affiche le message de bienvenue
        """
        print("=" * 60)
        print("🎤 JARVIS - Assistant IA Vocal")
        print("=" * 60)

        if self.voice_mode:
            print("🗣️ Bonjour ! Je suis JARVIS, votre assistant vocal.")
            print("🎤 PARLEZ-MOI directement - je vous écoute !")
            print("💬 Dites 'quitter' ou 'au revoir' pour arrêter")
            print("🔄 Dites 'mode texte' pour basculer en écriture")
            print("🌐 Dites 'recherche' suivi de votre question pour chercher sur internet")

            # Faire parler JARVIS si le mode vocal fonctionne
            if self.voice_manager:
                self.voice_manager.speak("Bonjour ! Je suis JARVIS, votre assistant vocal. Vous pouvez me parler directement !")
        else:
            print("⌨️ Mode texte activé (vocal indisponible)")
            print("Tapez 'quit' ou 'exit' pour quitter")
            print("Tapez 'clear' pour effacer l'historique")
            print("Tapez 'voice' pour réessayer le mode vocal")

        print("-" * 60)

    def display_help(self):
        """
        Affiche l'aide
        """
        print("\n📋 Commandes disponibles:")
        print("  • quit/exit     - Quitter le programme")
        print("  • clear         - Effacer l'historique de conversation")
        print("  • voice         - Activer/désactiver le mode vocal")
        print("  • test-voice    - Tester le système vocal")
        print("  • web: [query]  - Rechercher des infos sur internet")
        print("  • help          - Afficher cette aide")
        print()
        if self.voice_mode:
            print("🎤 Mode vocal ACTIVÉ - Parlez pour interagir!")
        else:
            print("⌨️ Mode texte - Tapez pour interagir")

    def process_command(self, user_input: str) -> bool:
        """
        Traite les commandes spéciales
        Retourne True si c'est une commande, False sinon
        """
        command = user_input.lower().strip()

        if command in ['quit', 'exit']:
            print("\n👋 Au revoir !")
            self.running = False
            return True

        elif command == 'clear':
            self.client.clear_history()
            print("\n🗑️ Historique effacé !")
            return True

        elif command == 'help':
            self.display_help()
            return True

        elif command == 'voice':
            self.toggle_voice_mode()
            return True

        elif command == 'test-voice':
            self.test_voice_system()
            return True

        elif command.startswith('web:'):
            query = user_input[4:].strip()
            if query:
                print(f"\n🌐 Recherche: {query}")
                print("⏳ Recherche en cours...")
                response = self.client.chat(f"Recherche des informations sur: {query}")
                print(f"\n🤖 Résultat: {response}\n")
            else:
                print("❌ Veuillez spécifier votre recherche après 'web:'")
            return True

        return False

    def init_voice_manager(self):
        """Initialise le gestionnaire vocal"""
        try:
            if self.voice_manager is None:
                print("🔄 Initialisation du système vocal...")
                self.voice_manager = VoiceManager()
                print("✅ Système vocal initialisé !")
            return True
        except Exception as e:
            print(f"❌ Erreur initialisation vocal: {e}")
            print("Vérifiez que vous avez un microphone connecté et les dépendances installées")
            return False

    def toggle_voice_mode(self):
        """Active/désactive le mode vocal"""
        if not self.init_voice_manager():
            return

        self.voice_mode = not self.voice_mode

        if self.voice_mode:
            print("🎤 Mode vocal ACTIVÉ")
            self.voice_manager.speak("Mode vocal activé. Vous pouvez maintenant me parler!")
        else:
            print("⌨️ Mode vocal DÉSACTIVÉ - retour au mode texte")
            if self.voice_manager:
                self.voice_manager.speak("Mode vocal désactivé")

    def test_voice_system(self):
        """Teste le système vocal"""
        if not self.init_voice_manager():
            return

        print("\n🧪 Test du système vocal...")
        success = self.voice_manager.test_voice()

        if success:
            print("✅ Système vocal opérationnel !")
        else:
            print("❌ Problème avec le système vocal")

    def get_voice_input(self) -> str:
        """Récupère l'entrée vocale"""
        if not self.voice_manager:
            return ""

        print("🎤 Parlez maintenant...")
        result = self.voice_manager.listen_once(timeout=10)
        return result if result else ""

    def get_user_input(self) -> str:
        """
        Récupère l'entrée utilisateur avec gestion des erreurs
        """
        try:
            if self.voice_mode:
                # Mode vocal
                return self.get_voice_input()
            else:
                # Mode texte
                return input("🗣️  Vous: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            self.running = False
            return ""
        except EOFError:
            self.running = False
            return ""

    def display_response(self, response: str):
        """
        Affiche la réponse de l'IA
        """
        print(f"\n🤖 JARVIS: {response}\n")

        # En mode vocal, faire parler JARVIS
        if self.voice_mode and self.voice_manager:
            self.voice_manager.speak(response)

        print("-" * 60)

    def run(self):
        """
        Lance l'interface de chat
        """
        self.display_welcome()

        while self.running:
            user_input = self.get_user_input()

            if not user_input or not self.running:
                break

            # Vérifier si c'est une commande spéciale
            if self.process_command(user_input):
                continue

            # Traitement normal du message
            print("⏳ JARVIS réfléchit...")
            try:
                response = self.client.chat(user_input)
                self.display_response(response)
            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
                print("Veuillez réessayer ou vérifier votre configuration.\n")

    def run_single_query(self, query: str) -> str:
        """
        Exécute une seule requête (utile pour les tests ou l'intégration)
        """
        try:
            return self.client.chat(query)
        except Exception as e:
            return f"Erreur: {str(e)}"