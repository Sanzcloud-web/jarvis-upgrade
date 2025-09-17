# -*- coding: utf-8 -*-
"""
Gestionnaire de sécurité pour les commandes système
Détecte et protège contre les commandes dangereuses
"""

import re
import os
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from ...utils.system_utils import system_detector, SystemType

class SecurityManager:
    def __init__(self):
        """Initialise le gestionnaire de sécurité"""
        self.system_detector = system_detector
        
        # Patterns de commandes absolument interdites
        self.forbidden_patterns = [
            # Fork bombs et attaques
            r':\(\)\{.*\|.*&.*\}.*:',  # Fork bomb bash :(){ :|:& };:
            r'while\s*true.*do.*done',  # Boucles infinies
            r'yes\s*\|.*',  # Spam de sortie
            
            # Formatage et destruction massive
            r'mkfs\.',  # Formatage de disques
            r'dd\s+if=/dev/zero',  # Effacement de disques
            r'dd\s+if=/dev/urandom',  # Remplissage aléatoire
            r'shred\s+-.*',  # Destruction sécurisée
            
            # Modification système critique
            r'chmod\s+000\s+/',  # Suppression permissions racine
            r'chown\s+.*\s+/',  # Changement propriétaire racine
            r'mount.*bind.*/',  # Montage dangereux
            r'umount\s+-f\s*/',  # Démontage forcé
            
            # Réseau et firewall
            r'iptables\s+-F',  # Flush firewall
            r'netsh\s+firewall.*disable',  # Désactiver firewall Windows
            r'systemctl\s+stop\s+firewall',  # Arrêt firewall Linux
            
            # Historique et logs
            r'history\s+-c',  # Effacement historique
            r'>\s*/var/log/',  # Vidage logs système
            r'truncate.*-s\s*0.*\.log',  # Troncature logs
            
            # Modification de fichiers système critiques
            r'>\s*/etc/passwd',  # Écrasement fichier utilisateurs
            r'>\s*/etc/shadow',  # Écrasement mots de passe
            r'>\s*/boot/',  # Modification boot
            
            # Téléchargements et exécutions suspectes
            r'curl.*\|\s*sh',  # Téléchargement et exécution directe
            r'wget.*\|\s*sh',  # Téléchargement et exécution directe
            r'curl.*\|\s*bash',  # Téléchargement et exécution bash
            r'wget.*\|\s*bash',  # Téléchargement et exécution bash
        ]
        
        # Patterns nécessitant confirmation
        self.confirmation_patterns = [
            # Suppressions multiples
            r'rm\s+.*-r.*\*',  # rm -r avec wildcard
            r'rm\s+.*-rf.*',  # rm -rf
            r'rmdir\s+.*-rf.*',  # rmdir récursif
            
            # Suppressions système
            r'rm\s+.*/(bin|sbin|etc|usr|var|opt)/',  # Dossiers système
            r'del\s+/[sSqQ].*',  # Suppression Windows silencieuse
            
            # Modifications critiques
            r'sudo\s+rm\s+',  # Suppression avec sudo
            r'sudo\s+chmod\s+',  # Modification permissions avec sudo
            r'sudo\s+chown\s+',  # Changement propriétaire avec sudo
            
            # Base de données
            r'DROP\s+DATABASE',  # Suppression base de données
            r'TRUNCATE\s+TABLE',  # Vidage table
        ]
        
        # Extensions de fichiers à surveiller spécialement
        self.critical_extensions = [
            '.exe', '.app', '.dmg', '.pkg', '.deb', '.rpm',
            '.sh', '.bat', '.ps1', '.py', '.js', '.php',
            '.sql', '.db', '.sqlite', '.mdb'
        ]

    def analyze_command(self, command: str) -> Dict[str, Any]:
        """
        Analyse une commande pour détecter les risques de sécurité
        
        Args:
            command: Commande à analyser
            
        Returns:
            Dictionnaire avec l'analyse de sécurité
        """
        analysis = {
            "is_safe": True,
            "risk_level": "low",  # low, medium, high, critical
            "issues": [],
            "requires_confirmation": False,
            "confirmation_message": "",
            "blocked": False,
            "suggestions": []
        }
        
        command_lower = command.lower().strip()
        
        # 1. Vérifier les patterns absolument interdits
        for pattern in self.forbidden_patterns:
            if re.search(pattern, command_lower, re.IGNORECASE):
                analysis["blocked"] = True
                analysis["is_safe"] = False
                analysis["risk_level"] = "critical"
                analysis["issues"].append(f"Commande interdite détectée: pattern dangereux")
                analysis["suggestions"].append("Cette commande est bloquée pour votre sécurité")
                return analysis
        
        # 2. Vérifier les patterns nécessitant confirmation
        for pattern in self.confirmation_patterns:
            if re.search(pattern, command_lower, re.IGNORECASE):
                analysis["requires_confirmation"] = True
                analysis["is_safe"] = False
                analysis["risk_level"] = "high"
                analysis["issues"].append("Commande potentiellement destructrice")
                break
        
        # 3. Analyse spécifique des commandes de suppression
        deletion_analysis = self._analyze_deletion_command(command)
        if deletion_analysis["is_deletion"]:
            analysis.update(deletion_analysis)
        
        # 4. Vérifier les privilèges élevés
        privilege_analysis = self._analyze_privileges(command)
        if privilege_analysis["elevated"]:
            if analysis["risk_level"] == "low":
                analysis["risk_level"] = "medium"
            analysis["issues"].extend(privilege_analysis["issues"])
        
        # 5. Analyser les wildcards dangereux
        wildcard_analysis = self._analyze_wildcards(command)
        if wildcard_analysis["dangerous"]:
            analysis["issues"].extend(wildcard_analysis["issues"])
            if analysis["risk_level"] in ["low", "medium"]:
                analysis["risk_level"] = "high"
                analysis["requires_confirmation"] = True
        
        return analysis

    def _analyze_deletion_command(self, command: str) -> Dict[str, Any]:
        """Analyse spécifique des commandes de suppression"""
        analysis = {
            "is_deletion": False,
            "target_paths": [],
            "recursive": False,
            "confirmation_message": ""
        }
        
        # Patterns de suppression par OS
        deletion_patterns = {
            "unix": [
                r'rm\s+(.+)',
                r'rmdir\s+(.+)',
                r'unlink\s+(.+)',
            ],
            "windows": [
                r'del\s+(.+)',
                r'erase\s+(.+)',
                r'rd\s+(.+)',
                r'rmdir\s+(.+)',
            ]
        }
        
        # Choisir les patterns selon l'OS
        if self.system_detector.is_windows:
            patterns = deletion_patterns["windows"]
        else:
            patterns = deletion_patterns["unix"]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                analysis["is_deletion"] = True
                targets = match.group(1).strip()
                
                # Analyser les options
                if re.search(r'-r|--recursive|/s', command, re.IGNORECASE):
                    analysis["recursive"] = True
                
                # Extraire les chemins cibles
                analysis["target_paths"] = self._extract_target_paths(targets)
                
                # Générer le message de confirmation
                analysis["confirmation_message"] = self._generate_deletion_confirmation(
                    analysis["target_paths"], 
                    analysis["recursive"]
                )
                
                break
        
        return analysis

    def _extract_target_paths(self, targets_string: str) -> List[str]:
        """Extrait les chemins cibles d'une chaîne de commande"""
        # Supprimer les options courantes
        options_to_remove = ['-r', '-f', '-rf', '-fr', '--recursive', '--force', '/s', '/q']
        
        cleaned = targets_string
        for option in options_to_remove:
            cleaned = re.sub(rf'\s*{re.escape(option)}\s*', ' ', cleaned, flags=re.IGNORECASE)
        
        # Diviser par espaces et nettoyer
        paths = []
        for path in cleaned.split():
            path = path.strip('\'"')  # Supprimer les guillemets
            if path and not path.startswith('-'):  # Ignorer les options restantes
                paths.append(path)
        
        return paths

    def _generate_deletion_confirmation(self, paths: List[str], recursive: bool) -> str:
        """Génère un message de confirmation pour la suppression"""
        if not paths:
            return "Êtes-vous sûr de vouloir exécuter cette commande de suppression ?"
        
        type_text = "récursivement" if recursive else ""
        
        if len(paths) == 1:
            path = paths[0]
            # Résoudre le chemin absolu si possible
            try:
                abs_path = os.path.abspath(os.path.expanduser(path))
                return f"Êtes-vous sûr de vouloir supprimer {type_text} '{path}' ?\nChemin complet: {abs_path}"
            except:
                return f"Êtes-vous sûr de vouloir supprimer {type_text} '{path}' ?"
        else:
            paths_text = "', '".join(paths[:3])
            if len(paths) > 3:
                paths_text += f"' et {len(paths) - 3} autres"
            else:
                paths_text += "'"
            
            return f"Êtes-vous sûr de vouloir supprimer {type_text} '{paths_text} ?"

    def _analyze_privileges(self, command: str) -> Dict[str, Any]:
        """Analyse les privilèges élevés dans la commande"""
        analysis = {
            "elevated": False,
            "issues": []
        }
        
        # Mots-clés de privilèges élevés
        privilege_keywords = ['sudo', 'su -', 'runas', 'powershell -command']
        
        command_lower = command.lower()
        for keyword in privilege_keywords:
            if keyword in command_lower:
                analysis["elevated"] = True
                analysis["issues"].append(f"Commande avec privilèges élevés: {keyword}")
        
        return analysis

    def _analyze_wildcards(self, command: str) -> Dict[str, Any]:
        """Analyse les wildcards potentiellement dangereux"""
        analysis = {
            "dangerous": False,
            "issues": []
        }
        
        # Patterns de wildcards dangereux
        dangerous_wildcards = [
            r'\*\s*/',  # /* - racine
            r'/\*',     # Wildcard sur racine
            r'\.\*',    # .* - fichiers cachés
            r'\*\*',    # ** - récursif global
        ]
        
        # Vérifier si c'est une commande de suppression avec wildcard
        if re.search(r'(rm|del|erase)\s+.*\*', command, re.IGNORECASE):
            for pattern in dangerous_wildcards:
                if re.search(pattern, command):
                    analysis["dangerous"] = True
                    analysis["issues"].append("Wildcard dangereux dans commande de suppression")
                    break
        
        return analysis

    def request_user_confirmation(self, message: str) -> bool:
        """
        Demande confirmation à l'utilisateur
        Dans un contexte réel, ceci serait connecté à l'interface utilisateur
        """
        print(f"\n⚠️  CONFIRMATION REQUISE ⚠️")
        print(f"🔸 {message}")
        print(f"🔸 Tapez 'oui' pour confirmer ou 'non' pour annuler:")
        
        # Dans un contexte réel avec interface, ceci retournerait la réponse de l'utilisateur
        # Pour l'instant, on retourne False par sécurité
        return False

    def get_safe_alternative(self, command: str) -> Optional[str]:
        """Propose une alternative plus sûre pour une commande dangereuse"""
        command_lower = command.lower()
        
        alternatives = {
            "rm -rf /": "Utilisez des outils de suppression plus spécifiques",
            "rm -rf *": "Listez d'abord les fichiers avec 'ls', puis supprimez spécifiquement",
            "chmod 777": "Utilisez des permissions plus restrictives comme 'chmod 755'",
            "sudo rm": "Utilisez des outils de gestion de fichiers avec interface graphique",
        }
        
        for dangerous, safe in alternatives.items():
            if dangerous in command_lower:
                return safe
        
        return None

    def format_security_report(self, analysis: Dict[str, Any]) -> str:
        """Formate un rapport de sécurité lisible"""
        if analysis["is_safe"] and not analysis["requires_confirmation"]:
            return "✅ Commande sécurisée"
        
        report = []
        
        # Niveau de risque
        risk_icons = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🟠",
            "critical": "🔴"
        }
        
        risk_icon = risk_icons.get(analysis["risk_level"], "❓")
        report.append(f"{risk_icon} Niveau de risque: {analysis['risk_level'].upper()}")
        
        # Issues détectées
        if analysis["issues"]:
            report.append("\n📋 Problèmes détectés:")
            for issue in analysis["issues"]:
                report.append(f"  • {issue}")
        
        # Actions requises
        if analysis["blocked"]:
            report.append("\n🚫 COMMANDE BLOQUÉE pour votre sécurité")
        elif analysis["requires_confirmation"]:
            report.append("\n⚠️ CONFIRMATION REQUISE avant exécution")
        
        # Suggestions
        if analysis["suggestions"]:
            report.append("\n💡 Suggestions:")
            for suggestion in analysis["suggestions"]:
                report.append(f"  • {suggestion}")
        
        return "\n".join(report)
