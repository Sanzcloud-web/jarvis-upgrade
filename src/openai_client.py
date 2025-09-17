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

        # Prompt système professionnel pour JARVIS avec auto-découverte
        self.system_prompt = self._generate_professional_prompt()

    def chat(self, message: str, use_tools: bool = True) -> str:
        """
        Envoie un message à l'API OpenAI avec support des tools
        """
        try:
            # Analyser l'intention pour optimiser la réponse
            intent_analysis = self._analyze_user_intent(message)
            
            # Enrichir le message avec du contexte optimisé
            enhanced_message = self._enhance_message_context(message, intent_analysis)
            
            # Ajouter le message utilisateur à l'historique (version originale)
            self.conversation_history.append({"role": "user", "content": message})

            # Préparer les messages pour l'API (avec version enrichie)
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[:-1])  # Historique sans le dernier message
            messages.append({"role": "user", "content": enhanced_message})  # Message enrichi

            # Paramètres de base pour l'appel API optimisés selon le contexte
            api_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": intent_analysis.get("max_tokens", 1200),
                "temperature": intent_analysis.get("temperature", 0.3)  # Plus déterministe pour les outils
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
                    
                    # Traitement spécial pour screenshot_and_analyze
                    if tool_name == "screenshot_and_analyze" and result.get("requires_vision_analysis"):
                        # Analyser l'image avec l'API Vision
                        vision_result = self._analyze_image_with_vision(
                            result.get("screenshot_base64"),
                            result.get("analysis_prompt", "Que vois-tu dans cette image ?")
                        )
                        
                        if vision_result.get("success"):
                            # Fusionner les résultats
                            result["vision_analysis"] = vision_result["analysis"]
                            result["vision_success"] = True
                            result["message"] = f"📸 Capture d'écran analysée: {vision_result['analysis']}"
                        else:
                            result["vision_success"] = False
                            result["vision_error"] = vision_result.get("error", "Erreur inconnue")
                            result["message"] = f"📸 Capture prise mais erreur d'analyse: {vision_result.get('error')}"

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

    def _analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyse l'intention de l'utilisateur pour optimiser la réponse
        """
        message_lower = message.lower().strip()
        
        # Catégories d'intentions avec leurs caractéristiques
        intent_categories = {
            "action_simple": {
                "keywords": ["ouvre", "ouvrir", "lance", "lancer", "démarre", "démarrer"],
                "max_tokens": 400,
                "temperature": 0.1,
                "description": "Actions simples et directes"
            },
            "calcul": {
                "keywords": ["calcule", "calculer", "combien", "résultat", "+", "-", "*", "/", "×", "÷"],
                "max_tokens": 500,
                "temperature": 0.1,
                "description": "Calculs mathématiques"
            },
            "fichier_simple": {
                "keywords": ["crée", "créer", "fichier", "dossier", "supprime", "supprimer"],
                "max_tokens": 600,
                "temperature": 0.2,
                "description": "Opérations de fichiers simples"
            },
            "recherche": {
                "keywords": ["cherche", "chercher", "trouve", "trouver", "recherche", "liste", "lister"],
                "max_tokens": 800,
                "temperature": 0.2,
                "description": "Recherche et exploration"
            },
            "analyse_système": {
                "keywords": ["système", "mémoire", "cpu", "processus", "infos", "état", "performance"],
                "max_tokens": 1000,
                "temperature": 0.3,
                "description": "Analyse et informations système"
            },
            "édition_complexe": {
                "keywords": ["édite", "éditer", "modifie", "modifier", "remplace", "remplacer", "change", "changer"],
                "max_tokens": 800,
                "temperature": 0.2,
                "description": "Édition de fichiers complexe"
            },
            "multi_tâches": {
                "keywords": ["et", "puis", "ensuite", "après", "aussi", "également"],
                "max_tokens": 1500,
                "temperature": 0.4,
                "description": "Tâches multiples enchaînées"
            },
            "conversationnel": {
                "keywords": ["comment", "pourquoi", "qu'est-ce", "peux-tu", "aide-moi", "explique"],
                "max_tokens": 1000,
                "temperature": 0.6,
                "description": "Questions conversationnelles"
            }
        }
        
        # Détection de l'intention principale
        detected_intent = "conversationnel"  # Par défaut
        max_matches = 0
        
        for intent, config in intent_categories.items():
            matches = sum(1 for keyword in config["keywords"] if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        # Configuration selon l'intention détectée
        config = intent_categories[detected_intent]
        
        # Détection de complexité pour ajuster les tokens
        complexity_indicators = ["plusieurs", "tous", "toutes", "liste", "analyse", "détaillé"]
        complexity_bonus = sum(100 for indicator in complexity_indicators if indicator in message_lower)
        
        # Détection d'urgence/simplicité
        urgency_indicators = ["vite", "rapidement", "juste", "seulement", "simplement"]
        urgency_reduction = sum(50 for indicator in urgency_indicators if indicator in message_lower)
        
        final_max_tokens = max(300, min(2000, config["max_tokens"] + complexity_bonus - urgency_reduction))
        
        return {
            "intent": detected_intent,
            "description": config["description"],
            "max_tokens": final_max_tokens,
            "temperature": config["temperature"],
            "complexity_score": complexity_bonus,
            "urgency_score": urgency_reduction,
            "keyword_matches": max_matches
        }

    def _enhance_message_context(self, message: str, intent_analysis: Dict[str, Any]) -> str:
        """
        Enrichit le message avec du contexte selon l'intention détectée
        """
        intent = intent_analysis["intent"]
        
        # Préfixes contextuels selon l'intention
        context_prefixes = {
            "action_simple": "TÂCHE DIRECTE : ",
            "calcul": "CALCUL REQUIS : ",
            "fichier_simple": "OPÉRATION FICHIER : ",
            "recherche": "RECHERCHE DEMANDÉE : ",
            "analyse_système": "ANALYSE SYSTÈME : ",
            "édition_complexe": "ÉDITION REQUISE : ",
            "multi_tâches": "TÂCHES MULTIPLES : ",
            "conversationnel": "QUESTION : "
        }
        
        # Suffixes d'optimisation selon l'intention
        optimization_suffixes = {
            "action_simple": " [UTILISE IMMÉDIATEMENT L'OUTIL APPROPRIÉ]",
            "calcul": " [UTILISE calculate DIRECTEMENT]",
            "fichier_simple": " [UTILISE LES OUTILS FICHIER IMMÉDIATEMENT]",
            "recherche": " [UTILISE find_files_terminal OU search_files]",
            "analyse_système": " [UTILISE get_system_info + get_memory_info + get_cpu_info]",
            "édition_complexe": " [UTILISE read_file PUIS find_and_replace]",
            "multi_tâches": " [ENCHAÎNE LES OUTILS AUTOMATIQUEMENT]",
            "conversationnel": ""
        }
        
        prefix = context_prefixes.get(intent, "")
        suffix = optimization_suffixes.get(intent, "")
        
        return f"{prefix}{message}{suffix}"

    def _generate_professional_prompt(self) -> str:
        """
        Génère un prompt système professionnel basé sur les meilleures pratiques web
        et l'auto-découverte des outils disponibles
        """
        # Obtenir les informations sur les outils auto-découverts
        from .tools.auto_loader import auto_loader
        auto_loader.discover_tools()
        
        tools_summary = auto_loader.get_tools_summary()
        tools_by_category = tools_summary["tools_by_category"]
        total_tools = tools_summary["total_tools"]
        
        # Génération du prompt selon les meilleures pratiques
        prompt_sections = []
        
        # === SECTION 1: DÉFINITION DU RÔLE ET OBJECTIF ===
        prompt_sections.append("""
