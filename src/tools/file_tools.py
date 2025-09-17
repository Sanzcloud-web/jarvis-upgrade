# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from typing import Dict, Any, List

class FileTools:
    def __init__(self):
        # Répertoire bureau de l'utilisateur
        self.desktop_path = Path.home() / "Desktop"

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas JSON stricts pour les outils de fichiers"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Crée un nouveau fichier sur le bureau avec le contenu spécifié",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à créer (avec extension)"
                            },
                            "content": {
                                "type": "string",
                                "description": "Contenu à écrire dans le fichier"
                            }
                        },
                        "required": ["filename", "content"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Liste tous les fichiers présents sur le bureau",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Lit le contenu d'un fichier sur le bureau",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à lire"
                            }
                        },
                        "required": ["filename"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Supprime un fichier du bureau",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à supprimer"
                            }
                        },
                        "required": ["filename"],
                        "additionalProperties": False
                    },
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés"""
        try:
            if tool_name == "create_file":
                return self._create_file(arguments["filename"], arguments["content"])
            elif tool_name == "list_files":
                return self._list_files()
            elif tool_name == "read_file":
                return self._read_file(arguments["filename"])
            elif tool_name == "delete_file":
                return self._delete_file(arguments["filename"])
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _create_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Crée un fichier sur le bureau"""
        try:
            file_path = self.desktop_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "success": True,
                "message": f"Fichier '{filename}' créé avec succès sur le bureau",
                "path": str(file_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de créer le fichier: {str(e)}"}

    def _list_files(self) -> Dict[str, Any]:
        """Liste les fichiers du bureau"""
        try:
            files = []
            for item in self.desktop_path.iterdir():
                if item.is_file():
                    files.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "extension": item.suffix
                    })
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de lister les fichiers: {str(e)}"}

    def _read_file(self, filename: str) -> Dict[str, Any]:
        """Lit un fichier du bureau"""
        try:
            file_path = self.desktop_path / filename
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "filename": filename
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de lire le fichier: {str(e)}"}

    def _delete_file(self, filename: str) -> Dict[str, Any]:
        """Supprime un fichier du bureau"""
        try:
            file_path = self.desktop_path / filename
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}

            file_path.unlink()
            return {
                "success": True,
                "message": f"Fichier '{filename}' supprimé avec succès"
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de supprimer le fichier: {str(e)}"}