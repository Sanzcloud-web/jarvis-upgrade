# -*- coding: utf-8 -*-
"""
Outils pour les opérations sur les fichiers
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class FileOperations:
    def __init__(self, base_path: str = None):
        """Initialise avec un chemin de base (par défaut: Bureau)"""
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.home() / "Desktop"
        
        # S'assurer que le chemin de base existe
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils de fichiers"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Crée un nouveau fichier avec le contenu spécifié",
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
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier où créer le fichier (optionnel, par défaut: Bureau)"
                            }
                        },
                        "required": ["filename", "content"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Lit le contenu d'un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à lire"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Édite un fichier existant en remplaçant son contenu",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à éditer"
                            },
                            "new_content": {
                                "type": "string",
                                "description": "Nouveau contenu du fichier"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename", "new_content"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "append_to_file",
                    "description": "Ajoute du contenu à la fin d'un fichier existant",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier"
                            },
                            "content": {
                                "type": "string",
                                "description": "Contenu à ajouter"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename", "content"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "copy_file",
                    "description": "Copie un fichier vers un autre emplacement",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_filename": {
                                "type": "string",
                                "description": "Nom du fichier source"
                            },
                            "target_filename": {
                                "type": "string",
                                "description": "Nom du fichier de destination"
                            },
                            "source_directory": {
                                "type": "string",
                                "description": "Dossier source (optionnel)"
                            },
                            "target_directory": {
                                "type": "string",
                                "description": "Dossier de destination (optionnel)"
                            }
                        },
                        "required": ["source_filename", "target_filename"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_file",
                    "description": "Déplace ou renomme un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_filename": {
                                "type": "string",
                                "description": "Nom du fichier actuel"
                            },
                            "target_filename": {
                                "type": "string",
                                "description": "Nouveau nom ou emplacement"
                            },
                            "source_directory": {
                                "type": "string",
                                "description": "Dossier source (optionnel)"
                            },
                            "target_directory": {
                                "type": "string",
                                "description": "Dossier de destination (optionnel)"
                            }
                        },
                        "required": ["source_filename", "target_filename"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Supprime un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à supprimer"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "file_info",
                    "description": "Obtient des informations détaillées sur un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés"""
        try:
            method_map = {
                "create_file": self._create_file,
                "read_file": self._read_file,
                "edit_file": self._edit_file,
                "append_to_file": self._append_to_file,
                "copy_file": self._copy_file,
                "move_file": self._move_file,
                "delete_file": self._delete_file,
                "file_info": self._file_info
            }
            
            if tool_name in method_map:
                return method_map[tool_name](**arguments)
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _get_path(self, filename: str, directory: str = None) -> Path:
        """Construit le chemin complet du fichier"""
        if directory:
            # Si un dossier est spécifié, l'utiliser (relatif au chemin de base)
            return self.base_path / directory / filename
        else:
            return self.base_path / filename

    def _create_file(self, filename: str, content: str, directory: str = None) -> Dict[str, Any]:
        """Crée un nouveau fichier"""
        try:
            file_path = self._get_path(filename, directory)
            
            # Créer le dossier parent si nécessaire
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Fichier '{filename}' créé avec succès",
                "path": str(file_path),
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de créer le fichier: {str(e)}"}

    def _read_file(self, filename: str, directory: str = None) -> Dict[str, Any]:
        """Lit le contenu d'un fichier"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "filename": filename,
                "path": str(file_path),
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de lire le fichier: {str(e)}"}

    def _edit_file(self, filename: str, new_content: str, directory: str = None) -> Dict[str, Any]:
        """Édite un fichier existant"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            # Créer une sauvegarde
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "message": f"Fichier '{filename}' édité avec succès",
                "path": str(file_path),
                "backup_path": str(backup_path),
                "new_size": len(new_content)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible d'éditer le fichier: {str(e)}"}

    def _append_to_file(self, filename: str, content: str, directory: str = None) -> Dict[str, Any]:
        """Ajoute du contenu à un fichier"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Contenu ajouté au fichier '{filename}'",
                "path": str(file_path),
                "added_length": len(content)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible d'ajouter au fichier: {str(e)}"}

    def _copy_file(self, source_filename: str, target_filename: str, 
                   source_directory: str = None, target_directory: str = None) -> Dict[str, Any]:
        """Copie un fichier"""
        try:
            source_path = self._get_path(source_filename, source_directory)
            target_path = self._get_path(target_filename, target_directory)
            
            if not source_path.exists():
                return {"success": False, "error": f"Le fichier source '{source_filename}' n'existe pas"}
            
            # Créer le dossier de destination si nécessaire
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_path, target_path)
            
            return {
                "success": True,
                "message": f"Fichier copié de '{source_filename}' vers '{target_filename}'",
                "source_path": str(source_path),
                "target_path": str(target_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de copier le fichier: {str(e)}"}

    def _move_file(self, source_filename: str, target_filename: str,
                   source_directory: str = None, target_directory: str = None) -> Dict[str, Any]:
        """Déplace ou renomme un fichier"""
        try:
            source_path = self._get_path(source_filename, source_directory)
            target_path = self._get_path(target_filename, target_directory)
            
            if not source_path.exists():
                return {"success": False, "error": f"Le fichier source '{source_filename}' n'existe pas"}
            
            # Créer le dossier de destination si nécessaire
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(target_path))
            
            return {
                "success": True,
                "message": f"Fichier déplacé de '{source_filename}' vers '{target_filename}'",
                "old_path": str(source_path),
                "new_path": str(target_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de déplacer le fichier: {str(e)}"}

    def _delete_file(self, filename: str, directory: str = None) -> Dict[str, Any]:
        """Supprime un fichier"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            file_path.unlink()
            
            return {
                "success": True,
                "message": f"Fichier '{filename}' supprimé avec succès",
                "path": str(file_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible de supprimer le fichier: {str(e)}"}

    def _file_info(self, filename: str, directory: str = None) -> Dict[str, Any]:
        """Obtient des informations sur un fichier"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            stat = file_path.stat()
            
            return {
                "success": True,
                "filename": filename,
                "path": str(file_path),
                "size": stat.st_size,
                "extension": file_path.suffix,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK)
            }
        except Exception as e:
            return {"success": False, "error": f"Impossible d'obtenir les infos du fichier: {str(e)}"}
