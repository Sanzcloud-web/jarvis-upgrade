# -*- coding: utf-8 -*-
"""
Gestionnaire centralisé de tous les outils JARVIS avec auto-découverte
"""

from typing import Dict, Any, List, Optional
from .auto_loader import auto_loader, get_auto_discovered_tools

class ToolManager:
    def __init__(self, base_path: str = None):
        """Initialise le gestionnaire d'outils avec auto-découverte"""
        self.base_path = base_path
        
        # Auto-découverte des outils
        print("🔍 Auto-découverte des outils JARVIS en cours...")
        self.tools_map, self.all_schemas = get_auto_discovered_tools()
        
        # Statistiques
        tools_count = len(self.tools_map)
        categories = auto_loader.get_tools_by_category()
        categories_count = len(categories)
        
        print(f"✅ {tools_count} outils découverts dans {categories_count} catégories")
        
        # Afficher le résumé par catégorie
        for category, tools in categories.items():
            category_emoji = {
                "file_system": "📁",
                "text_editor": "📝", 
                "system": "⚙️",
                "utilities": "🔧"
            }.get(category, "🔧")
            print(f"   {category_emoji} {category}: {len(tools)} outils")

    def get_all_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne tous les schémas d'outils disponibles (auto-découverts)"""
        return self.all_schemas

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil spécifique"""
        try:
            if tool_name not in self.tools_map:
                return {
                    "success": False, 
                    "error": f"Outil inconnu: {tool_name}",
                    "available_tools": list(self.tools_map.keys())
                }
            
            tool_instance = self.tools_map[tool_name]
            result = tool_instance.execute_tool(tool_name, arguments)
            
            # Ajouter des métadonnées
            result["tool_name"] = tool_name
            result["tool_category"] = self._get_tool_category(tool_name)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de l'exécution de {tool_name}: {str(e)}",
                "tool_name": tool_name
            }

    def _get_tool_category(self, tool_name: str) -> str:
        """Détermine la catégorie d'un outil"""
        # Utiliser l'auto-découverte pour obtenir la catégorie
        tool_info = auto_loader.discovered_tools.get(tool_name)
        if tool_info:
            return tool_info["category"]
        return "unknown"

    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Retourne les outils groupés par catégorie (auto-découverts)"""
        return auto_loader.get_tools_by_category()

    def get_tool_help(self, tool_name: str = None) -> Dict[str, Any]:
        """Retourne l'aide pour un outil spécifique ou tous les outils"""
        if tool_name:
            if tool_name not in self.tools_map:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
            
            # Trouver le schéma de cet outil
            all_schemas = self.get_all_tools_schema()
            tool_schema = None
            
            for schema in all_schemas:
                if schema["function"]["name"] == tool_name:
                    tool_schema = schema
                    break
            
            if not tool_schema:
                return {"success": False, "error": f"Schéma non trouvé pour: {tool_name}"}
            
            return {
                "success": True,
                "tool_name": tool_name,
                "category": self._get_tool_category(tool_name),
                "description": tool_schema["function"]["description"],
                "parameters": tool_schema["function"]["parameters"]["properties"],
                "required_parameters": tool_schema["function"]["parameters"].get("required", [])
            }
        else:
            # Retourner la liste de tous les outils avec descriptions
            categories = self.get_tools_by_category()
            all_schemas = self.get_all_tools_schema()
            
            help_data = {}
            for category, tools in categories.items():
                help_data[category] = []
                for tool in tools:
                    for schema in all_schemas:
                        if schema["function"]["name"] == tool:
                            help_data[category].append({
                                "name": tool,
                                "description": schema["function"]["description"]
                            })
                            break
            
            return {
                "success": True,
                "total_tools": len(self.tools_map),
                "categories": help_data
            }

    def execute_multiple_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Exécute plusieurs outils en séquence"""
        results = []
        
        for i, tool_call in enumerate(tool_calls):
            try:
                tool_name = tool_call.get("tool_name")
                arguments = tool_call.get("arguments", {})
                
                if not tool_name:
                    results.append({
                        "success": False,
                        "error": "tool_name manquant",
                        "call_index": i
                    })
                    continue
                
                result = self.execute_tool(tool_name, arguments)
                result["call_index"] = i
                results.append(result)
                
            except Exception as e:
                results.append({
                    "success": False,
                    "error": f"Erreur lors de l'exécution du call {i}: {str(e)}",
                    "call_index": i
                })
        
        return results
