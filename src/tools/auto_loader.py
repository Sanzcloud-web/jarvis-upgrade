# -*- coding: utf-8 -*-
"""
Système d'auto-loading des outils JARVIS
Découvre et charge automatiquement tous les outils disponibles
"""

import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Type
import logging

class ToolAutoLoader:
    def __init__(self, tools_base_path: str = None):
        """
        Initialise l'auto-loader des outils
        
        Args:
            tools_base_path: Chemin vers le dossier des outils (par défaut: ce dossier)
        """
        if tools_base_path is None:
            tools_base_path = str(Path(__file__).parent)
        
        self.tools_base_path = Path(tools_base_path)
        self.discovered_tools = {}
        self.tool_instances = {}
        self.all_schemas = []
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def discover_tools(self) -> Dict[str, Any]:
        """
        Découvre automatiquement tous les outils disponibles
        
        Returns:
            Dictionnaire des outils découverts avec leurs métadonnées
        """
        self.logger.info("🔍 Découverte automatique des outils JARVIS...")
        
        # Dossiers d'outils à scanner
        tool_directories = [
            "file_system",
            "text_editor", 
            "system",
            "utilities"
        ]
        
        total_tools = 0
        
        for tool_dir in tool_directories:
            dir_path = self.tools_base_path / tool_dir
            if dir_path.exists():
                tools_found = self._scan_directory(tool_dir, dir_path)
                total_tools += len(tools_found)
                self.logger.info(f"  📂 {tool_dir}: {len(tools_found)} outils trouvés")
        
        # Scanner aussi le fichier legacy file_tools.py
        legacy_tools = self._scan_legacy_tools()
        total_tools += len(legacy_tools)
        
        self.logger.info(f"✅ Découverte terminée: {total_tools} outils au total")
        return self.discovered_tools
    
    def _scan_directory(self, category: str, directory_path: Path) -> List[str]:
        """
        Scanne un dossier pour découvrir les classes d'outils
        
        Args:
            category: Catégorie d'outils (ex: "file_system")
            directory_path: Chemin vers le dossier
            
        Returns:
            Liste des noms d'outils trouvés
        """
        found_tools = []
        
        for py_file in directory_path.glob("*.py"):
            if py_file.name.startswith("__") or py_file.name == "security_manager.py":
                continue
                
            module_name = f"src.tools.{category}.{py_file.stem}"
            
            try:
                # Importer le module
                module = importlib.import_module(module_name)
                
                # Chercher les classes d'outils
                for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
                    if (class_name.endswith(('Operations', 'Commands', 'Tools', 'Editor', 'Calculator')) 
                        and hasattr(class_obj, 'get_tools_schema')):
                        
                        # Instancier la classe d'outils
                        tool_instance = class_obj()
                        
                        # Obtenir les schémas des outils
                        schemas = tool_instance.get_tools_schema()
                        
                        # Enregistrer chaque outil
                        for schema in schemas:
                            tool_name = schema["function"]["name"]
                            
                            self.discovered_tools[tool_name] = {
                                "category": category,
                                "class_name": class_name,
                                "instance": tool_instance,
                                "module": module_name,
                                "schema": schema,
                                "description": schema["function"]["description"]
                            }
                            
                            found_tools.append(tool_name)
                            self.all_schemas.append(schema)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur lors du chargement de {module_name}: {e}")
        
        return found_tools
    
    def _scan_legacy_tools(self) -> List[str]:
        """Scanne les outils legacy (file_tools.py)"""
        found_tools = []
        
        try:
            from . import file_tools
            
            # Importer FileTools
            file_tools_instance = file_tools.FileTools()
            schemas = file_tools_instance.get_tools_schema()
            
            for schema in schemas:
                tool_name = schema["function"]["name"]
                
                self.discovered_tools[tool_name + "_legacy"] = {
                    "category": "legacy",
                    "class_name": "FileTools",
                    "instance": file_tools_instance,
                    "module": "src.tools.file_tools",
                    "schema": schema,
                    "description": schema["function"]["description"]
                }
                
                found_tools.append(tool_name + "_legacy")
                # Note: on n'ajoute pas les schémas legacy pour éviter les doublons
                
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur lors du chargement des outils legacy: {e}")
        
        return found_tools
    
    def get_tool_instances_map(self) -> Dict[str, Any]:
        """
        Retourne un mapping tool_name -> instance pour le ToolManager
        
        Returns:
            Dictionnaire mapping les noms d'outils vers leurs instances
        """
        tool_map = {}
        
        for tool_name, tool_info in self.discovered_tools.items():
            if not tool_name.endswith("_legacy"):  # Ignorer les outils legacy
                tool_map[tool_name] = tool_info["instance"]
        
        return tool_map
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Retourne tous les schémas d'outils découverts
        
        Returns:
            Liste de tous les schémas d'outils
        """
        return self.all_schemas
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """
        Retourne les outils groupés par catégorie
        
        Returns:
            Dictionnaire catégorie -> liste d'outils
        """
        categories = {}
        
        for tool_name, tool_info in self.discovered_tools.items():
            if not tool_name.endswith("_legacy"):
                category = tool_info["category"]
                if category not in categories:
                    categories[category] = []
                categories[category].append(tool_name)
        
        return categories
    
    def get_tools_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des outils découverts
        
        Returns:
            Résumé des outils avec statistiques
        """
        categories = self.get_tools_by_category()
        
        summary = {
            "total_tools": len([t for t in self.discovered_tools.keys() if not t.endswith("_legacy")]),
            "categories": {},
            "tools_by_category": categories
        }
        
        # Statistiques par catégorie
        for category, tools in categories.items():
            summary["categories"][category] = {
                "count": len(tools),
                "tools": tools
            }
        
        return summary
    
    def generate_prompt_section(self) -> str:
        """
        Génère une section de prompt décrivant tous les outils disponibles
        
        Returns:
            Section de prompt formatée
        """
        categories = self.get_tools_by_category()
        
        # Emojis et noms pour les catégories
        category_info = {
            "file_system": ("📁", "FICHIERS & DOSSIERS"),
            "text_editor": ("📝", "ÉDITEUR AVANCÉ"),
            "system": ("⚙️", "SYSTÈME & TERMINAL"),
            "utilities": ("🔧", "UTILITAIRES")
        }
        
        prompt_lines = ["=== ARSENAL D'OUTILS DISPONIBLES (AUTO-DÉCOUVERTS) ===\n"]
        
        for category, tools in categories.items():
            emoji, name = category_info.get(category, ("🔧", category.upper()))
            
            prompt_lines.append(f"{emoji} {name} ({len(tools)} outils) :")
            
            # Grouper les outils par ligne (max 6 par ligne)
            tool_groups = [tools[i:i+6] for i in range(0, len(tools), 6)]
            for group in tool_groups:
                prompt_lines.append(f"- {', '.join(group)}")
            
            prompt_lines.append("")  # Ligne vide entre catégories
        
        return "\n".join(prompt_lines)
    
    def generate_mapping_code(self) -> str:
        """
        Génère le code Python pour créer le mapping des outils
        
        Returns:
            Code Python string
        """
        lines = ["# Mapping automatique des outils (généré par auto_loader)"]
        lines.append("tools_map = {")
        
        for tool_name, tool_info in self.discovered_tools.items():
            if not tool_name.endswith("_legacy"):
                lines.append(f'    "{tool_name}": {tool_info["class_name"].lower()}_instance,')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def reload_tools(self) -> None:
        """Recharge tous les outils (utile pour le développement)"""
        self.logger.info("🔄 Rechargement des outils...")
        
        # Effacer les anciens outils
        self.discovered_tools.clear()
        self.tool_instances.clear()
        self.all_schemas.clear()
        
        # Redécouvrir
        self.discover_tools()
        
        self.logger.info("✅ Rechargement terminé")

# Instance globale pour utilisation facile
auto_loader = ToolAutoLoader()

def get_auto_discovered_tools():
    """Fonction utilitaire pour obtenir tous les outils auto-découverts"""
    auto_loader.discover_tools()
    return auto_loader.get_tool_instances_map(), auto_loader.get_all_schemas()

def get_tools_summary():
    """Fonction utilitaire pour obtenir un résumé des outils"""
    auto_loader.discover_tools()
    return auto_loader.get_tools_summary()

def generate_tools_prompt():
    """Fonction utilitaire pour générer la section prompt"""
    auto_loader.discover_tools()
    return auto_loader.generate_prompt_section()
