# -*- coding: utf-8 -*-
"""
Gestionnaire centralisé de tous les outils JARVIS
"""

from typing import Dict, Any, List, Optional
from .file_system.file_operations import FileOperations
from .file_system.directory_operations import DirectoryOperations
from .text_editor.text_editor import TextEditor
from .system.system_commands import SystemCommands
from .utilities.datetime_tools import DateTimeTools
from .utilities.calculator import Calculator

class ToolManager:
    def __init__(self, base_path: str = None):
        """Initialise le gestionnaire d'outils"""
        self.base_path = base_path
        
        # Initialiser tous les outils
        self.file_ops = FileOperations(base_path)
        self.dir_ops = DirectoryOperations(base_path)
        self.text_editor = TextEditor(base_path)
        self.system_commands = SystemCommands()
        self.datetime_tools = DateTimeTools()
        self.calculator = Calculator()
        
        # Mapping des outils
        self.tools_map = {
            # Opérations sur les fichiers
            "create_file": self.file_ops,
            "read_file": self.file_ops,
            "edit_file": self.file_ops,
            "append_to_file": self.file_ops,
            "copy_file": self.file_ops,
            "move_file": self.file_ops,
            "delete_file": self.file_ops,
            "file_info": self.file_ops,
            
            # Opérations sur les dossiers
            "list_files": self.dir_ops,
            "create_directory": self.dir_ops,
            "remove_directory": self.dir_ops,
            "copy_directory": self.dir_ops,
            "search_files": self.dir_ops,
            "get_directory_size": self.dir_ops,
            
            # Éditeur de texte avancé
            "find_and_replace": self.text_editor,
            "insert_line": self.text_editor,
            "delete_lines": self.text_editor,
            "replace_line": self.text_editor,
            "show_lines": self.text_editor,
            "search_in_file": self.text_editor,
            
            # Commandes système
            "execute_command": self.system_commands,
            "get_system_info": self.system_commands,
            "get_disk_usage": self.system_commands,
            "get_memory_info": self.system_commands,
            "get_cpu_info": self.system_commands,
            "list_processes": self.system_commands,
            "open_application": self.system_commands,
            "open_url": self.system_commands,
            "find_files_terminal": self.system_commands,
            "smart_terminal_command": self.system_commands,
            
            # Outils de date/heure
            "get_current_time": self.datetime_tools,
            "add_time": self.datetime_tools,
            "calculate_age": self.datetime_tools,
            "get_calendar": self.datetime_tools,
            
            # Calculatrice
            "calculate": self.calculator,
            "convert_units": self.calculator,
            "percentage_calculation": self.calculator
        }

    def get_all_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne tous les schémas d'outils disponibles"""
        all_schemas = []
        
        all_schemas.extend(self.file_ops.get_tools_schema())
        all_schemas.extend(self.dir_ops.get_tools_schema())
        all_schemas.extend(self.text_editor.get_tools_schema())
        all_schemas.extend(self.system_commands.get_tools_schema())
        all_schemas.extend(self.datetime_tools.get_tools_schema())
        all_schemas.extend(self.calculator.get_tools_schema())
        
        return all_schemas

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
        categories = {
            # Fichiers
            "create_file": "file_operations",
            "read_file": "file_operations", 
            "edit_file": "file_operations",
            "append_to_file": "file_operations",
            "copy_file": "file_operations",
            "move_file": "file_operations", 
            "delete_file": "file_operations",
            "file_info": "file_operations",
            
            # Dossiers
            "list_files": "directory_operations",
            "create_directory": "directory_operations",
            "remove_directory": "directory_operations", 
            "copy_directory": "directory_operations",
            "search_files": "directory_operations",
            "get_directory_size": "directory_operations",
            
            # Éditeur de texte
            "find_and_replace": "text_editor",
            "insert_line": "text_editor",
            "delete_lines": "text_editor",
            "replace_line": "text_editor",
            "show_lines": "text_editor",
            "search_in_file": "text_editor",
            
            # Système
            "execute_command": "system_commands",
            "get_system_info": "system_commands",
            "get_disk_usage": "system_commands",
            "get_memory_info": "system_commands", 
            "get_cpu_info": "system_commands",
            "list_processes": "system_commands",
            "open_application": "system_commands",
            "open_url": "system_commands",
            "find_files_terminal": "system_commands",
            "smart_terminal_command": "system_commands",
            
            # Date/heure
            "get_current_time": "datetime_tools",
            "add_time": "datetime_tools",
            "calculate_age": "datetime_tools", 
            "get_calendar": "datetime_tools",
            
            # Calcul
            "calculate": "calculator",
            "convert_units": "calculator",
            "percentage_calculation": "calculator"
        }
        
        return categories.get(tool_name, "unknown")

    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Retourne les outils groupés par catégorie"""
        categories = {}
        
        for tool_name in self.tools_map.keys():
            category = self._get_tool_category(tool_name)
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)
        
        return categories

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
