# -*- coding: utf-8 -*-
"""
Éditeur de texte avancé avec recherche/remplacement et manipulation de lignes
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional

class TextEditor:
    def __init__(self, base_path: str = None):
        """Initialise l'éditeur avec un chemin de base"""
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.home() / "Desktop"
        
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils d'édition"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "find_and_replace",
                    "description": "Recherche et remplace du texte dans un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à éditer"
                            },
                            "search_text": {
                                "type": "string",
                                "description": "Texte à rechercher"
                            },
                            "replace_text": {
                                "type": "string",
                                "description": "Texte de remplacement"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            },
                            "use_regex": {
                                "type": "boolean",
                                "description": "Utiliser des expressions régulières"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Recherche sensible à la casse"
                            }
                        },
                        "required": ["filename", "search_text", "replace_text"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "insert_line",
                    "description": "Insère une ligne à une position spécifique dans un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à éditer"
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Numéro de ligne où insérer (1 = début du fichier)"
                            },
                            "text": {
                                "type": "string",
                                "description": "Texte à insérer"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename", "line_number", "text"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_lines",
                    "description": "Supprime des lignes spécifiques d'un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à éditer"
                            },
                            "start_line": {
                                "type": "integer",
                                "description": "Première ligne à supprimer"
                            },
                            "end_line": {
                                "type": "integer",
                                "description": "Dernière ligne à supprimer (optionnel, défaut: même que start_line)"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename", "start_line"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "replace_line",
                    "description": "Remplace une ligne spécifique dans un fichier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à éditer"
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Numéro de ligne à remplacer"
                            },
                            "new_text": {
                                "type": "string",
                                "description": "Nouveau contenu de la ligne"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            }
                        },
                        "required": ["filename", "line_number", "new_text"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_lines",
                    "description": "Affiche des lignes spécifiques d'un fichier avec numérotation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à lire"
                            },
                            "start_line": {
                                "type": "integer",
                                "description": "Première ligne à afficher (optionnel, défaut: 1)"
                            },
                            "end_line": {
                                "type": "integer",
                                "description": "Dernière ligne à afficher (optionnel, défaut: toutes)"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
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
                    "name": "search_in_file",
                    "description": "Recherche du texte dans un fichier et affiche les lignes correspondantes",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à rechercher"
                            },
                            "search_text": {
                                "type": "string",
                                "description": "Texte à rechercher"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Dossier contenant le fichier (optionnel)"
                            },
                            "use_regex": {
                                "type": "boolean",
                                "description": "Utiliser des expressions régulières"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Recherche sensible à la casse"
                            }
                        },
                        "required": ["filename", "search_text"],
                        "additionalProperties": False
                    },
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés"""
        try:
            method_map = {
                "find_and_replace": self._find_and_replace,
                "insert_line": self._insert_line,
                "delete_lines": self._delete_lines,
                "replace_line": self._replace_line,
                "show_lines": self._show_lines,
                "search_in_file": self._search_in_file
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
            return self.base_path / directory / filename
        else:
            return self.base_path / filename

    def _read_lines(self, file_path: Path) -> List[str]:
        """Lit toutes les lignes d'un fichier"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()

    def _write_lines(self, file_path: Path, lines: List[str]) -> None:
        """Écrit les lignes dans un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def _find_and_replace(self, filename: str, search_text: str, replace_text: str,
                         directory: str = None, use_regex: bool = False, 
                         case_sensitive: bool = True) -> Dict[str, Any]:
        """Recherche et remplace du texte"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            # Créer une sauvegarde
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            import shutil
            shutil.copy2(file_path, backup_path)
            
            lines = self._read_lines(file_path)
            original_content = ''.join(lines)
            
            replacements_count = 0
            affected_lines = []
            
            if use_regex:
                # Utiliser les expressions régulières
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_text, flags)
                
                new_content = pattern.sub(replace_text, original_content)
                replacements_count = len(pattern.findall(original_content))
                
                # Trouver les lignes affectées
                for i, line in enumerate(lines, 1):
                    if pattern.search(line):
                        affected_lines.append(i)
            else:
                # Recherche de texte simple
                search_term = search_text if case_sensitive else search_text.lower()
                
                new_lines = []
                for i, line in enumerate(lines, 1):
                    check_line = line if case_sensitive else line.lower()
                    if search_term in check_line:
                        new_line = line.replace(search_text, replace_text)
                        replacements_count += line.count(search_text)
                        affected_lines.append(i)
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                
                new_content = ''.join(new_lines)
            
            # Écrire le nouveau contenu
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "message": f"Remplacement effectué dans '{filename}'",
                "replacements_count": replacements_count,
                "affected_lines": affected_lines,
                "backup_path": str(backup_path)
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du remplacement: {str(e)}"}

    def _insert_line(self, filename: str, line_number: int, text: str, directory: str = None) -> Dict[str, Any]:
        """Insère une ligne à une position spécifique"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            lines = self._read_lines(file_path)
            
            # Validation du numéro de ligne
            if line_number < 1:
                line_number = 1
            elif line_number > len(lines) + 1:
                line_number = len(lines) + 1
            
            # Insérer la ligne (ajuster l'index car les listes commencent à 0)
            insert_index = line_number - 1
            if not text.endswith('\n'):
                text += '\n'
            
            lines.insert(insert_index, text)
            
            self._write_lines(file_path, lines)
            
            return {
                "success": True,
                "message": f"Ligne insérée à la position {line_number} dans '{filename}'",
                "line_number": line_number,
                "inserted_text": text.rstrip('\n')
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'insertion: {str(e)}"}

    def _delete_lines(self, filename: str, start_line: int, end_line: int = None, directory: str = None) -> Dict[str, Any]:
        """Supprime des lignes spécifiques"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            lines = self._read_lines(file_path)
            total_lines = len(lines)
            
            if end_line is None:
                end_line = start_line
            
            # Validation des numéros de ligne
            if start_line < 1 or start_line > total_lines:
                return {"success": False, "error": f"Numéro de ligne invalide: {start_line}"}
            
            if end_line < start_line or end_line > total_lines:
                return {"success": False, "error": f"Numéro de ligne de fin invalide: {end_line}"}
            
            # Supprimer les lignes (ajuster les index)
            deleted_lines = lines[start_line-1:end_line]
            del lines[start_line-1:end_line]
            
            self._write_lines(file_path, lines)
            
            return {
                "success": True,
                "message": f"Lignes {start_line} à {end_line} supprimées de '{filename}'",
                "deleted_lines_count": len(deleted_lines),
                "deleted_content": [line.rstrip('\n') for line in deleted_lines]
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la suppression: {str(e)}"}

    def _replace_line(self, filename: str, line_number: int, new_text: str, directory: str = None) -> Dict[str, Any]:
        """Remplace une ligne spécifique"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            lines = self._read_lines(file_path)
            
            # Validation du numéro de ligne
            if line_number < 1 or line_number > len(lines):
                return {"success": False, "error": f"Numéro de ligne invalide: {line_number}"}
            
            # Sauvegarder l'ancienne ligne
            old_line = lines[line_number - 1].rstrip('\n')
            
            # Remplacer la ligne
            if not new_text.endswith('\n'):
                new_text += '\n'
            
            lines[line_number - 1] = new_text
            
            self._write_lines(file_path, lines)
            
            return {
                "success": True,
                "message": f"Ligne {line_number} remplacée dans '{filename}'",
                "line_number": line_number,
                "old_content": old_line,
                "new_content": new_text.rstrip('\n')
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du remplacement: {str(e)}"}

    def _show_lines(self, filename: str, start_line: int = 1, end_line: int = None, directory: str = None) -> Dict[str, Any]:
        """Affiche des lignes avec numérotation"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            lines = self._read_lines(file_path)
            total_lines = len(lines)
            
            if end_line is None:
                end_line = total_lines
            
            # Validation des numéros de ligne
            start_line = max(1, min(start_line, total_lines))
            end_line = max(start_line, min(end_line, total_lines))
            
            # Extraire les lignes demandées
            displayed_lines = []
            for i in range(start_line - 1, end_line):
                line_content = lines[i].rstrip('\n')
                displayed_lines.append({
                    "line_number": i + 1,
                    "content": line_content
                })
            
            return {
                "success": True,
                "filename": filename,
                "total_lines": total_lines,
                "displayed_range": f"{start_line}-{end_line}",
                "lines": displayed_lines
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'affichage: {str(e)}"}

    def _search_in_file(self, filename: str, search_text: str, directory: str = None,
                       use_regex: bool = False, case_sensitive: bool = True) -> Dict[str, Any]:
        """Recherche du texte dans un fichier"""
        try:
            file_path = self._get_path(filename, directory)
            
            if not file_path.exists():
                return {"success": False, "error": f"Le fichier '{filename}' n'existe pas"}
            
            lines = self._read_lines(file_path)
            matches = []
            
            if use_regex:
                # Utiliser les expressions régulières
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    pattern = re.compile(search_text, flags)
                except re.error as e:
                    return {"success": False, "error": f"Expression régulière invalide: {str(e)}"}
                
                for i, line in enumerate(lines, 1):
                    match = pattern.search(line)
                    if match:
                        matches.append({
                            "line_number": i,
                            "content": line.rstrip('\n'),
                            "match_start": match.start(),
                            "match_end": match.end(),
                            "matched_text": match.group()
                        })
            else:
                # Recherche de texte simple
                search_term = search_text if case_sensitive else search_text.lower()
                
                for i, line in enumerate(lines, 1):
                    check_line = line if case_sensitive else line.lower()
                    if search_term in check_line:
                        matches.append({
                            "line_number": i,
                            "content": line.rstrip('\n')
                        })
            
            return {
                "success": True,
                "filename": filename,
                "search_text": search_text,
                "use_regex": use_regex,
                "case_sensitive": case_sensitive,
                "matches_count": len(matches),
                "matches": matches
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la recherche: {str(e)}"}
