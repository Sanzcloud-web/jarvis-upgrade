# -*- coding: utf-8 -*-
"""
Outils pour les opérations sur les dossiers
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class DirectoryOperations:
    def __init__(self, base_path: str = None):
        """Initialise avec un chemin de base (par défaut: Bureau)"""
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.home() / "Desktop"
        
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils de dossiers"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Liste tous les fichiers et dossiers dans un répertoire",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Dossier à explorer (optionnel, par défaut: Bureau)"
                            },
                            "include_hidden": {
                                "type": "boolean",
                                "description": "Inclure les fichiers cachés (optionnel, défaut: false)"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "Crée un nouveau dossier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_name": {
                                "type": "string",
                                "description": "Nom du dossier à créer"
                            },
                            "parent_directory": {
                                "type": "string",
                                "description": "Dossier parent (optionnel, par défaut: Bureau)"
                            }
                        },
                        "required": ["directory_name"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_directory",
                    "description": "Supprime un dossier et tout son contenu",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_name": {
                                "type": "string",
                                "description": "Nom du dossier à supprimer"
                            },
                            "parent_directory": {
                                "type": "string",
                                "description": "Dossier parent (optionnel)"
                            },
                            "force": {
                                "type": "boolean",
                                "description": "Forcer la suppression même si le dossier n'est pas vide"
                            }
                        },
                        "required": ["directory_name"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "copy_directory",
                    "description": "Copie un dossier et tout son contenu",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_directory": {
                                "type": "string",
                                "description": "Nom du dossier source"
                            },
                            "target_directory": {
                                "type": "string",
                                "description": "Nom du dossier de destination"
                            },
                            "source_parent": {
                                "type": "string",
                                "description": "Dossier parent source (optionnel)"
                            },
                            "target_parent": {
                                "type": "string",
                                "description": "Dossier parent de destination (optionnel)"
                            }
                        },
                        "required": ["source_directory", "target_directory"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Recherche des fichiers par nom ou extension",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Motif de recherche (nom de fichier ou extension)"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier où chercher (optionnel, par défaut: Bureau)"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Recherche récursive dans les sous-dossiers"
                            }
                        },
                        "required": ["pattern"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_directory_size",
                    "description": "Calcule la taille totale d'un dossier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Dossier à analyser (optionnel, par défaut: Bureau)"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés"""
        try:
            method_map = {
                "list_files": self._list_files,
                "create_directory": self._create_directory,
                "remove_directory": self._remove_directory,
                "copy_directory": self._copy_directory,
                "search_files": self._search_files,
                "get_directory_size": self._get_directory_size
            }
            
            if tool_name in method_map:
                return method_map[tool_name](**arguments)
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _get_path(self, directory: str = None) -> Path:
        """Construit le chemin complet du dossier"""
        if directory:
            return self.base_path / directory
        else:
            return self.base_path

    def _list_files(self, directory: str = None, include_hidden: bool = False) -> Dict[str, Any]:
        """Liste les fichiers et dossiers"""
        try:
            dir_path = self._get_path(directory)
            
            if not dir_path.exists():
                return {"success": False, "error": f"Le dossier '{directory or 'Bureau'}' n'existe pas"}
            
            items = []
            for item in dir_path.iterdir():
                # Ignorer les fichiers cachés si demandé
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                stat = item.stat()
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": item.suffix if item.is_file() else None
                }
                items.append(item_info)
            
            # Trier par type puis par nom
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return {
                "success": True,
                "directory": str(dir_path),
                "items": items,
                "total_count": len(items),
                "files_count": len([i for i in items if i["type"] == "file"]),
                "directories_count": len([i for i in items if i["type"] == "directory"])
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de lister le contenu: {str(e)}"}

    def _create_directory(self, directory_name: str, parent_directory: str = None) -> Dict[str, Any]:
        """Crée un nouveau dossier"""
        try:
            parent_path = self._get_path(parent_directory)
            new_dir_path = parent_path / directory_name
            
            if new_dir_path.exists():
                return {"success": False, "error": f"Le dossier '{directory_name}' existe déjà"}
            
            new_dir_path.mkdir(parents=True, exist_ok=False)
            
            return {
                "success": True,
                "message": f"Dossier '{directory_name}' créé avec succès",
                "path": str(new_dir_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de créer le dossier: {str(e)}"}

    def _remove_directory(self, directory_name: str, parent_directory: str = None, force: bool = False) -> Dict[str, Any]:
        """Supprime un dossier"""
        try:
            parent_path = self._get_path(parent_directory)
            dir_path = parent_path / directory_name
            
            if not dir_path.exists():
                return {"success": False, "error": f"Le dossier '{directory_name}' n'existe pas"}
            
            if not dir_path.is_dir():
                return {"success": False, "error": f"'{directory_name}' n'est pas un dossier"}
            
            # Vérifier si le dossier est vide
            if list(dir_path.iterdir()) and not force:
                return {"success": False, "error": f"Le dossier '{directory_name}' n'est pas vide. Utilisez force=true pour forcer la suppression."}
            
            if force:
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()
            
            return {
                "success": True,
                "message": f"Dossier '{directory_name}' supprimé avec succès",
                "path": str(dir_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de supprimer le dossier: {str(e)}"}

    def _copy_directory(self, source_directory: str, target_directory: str,
                       source_parent: str = None, target_parent: str = None) -> Dict[str, Any]:
        """Copie un dossier"""
        try:
            source_parent_path = self._get_path(source_parent)
            target_parent_path = self._get_path(target_parent)
            
            source_path = source_parent_path / source_directory
            target_path = target_parent_path / target_directory
            
            if not source_path.exists():
                return {"success": False, "error": f"Le dossier source '{source_directory}' n'existe pas"}
            
            if target_path.exists():
                return {"success": False, "error": f"Le dossier de destination '{target_directory}' existe déjà"}
            
            shutil.copytree(source_path, target_path)
            
            return {
                "success": True,
                "message": f"Dossier copié de '{source_directory}' vers '{target_directory}'",
                "source_path": str(source_path),
                "target_path": str(target_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de copier le dossier: {str(e)}"}

    def _search_files(self, pattern: str, directory: str = None, recursive: bool = True) -> Dict[str, Any]:
        """Recherche des fichiers"""
        try:
            search_path = self._get_path(directory)
            
            if not search_path.exists():
                return {"success": False, "error": f"Le dossier de recherche n'existe pas"}
            
            found_files = []
            
            # Fonction de recherche récursive
            def search_in_directory(dir_path: Path, current_depth: int = 0):
                try:
                    for item in dir_path.iterdir():
                        if item.is_file():
                            # Vérifier si le fichier correspond au motif
                            if (pattern.lower() in item.name.lower() or 
                                (pattern.startswith('.') and item.suffix.lower() == pattern.lower())):
                                
                                stat = item.stat()
                                found_files.append({
                                    "name": item.name,
                                    "path": str(item.relative_to(search_path)),
                                    "full_path": str(item),
                                    "size": stat.st_size,
                                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                    "extension": item.suffix
                                })
                        
                        elif item.is_dir() and recursive:
                            search_in_directory(item, current_depth + 1)
                except PermissionError:
                    # Ignorer les dossiers sans permission
                    pass
            
            search_in_directory(search_path)
            
            # Trier par nom
            found_files.sort(key=lambda x: x["name"].lower())
            
            return {
                "success": True,
                "pattern": pattern,
                "search_directory": str(search_path),
                "recursive": recursive,
                "found_files": found_files,
                "count": len(found_files)
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la recherche: {str(e)}"}

    def _get_directory_size(self, directory: str = None) -> Dict[str, Any]:
        """Calcule la taille d'un dossier"""
        try:
            dir_path = self._get_path(directory)
            
            if not dir_path.exists():
                return {"success": False, "error": f"Le dossier n'existe pas"}
            
            total_size = 0
            file_count = 0
            dir_count = 0
            
            def calculate_size(path: Path):
                nonlocal total_size, file_count, dir_count
                try:
                    for item in path.iterdir():
                        if item.is_file():
                            total_size += item.stat().st_size
                            file_count += 1
                        elif item.is_dir():
                            dir_count += 1
                            calculate_size(item)
                except PermissionError:
                    pass
            
            calculate_size(dir_path)
            
            # Convertir en unités lisibles
            def format_size(size_bytes: int) -> str:
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size_bytes < 1024.0:
                        return f"{size_bytes:.1f} {unit}"
                    size_bytes /= 1024.0
                return f"{size_bytes:.1f} PB"
            
            return {
                "success": True,
                "directory": str(dir_path),
                "total_size_bytes": total_size,
                "total_size_formatted": format_size(total_size),
                "file_count": file_count,
                "directory_count": dir_count
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du calcul de taille: {str(e)}"}
