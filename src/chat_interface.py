# -*- coding: utf-8 -*-
import sys
import os
from typing import Optional
from .openai_client import OpenAIClient
from .voice_manager import VoiceManager
from .tools.tool_manager import ToolManager
import time

class ChatInterface:
    def __init__(self):
        self.client = OpenAIClient()
        self.voice_manager = None
        self.voice_mode = False
        self.running = True
        
        # Initialiser le gestionnaire d'outils
        self.tool_manager = ToolManager()

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
            print("🗣️ Bonjour ! Je suis JARVIS, votre assistant vocal intelligent.")
            print("🎤 EN ÉCOUTE PERMANENTE - Dites 'JARVIS' pour m'activer !")
            print("💬 Dites 'JARVIS quitter' ou 'JARVIS arrêter le service' pour m'arrêter")
            print("🔄 Dites 'JARVIS mode texte' pour basculer en écriture")
            print("🌐 Dites 'JARVIS recherche ...' pour chercher sur internet")
            print("🛠️ Dites 'JARVIS outils' pour voir tous mes outils disponibles")
            print("🎯 Je ne réponds qu'aux phrases commençant par 'JARVIS'")
            print("🤔 NOUVEAU: Si je pose une question (?), répondez sans redire 'JARVIS' !")

            # Faire parler JARVIS si le mode vocal fonctionne
            if self.voice_manager:
                self.voice_manager.speak("Bonjour ! Je suis JARVIS. Je suis maintenant en écoute permanente. Dites 'jarvis' puis votre demande pour m'activer. Si je vous pose une question, vous pouvez répondre directement !")
        else:
            print("⌨️ Mode texte activé (vocal indisponible)")
            print("Tapez 'quit' ou 'exit' pour quitter")
            print("Tapez 'clear' pour effacer l'historique")
            print("Tapez 'voice' pour réessayer le mode vocal")
            print("Tapez 'outils' pour voir tous les outils disponibles")
            print("Tapez 'test outils' pour tester les fonctionnalités")

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

        if command in ['quit', 'exit', 'quitter', 'au revoir']:
            print("\n👋 Au revoir !")
            if self.voice_mode and self.voice_manager:
                self.voice_manager.speak("Au revoir !")
            self.running = False
            return True

        elif command in ['clear', 'effacer']:
            self.client.clear_history()
            print("\n🗑️ Historique effacé !")
            if self.voice_mode and self.voice_manager:
                self.voice_manager.speak("Historique effacé.")
            return True

        elif command in ['help', 'aide']:
            self.display_help()
            return True

        elif command in ['voice', 'mode texte']:
            self.toggle_voice_mode()
            return True

        elif command in ['test-voice', 'test vocal']:
            self.test_voice_system()
            return True
        
        elif command in ['outils', 'tools', 'aide outils']:
            self.show_tools_help()
            return True
        
        elif command.startswith('outil '):
            tool_name = user_input[6:].strip()
            self.show_tool_help(tool_name)
            return True
        
        elif command == 'test outils':
            self.test_tools()
            return True

        elif command.startswith('recherche '):
            query = user_input[10:].strip()  # Enlever "recherche "
            if query:
                print(f"\n🌐 Recherche: {query}")
                print("⏳ Recherche en cours...")
                if self.voice_mode and self.voice_manager:
                    self.voice_manager.speak(f"Je recherche des informations sur {query}")
                response = self.client.chat(f"Recherche des informations sur: {query}")
                print(f"\n🤖 Résultat: {response}\n")
                if self.voice_mode and self.voice_manager:
                    self.voice_manager.speak(response)
                    
                    # Vérifier si c'est une question pour activer le mode attente
                    if response.strip().endswith('?'):
                        print("🤔 Question détectée - Vous pouvez répondre directement sans dire 'jarvis'")
                        self.voice_manager.enable_response_mode()
            else:
                print("❌ Veuillez spécifier votre recherche après 'recherche'")
                if self.voice_mode and self.voice_manager:
                    self.voice_manager.speak("Veuillez spécifier votre recherche.")
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
    
    def show_tools_help(self):
        """Affiche l'aide des outils disponibles"""
        print("\n🛠️ === OUTILS JARVIS DISPONIBLES ===")
        
        help_data = self.tool_manager.get_tool_help()
        if help_data["success"]:
            print(f"📊 Total: {help_data['total_tools']} outils disponibles\n")
            
            for category, tools in help_data["categories"].items():
                category_names = {
                    "file_operations": "📁 Opérations sur les fichiers",
                    "directory_operations": "📂 Gestion des dossiers", 
                    "text_editor": "📝 Éditeur de texte avancé",
                    "system_commands": "⚙️ Commandes système",
                    "datetime_tools": "🕒 Outils de date/heure",
                    "calculator": "🧮 Calculatrice"
                }
                
                print(f"{category_names.get(category, category.upper())}:")
                for tool in tools:
                    print(f"  • {tool['name']} - {tool['description']}")
                print()
            
            print("💡 Tapez 'outil [nom]' pour plus d'infos sur un outil spécifique")
            print("💡 Tapez 'test outils' pour tester quelques outils")
        else:
            print(f"❌ Erreur: {help_data['error']}")
    
    def show_tool_help(self, tool_name: str):
        """Affiche l'aide pour un outil spécifique"""
        help_data = self.tool_manager.get_tool_help(tool_name)
        
        if help_data["success"]:
            print(f"\n🛠️ === OUTIL: {tool_name.upper()} ===")
            print(f"📂 Catégorie: {help_data['category']}")
            print(f"📝 Description: {help_data['description']}")
            print(f"\n📋 Paramètres:")
            
            for param_name, param_info in help_data["parameters"].items():
                required = " (REQUIS)" if param_name in help_data["required_parameters"] else " (optionnel)"
                print(f"  • {param_name}{required}: {param_info.get('description', 'Pas de description')}")
                if "type" in param_info:
                    print(f"    Type: {param_info['type']}")
        else:
            print(f"❌ Erreur: {help_data['error']}")
    
    def test_tools(self):
        """Teste quelques outils de base"""
        print("\n🧪 === TEST DES OUTILS JARVIS ===")
        
        tests = [
            {
                "name": "Heure actuelle",
                "tool": "get_current_time", 
                "args": {"format": "french"}
            },
            {
                "name": "Calcul simple",
                "tool": "calculate",
                "args": {"expression": "15 + 25 * 2"}
            },
            {
                "name": "Infos système",
                "tool": "get_system_info",
                "args": {}
            },
            {
                "name": "Liste fichiers",
                "tool": "list_files",
                "args": {}
            }
        ]
        
        for test in tests:
            print(f"\n🔍 Test: {test['name']}")
            result = self.tool_manager.execute_tool(test["tool"], test["args"])
            
            if result["success"]:
                print(f"✅ Succès!")
                # Afficher quelques infos clés selon le type de résultat
                if "current_time" in result:
                    print(f"   Heure: {result['current_time']}")
                elif "result" in result:
                    print(f"   Résultat: {result['result']}")
                elif "system_info" in result:
                    info = result["system_info"]
                    print(f"   OS: {info.get('system', 'Inconnu')}")
                    print(f"   Architecture: {info.get('architecture', 'Inconnu')}")
                elif "items" in result:
                    print(f"   {result.get('files_count', 0)} fichiers trouvés")
            else:
                print(f"❌ Échec: {result['error']}")
        
        print(f"\n🎉 Tests terminés! Utilisez 'outils' pour voir tous les outils disponibles.")

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
            
            # Vérifier si JARVIS pose une question pour activer le mode attente
            if response.strip().endswith('?'):
                print("🤔 Question détectée - Vous pouvez répondre directement sans dire 'jarvis'")
                self.voice_manager.enable_response_mode()
            else:
                # S'assurer qu'on est en mode normal si ce n'est pas une question
                if self.voice_manager.is_waiting_for_response():
                    self.voice_manager.disable_response_mode()

        print("-" * 60)

    def handle_voice_command(self, user_input: str):
        """Traite une commande vocale détectée avec le mot-clé JARVIS"""
        print(f"🎯 Commande reçue: {user_input}")
        
        # Vérifier les commandes d'arrêt spéciales
        if any(word in user_input.lower() for word in ['quitter', 'arrêter le service', 'au revoir', 'stop service']):
            print("🔇 Arrêt du service JARVIS...")
            if self.voice_manager:
                self.voice_manager.speak("Au revoir ! Service JARVIS arrêté.")
            self.running = False
            return
            
        # Vérifier si c'est une commande spéciale
        if self.process_command(user_input):
            return

        # Traitement normal du message
        print("⏳ JARVIS réfléchit...")
        try:
            response = self.client.chat(user_input)
            self.display_response(response)
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            if self.voice_manager:
                self.voice_manager.speak("Désolé, j'ai rencontré une erreur. Pouvez-vous répéter ?")
            print("Veuillez réessayer ou vérifier votre configuration.\n")

    def run(self):
        """
        Lance l'interface de chat avec écoute permanente en mode vocal
        """
        self.display_welcome()

        if self.voice_mode and self.voice_manager:
            # Mode vocal : écoute continue permanente
            print("🎤 Écoute permanente activée - En attente de 'JARVIS'...")
            print("📱 Le service fonctionne maintenant en arrière-plan")
            print("💡 Appuyez sur [CTRL+C] pour arrêter le service manuellement")
            print("=" * 60)
            
            try:
                # Lancer l'écoute continue avec callback
                self.voice_manager.listen_continuous(self.handle_voice_command)
                
                # Boucle d'attente tant que le service tourne
                import time
                while self.running:
                    time.sleep(0.5)  # Éviter d'utiliser trop de CPU
                    
            except KeyboardInterrupt:
                print("\n\n🔇 Service JARVIS arrêté manuellement")
                self.running = False
            finally:
                if self.voice_manager:
                    self.voice_manager.stop_listening()
                    
        else:
            # Mode texte : comportement classique
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