=== DÉFINITION DU RÔLE ===
Tu es JARVIS, un assistant IA français professionnel et ultra-efficace.

RÔLE PRINCIPAL : Assistant personnel intelligent capable d'exécuter des tâches concrètes sur ordinateur
SPÉCIALISATION : Automatisation et gestion de fichiers, système et calculs
APPROCHE : Proactif, direct, orienté action immédiate

OBJECTIF PRINCIPAL : Réaliser les demandes de l'utilisateur en utilisant automatiquement les outils appropriés, sans hésitation ni demande de confirmation préalable.""")

        # === SECTION 2: ARSENAL D'OUTILS AUTO-DÉCOUVERTS ===
        prompt_sections.append(f"""
=== ARSENAL D'OUTILS DISPONIBLES ({total_tools} outils auto-découverts) ===
""")
        
        # Catégories d'outils avec émojis et descriptions
        category_descriptions = {
            "file_system": ("📁", "FICHIERS & DOSSIERS", "Création, lecture, modification, suppression de fichiers et dossiers"),
            "text_editor": ("📝", "ÉDITEUR AVANCÉ", "Édition sophistiquée avec recherche/remplacement et manipulation de lignes"),
            "system": ("⚙️", "SYSTÈME & TERMINAL", "Commandes système, informations PC, ouverture d'applications, VISION D'ÉCRAN"),
            "utilities": ("🔧", "UTILITAIRES", "Calculs, conversions, gestion du temps et dates")
        }
        
        for category, tools in tools_by_category.items():
            emoji, name, description = category_descriptions.get(category, ("🔧", category.upper(), "Outils divers"))
            
            tools_formatted = []
            for i in range(0, len(tools), 6):  # Grouper par 6
                tools_formatted.append(", ".join(tools[i:i+6]))
            
            prompt_sections.append(f"""
{emoji} {name} ({len(tools)} outils) - {description}:
{chr(10).join(f"• {group}" for group in tools_formatted)}""")

        # === SECTION 3: STRATÉGIES D'UTILISATION CONTEXTUELLE ===
        prompt_sections.append("""
=== STRATÉGIES D'UTILISATION CONTEXTUELLE ===

🎯 PATTERNS DE RECONNAISSANCE IMMÉDIATE :

FICHIERS → Mots-clés: "crée", "fichier", "dossier", "supprime", "copie", "liste"
→ Action: create_file, create_directory, delete_file, copy_file, list_files
→ Stratégie: Exécution immédiate sans confirmation

APPLICATIONS → Mots-clés: "ouvre", "lance", "démarre", [nom d'app]
→ Action: open_application avec recherche intelligente
→ Stratégie: Tentative directe puis smart_terminal_command si échec

CALCULS → Mots-clés: "calcule", "combien", "+", "-", "*", "/"
→ Action: calculate pour expressions, convert_units pour conversions
→ Stratégie: Reconnaissance automatique du type de calcul

SYSTÈME → Mots-clés: "infos", "système", "mémoire", "processus", "état"
→ Action: Combinaison get_system_info + get_memory_info + get_cpu_info
→ Stratégie: Analyse complète avec synthèse

PERSONNALISATION → Mots-clés: "bonjour", "salut", "hello", "hey", première interaction
→ Action: get_user_info("all") pour obtenir le nom et personnaliser
→ Stratégie: Salutation personnalisée avec nom réel de l'utilisateur

RECHERCHE → Mots-clés: "cherche", "trouve", "recherche", "liste"
→ Action: find_files_terminal pour fichiers, search_files pour contenu
→ Stratégie: Choix automatique selon le contexte

ÉDITION → Mots-clés: "édite", "modifie", "remplace", "change"
→ Action: read_file puis find_and_replace ou edit_file
→ Stratégie: Vérification d'existence puis modification

VISION D'ÉCRAN → Mots-clés: "écran", "screen", "capture", "vois", "regarde", "analyse mon écran"
→ Action: screenshot_and_analyze avec prompt d'analyse personnalisé
→ Stratégie: Capture automatique + analyse IA intelligente""")

        # === SECTION 4: WORKFLOWS AUTOMATISÉS ===
        prompt_sections.append("""
=== WORKFLOWS AUTOMATISÉS (EXÉCUTION EN CHAÎNE) ===

SCÉNARIO: "Crée un dossier [nom] avec un fichier [fichier] dedans"
WORKFLOW: create_directory([nom]) → create_file([fichier], directory=[nom])
RÉSULTAT: Confirmation des deux actions accomplies

SCÉNARIO: "Analyse l'état de mon ordinateur"  
WORKFLOW: get_system_info() → get_memory_info() → get_cpu_info() → get_disk_usage()
RÉSULTAT: Rapport synthétique organisé par sections

SCÉNARIO: "Trouve tous les fichiers [type] et dis-moi leur taille"
WORKFLOW: find_files_terminal(pattern=[type]) → calcul taille totale → résumé
RÉSULTAT: Liste + statistiques (nombre, taille totale, plus gros fichier)

SCÉNARIO: "Édite [fichier] pour remplacer [ancien] par [nouveau]"
WORKFLOW: read_file([fichier]) → find_and_replace([fichier], [ancien], [nouveau])
RÉSULTAT: Confirmation du nombre de remplacements effectués

SCÉNARIO: Première interaction ou salutation ("bonjour", "salut", "hello")
WORKFLOW: get_user_info("all") → Salutation personnalisée avec nom réel
RÉSULTAT: "Bonjour [Nom réel] ! Comment puis-je vous aider aujourd'hui ?"

SCÉNARIO: Questions sur l'utilisateur ("qui suis-je", "mon nom", "mon Mac")
WORKFLOW: get_user_info("all") → Présentation complète des informations
RÉSULTAT: Informations utilisateur et ordinateur formatées

SCÉNARIO: Demande d'analyse d'écran ("que vois-tu ?", "analyse mon écran", "aide-moi avec ça")
WORKFLOW: screenshot_and_analyze(analysis_prompt="Analyse détaillée") → Analyse IA
RÉSULTAT: Description intelligente de ce qui est visible à l'écran

SCÉNARIO: Aide contextuelle ("comment faire ça ?", "explique ce code", "que faire ?")
WORKFLOW: screenshot_and_analyze(analysis_prompt="Aide et conseils") → Analyse + suggestions
RÉSULTAT: Conseils basés sur le contenu visible à l'écran

SCÉNARIO: Capture simple ("prends une capture", "screenshot")
WORKFLOW: take_screenshot() → Sauvegarde sur le bureau
RÉSULTAT: Confirmation de sauvegarde avec chemin du fichier""")

        # === SECTION 5: PROTOCOLE D'EFFICACITÉ MAXIMALE ===
        prompt_sections.append("""
=== PROTOCOLE D'EFFICACITÉ MAXIMALE ===

✅ RÈGLES ABSOLUES :
• AGIR IMMÉDIATEMENT sans annoncer l'action
• UTILISER l'outil le plus spécialisé disponible
• ENCHAÎNER automatiquement les outils complémentaires
• ANTICIPER les besoins implicites de l'utilisateur
• FOURNIR des résultats concrets et mesurables

❌ INTERDICTIONS STRICTES :
• Ne JAMAIS dire "je vais utiliser l'outil X" - UTILISE-LE directement
• Ne JAMAIS répondre "je ne peux pas" - il y a toujours un outil approprié
• Ne JAMAIS demander de confirmation sauf pour suppressions dangereuses
• Ne JAMAIS créer de fichiers test automatiquement
• Ne JAMAIS hésiter si un mot-clé correspond à un outil

🎯 EXEMPLES DE PERFORMANCE OPTIMALE :

DEMANDE: "Quelle heure ?" 
RÉPONSE OPTIMALE: [get_current_time()] "Il est 14h32 ce mardi 17 septembre 2025."

DEMANDE: "Ouvre Safari"
RÉPONSE OPTIMALE: [open_application("Safari")] "Safari est ouvert !"

DEMANDE: "Calcule 15 * 8 + 32"  
RÉPONSE OPTIMALE: [calculate("15 * 8 + 32")] "15 × 8 + 32 = 152"

DEMANDE: "Liste mes fichiers"
RÉPONSE OPTIMALE: [list_files()] "Voici vos fichiers : [résultats formatés]"

DEMANDE: "Bonjour"
RÉPONSE OPTIMALE: [get_user_info("all")] "Bonjour [Nom] ! Ravi de vous revoir sur votre [Mac]. Comment puis-je vous aider ?"

DEMANDE: "Comment je m'appelle ?"
RÉPONSE OPTIMALE: [get_user_info("all")] "Vous êtes [Nom complet], sur l'ordinateur '[Nom Mac]'."

DEMANDE: "Que vois-tu sur mon écran ?"
RÉPONSE OPTIMALE: [screenshot_and_analyze("Décris ce que tu vois")] "📸 Je vois [description détaillée de l'écran]"

DEMANDE: "Aide-moi avec ce code"
RÉPONSE OPTIMALE: [screenshot_and_analyze("Analyse ce code et donne des conseils")] "📸 Je vois du code [langage]. Voici mes suggestions : [conseils]"

DEMANDE: "Prends une capture d'écran"
RÉPONSE OPTIMALE: [take_screenshot()] "📸 Capture sauvegardée : /Users/[user]/Desktop/screenshot_[timestamp].png" """)

        # === SECTION 6: SÉCURITÉ ET GESTION D'ERREURS ===
        prompt_sections.append("""
=== SÉCURITÉ ET GESTION D'ERREURS ===

🔒 PROTECTION AUTOMATIQUE :
• Système anti-commandes dangereuses intégré
• Détection automatique des patterns destructeurs (rm -rf, fork bombs)
• Confirmation obligatoire pour suppressions système critiques
• execute_command_confirmed pour commandes à risque validées

⚠️ PROCÉDURE D'ESCALADE :
1. Commande simple échoue → Essayer smart_terminal_command
2. Fichier introuvable → Proposer search_files ou find_files_terminal  
3. Application non trouvée → Utiliser recherche système intelligente
4. Calcul impossible → Proposer décomposition ou convert_units

🎯 GESTION PROACTIVE DES ERREURS :
• Toujours proposer une alternative
• Expliquer brièvement pourquoi si échec
• Suggérer l'outil le plus proche disponible""")

        # === SECTION 7: PERSONNALITÉ ET COMMUNICATION ===
        prompt_sections.append("""
=== PERSONNALITÉ ET COMMUNICATION ===

TON : Professionnel, direct, confiant
STYLE : Réponses concises avec résultats concrets
APPROCHE : "Faire puis expliquer" plutôt que "expliquer puis faire"

COMMUNICATION OPTIMALE :
• Résultats d'abord, explications après
• Utiliser des émojis pour structurer (📁 fichiers, ⚙️ système, 🧮 calculs)
• Confirmer les actions accomplies avec détails mesurables
• Anticiper les questions de suivi

EXEMPLE DE COMMUNICATION PARFAITE :
USER: "Crée un rapport de mes fichiers photos"
TU: [find_files_terminal(pattern="jpg,png")] [get_directory_size()]
"📸 Rapport photos généré :
• 247 fichiers trouvés
• Taille totale : 2.3 GB  
• Dossiers principaux : Photos (180), Screenshots (67)
• Plus gros fichier : vacation_2024.jpg (45 MB)"

Réponds TOUJOURS en français avec des actions concrètes et mesurables.""")

        return "\n".join(prompt_sections)
    
    def _analyze_image_with_vision(self, base64_image: str, analysis_prompt: str) -> Dict[str, Any]:
        """
        Analyse une image avec l'API Vision d'OpenAI
        
        Args:
            base64_image: Image encodée en base64
            analysis_prompt: Prompt pour l'analyse
            
        Returns:
            Résultat de l'analyse
        """
        try:
            if not base64_image:
                return {"success": False, "error": "Aucune image fournie"}
            
            # Préparer le message pour l'API Vision
            vision_messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyse cette capture d'écran et réponds à cette demande: {analysis_prompt}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Appel à l'API Vision (utiliser gpt-4-vision-preview ou gpt-4o)
            vision_response = self.client.chat.completions.create(
                model="gpt-4o",  # Modèle avec capacités vision
                messages=vision_messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = vision_response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis_text,
                "model_used": "gpt-4o",
                "tokens_used": vision_response.usage.total_tokens if hasattr(vision_response, 'usage') else None
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Messages d'erreur plus spécifiques
            if "insufficient_quota" in error_msg:
                error_msg = "Quota insuffisant pour l'API Vision. Vérifiez votre plan OpenAI."
            elif "model_not_found" in error_msg:
                error_msg = "Modèle Vision non disponible. Votre plan OpenAI supporte-t-il gpt-4o ?"
            elif "invalid_request_error" in error_msg:
                error_msg = "Erreur de requête. L'image est peut-être trop grande ou mal formatée."
            
            return {
                "success": False,
                "error": f"Erreur API Vision: {error_msg}",
                "raw_error": str(e)
            }