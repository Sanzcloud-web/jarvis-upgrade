# -*- coding: utf-8 -*-
"""
Commandes système de base adaptées selon l'OS
"""

import subprocess
import os
import psutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from ...utils.system_utils import system_detector, SystemType

class SystemCommands:
    def __init__(self):
        """Initialise les commandes système"""
        self.system_detector = system_detector

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils système"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Exécute une commande système adaptée à l'OS",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Commande à exécuter"
                            },
                            "capture_output": {
                                "type": "boolean",
                                "description": "Capturer la sortie de la commande"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout en secondes (défaut: 30)"
                            }
                        },
                        "required": ["command"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Obtient des informations détaillées sur le système",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_disk_usage",
                    "description": "Affiche l'utilisation de l'espace disque",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Chemin à analyser (défaut: racine)"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_memory_info",
                    "description": "Affiche les informations sur la mémoire",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cpu_info",
                    "description": "Affiche les informations sur le processeur",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_processes",
                    "description": "Liste les processus en cours d'exécution",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Nombre maximum de processus à afficher"
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Critère de tri (cpu, memory, name)"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Ouvre une application selon l'OS",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "application": {
                                "type": "string",
                                "description": "Nom de l'application à ouvrir"
                            }
                        },
                        "required": ["application"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_url",
                    "description": "Ouvre une URL dans le navigateur par défaut",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL à ouvrir"
                            }
                        },
                        "required": ["url"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_files_terminal",
                    "description": "Recherche des fichiers en utilisant des commandes terminal natives (find, ls, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_pattern": {
                                "type": "string",
                                "description": "Motif de recherche (nom de fichier, extension, etc.)"
                            },
                            "search_path": {
                                "type": "string",
                                "description": "Chemin où chercher (défaut: répertoire utilisateur)"
                            },
                            "file_type": {
                                "type": "string",
                                "description": "Type de fichier à chercher (file, directory, ou all)"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Recherche sensible à la casse"
                            }
                        },
                        "required": ["search_pattern"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "smart_terminal_command",
                    "description": "Exécute une commande terminal intelligente adaptée à l'OS avec suggestions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Description de la tâche à accomplir (ex: 'trouver tous les fichiers PDF', 'voir l'espace disque')"
                            },
                            "preferred_command": {
                                "type": "string",
                                "description": "Commande préférée si connue (optionnel)"
                            }
                        },
                        "required": ["task_description"],
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
                "execute_command": self._execute_command,
                "get_system_info": self._get_system_info,
                "get_disk_usage": self._get_disk_usage,
                "get_memory_info": self._get_memory_info,
                "get_cpu_info": self._get_cpu_info,
                "list_processes": self._list_processes,
                "open_application": self._open_application,
                "open_url": self._open_url,
                "find_files_terminal": self._find_files_terminal,
                "smart_terminal_command": self._smart_terminal_command
            }
            
            if tool_name in method_map:
                return method_map[tool_name](**arguments)
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _execute_command(self, command: str, capture_output: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Exécute une commande système"""
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "command": command
                }
            else:
                result = subprocess.run(command, shell=True, timeout=timeout)
                return {
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "command": command,
                    "message": "Commande exécutée (sortie non capturée)"
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout après {timeout} secondes"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _get_system_info(self) -> Dict[str, Any]:
        """Obtient les informations système"""
        try:
            info = self.system_detector.system_info.copy()
            
            # Ajouter des informations supplémentaires
            info.update({
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total": self._format_bytes(psutil.virtual_memory().total),
                "disk_usage": self._format_bytes(psutil.disk_usage('/').total) if self.system_detector.is_linux or self.system_detector.is_macos else None
            })
            
            if self.system_detector.is_windows:
                info["disk_usage"] = self._format_bytes(psutil.disk_usage('C:\\').total)
            
            return {
                "success": True,
                "system_info": info,
                "detected_os": self.system_detector.system_type.value
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la récupération des infos système: {str(e)}"}

    def _get_disk_usage(self, path: str = None) -> Dict[str, Any]:
        """Affiche l'utilisation du disque"""
        try:
            if path is None:
                if self.system_detector.is_windows:
                    path = "C:\\"
                else:
                    path = "/"
            
            usage = psutil.disk_usage(path)
            
            return {
                "success": True,
                "path": path,
                "total": self._format_bytes(usage.total),
                "used": self._format_bytes(usage.used),
                "free": self._format_bytes(usage.free),
                "percentage": round((usage.used / usage.total) * 100, 2),
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'analyse du disque: {str(e)}"}

    def _get_memory_info(self) -> Dict[str, Any]:
        """Affiche les informations mémoire"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "success": True,
                "virtual_memory": {
                    "total": self._format_bytes(memory.total),
                    "available": self._format_bytes(memory.available),
                    "used": self._format_bytes(memory.used),
                    "percentage": memory.percent,
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used
                },
                "swap_memory": {
                    "total": self._format_bytes(swap.total),
                    "used": self._format_bytes(swap.used),
                    "free": self._format_bytes(swap.free),
                    "percentage": swap.percent,
                    "total_bytes": swap.total,
                    "used_bytes": swap.used,
                    "free_bytes": swap.free
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'analyse mémoire: {str(e)}"}

    def _get_cpu_info(self) -> Dict[str, Any]:
        """Affiche les informations CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            return {
                "success": True,
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_usage_overall": round(sum(cpu_percent) / len(cpu_percent), 2),
                "cpu_usage_per_core": [round(usage, 2) for usage in cpu_percent],
                "cpu_frequency": {
                    "current": round(cpu_freq.current, 2) if cpu_freq else None,
                    "min": round(cpu_freq.min, 2) if cpu_freq else None,
                    "max": round(cpu_freq.max, 2) if cpu_freq else None
                } if cpu_freq else None
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'analyse CPU: {str(e)}"}

    def _list_processes(self, limit: int = 10, sort_by: str = "cpu") -> Dict[str, Any]:
        """Liste les processus"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    proc_info['memory_mb'] = round(proc.memory_info().rss / 1024 / 1024, 2)
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Trier selon le critère demandé
            if sort_by == "cpu":
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: x.get('name', '').lower())
            
            # Limiter le nombre de résultats
            if limit:
                processes = processes[:limit]
            
            return {
                "success": True,
                "processes": processes,
                "total_processes": len(psutil.pids()),
                "displayed_count": len(processes),
                "sorted_by": sort_by
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la liste des processus: {str(e)}"}

    def _open_application(self, application: str) -> Dict[str, Any]:
        """Ouvre une application selon l'OS avec recherche intelligente"""
        try:
            # Étape 1: Recherche intelligente de l'application
            search_results = self._search_application(application)
            
            if not search_results["success"]:
                return search_results
            
            # Étape 2: Tentative d'ouverture avec le nom trouvé
            app_name = search_results["found_app"]
            
            commands = {
                SystemType.MACOS: f"open -a '{app_name}'",
                SystemType.WINDOWS: f"start '{app_name}'",  
                SystemType.LINUX: app_name.lower()
            }
            
            command = self.system_detector.get_command_adapted(commands)
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Application '{app_name}' ouverte avec succès",
                    "command_used": command,
                    "original_request": application,
                    "found_app": app_name
                }
            else:
                # Si l'ouverture échoue, essayer avec le nom original
                original_command = self.system_detector.get_command_adapted({
                    SystemType.MACOS: f"open -a '{application}'",
                    SystemType.WINDOWS: f"start '{application}'",
                    SystemType.LINUX: application
                })
                
                fallback_result = subprocess.run(original_command, shell=True, capture_output=True, text=True)
                
                if fallback_result.returncode == 0:
                    return {
                        "success": True,
                        "message": f"Application '{application}' ouverte avec succès (nom original)",
                        "command_used": original_command
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Impossible d'ouvrir '{application}'. Essayé: '{app_name}' et '{application}'. Erreur: {result.stderr}",
                        "suggestions": search_results.get("suggestions", [])
                    }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'ouverture de l'application: {str(e)}"}

    def _search_application(self, app_name: str) -> Dict[str, Any]:
        """Recherche une application sur le système"""
        try:
            app_name_lower = app_name.lower()
            found_apps = []
            
            if self.system_detector.is_macos:
                # Rechercher dans les dossiers d'applications macOS
                search_commands = [
                    f"find /Applications -name '*{app_name}*' -type d -maxdepth 2 2>/dev/null",
                    f"find /System/Applications -name '*{app_name}*' -type d -maxdepth 2 2>/dev/null",
                    f"mdfind 'kMDItemKind == \"Application\"' | grep -i '{app_name}' | head -5"
                ]
                
                for cmd in search_commands:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        apps = result.stdout.strip().split('\n')
                        for app_path in apps:
                            if app_path.strip():
                                app_basename = os.path.basename(app_path).replace('.app', '')
                                found_apps.append(app_basename)
                
            elif self.system_detector.is_windows:
                # Rechercher dans le menu Démarrer Windows
                search_commands = [
                    f'powershell "Get-StartApps | Where-Object {{$_.Name -like \'*{app_name}*\'}} | Select-Object -First 5 Name"',
                    f'where {app_name}'
                ]
                
                for cmd in search_commands:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and 'Name' not in line and '---' not in line:
                                found_apps.append(line)
                                
            elif self.system_detector.is_linux:
                # Rechercher dans les applications Linux
                search_commands = [
                    f"find /usr/share/applications -name '*{app_name}*' -type f 2>/dev/null",
                    f"which {app_name_lower}",
                    f"command -v {app_name_lower}"
                ]
                
                for cmd in search_commands:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        found_apps.extend(result.stdout.strip().split('\n'))
            
            # Nettoyer et déduplication
            found_apps = list(set([app.strip() for app in found_apps if app.strip()]))
            
            if found_apps:
                # Trouver la meilleure correspondance
                best_match = None
                for app in found_apps:
                    app_clean = app.lower().replace('.app', '').replace('.exe', '')
                    if app_name_lower in app_clean or app_clean in app_name_lower:
                        best_match = app
                        break
                
                if not best_match:
                    best_match = found_apps[0]
                
                return {
                    "success": True,
                    "found_app": best_match,
                    "suggestions": found_apps[:5],
                    "search_term": app_name
                }
            else:
                return {
                    "success": False,
                    "error": f"Aucune application trouvée correspondant à '{app_name}'",
                    "suggestions": [],
                    "search_term": app_name
                }
                
        except Exception as e:
            return {
                "success": False, 
                "error": f"Erreur lors de la recherche d'application: {str(e)}",
                "found_app": app_name  # Fallback vers le nom original
            }

    def _open_url(self, url: str) -> Dict[str, Any]:
        """Ouvre une URL dans le navigateur"""
        try:
            commands = {
                SystemType.MACOS: f"open '{url}'",
                SystemType.WINDOWS: f"start '{url}'",
                SystemType.LINUX: f"xdg-open '{url}'"
            }
            
            command = self.system_detector.get_command_adapted(commands)
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"URL '{url}' ouverte dans le navigateur",
                    "command_used": command
                }
            else:
                return {
                    "success": False,
                    "error": f"Impossible d'ouvrir l'URL: {result.stderr}",
                    "command_used": command
                }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'ouverture de l'URL: {str(e)}"}

    def _format_bytes(self, bytes_value: int) -> str:
        """Formate une valeur en octets vers une unité lisible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def _find_files_terminal(self, search_pattern: str, search_path: str = None, 
                           file_type: str = "all", case_sensitive: bool = False) -> Dict[str, Any]:
        """Recherche des fichiers avec des commandes terminal natives"""
        try:
            if search_path is None:
                search_path = str(Path.home())
            
            found_files = []
            
            if self.system_detector.is_macos or self.system_detector.is_linux:
                # Construire la commande find
                find_cmd = f"find '{search_path}'"
                
                # Type de fichier
                if file_type == "file":
                    find_cmd += " -type f"
                elif file_type == "directory":
                    find_cmd += " -type d"
                
                # Sensibilité à la casse
                name_flag = "-name" if case_sensitive else "-iname"
                find_cmd += f" {name_flag} '*{search_pattern}*'"
                
                # Limiter les résultats et éviter les erreurs de permission
                find_cmd += " 2>/dev/null | head -20"
                
                result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    found_files = result.stdout.strip().split('\n')
                
            elif self.system_detector.is_windows:
                # Utiliser dir et forfiles sur Windows
                case_flag = "/C" if case_sensitive else ""
                
                if file_type == "directory":
                    cmd = f'dir "{search_path}" /AD /S /B | findstr /I "{search_pattern}"'
                else:
                    cmd = f'dir "{search_path}" /S /B | findstr /I "{search_pattern}"'
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    found_files = result.stdout.strip().split('\n')[:20]  # Limiter à 20 résultats
            
            # Nettoyer et enrichir les résultats
            enriched_results = []
            for file_path in found_files:
                file_path = file_path.strip()
                if file_path:
                    path_obj = Path(file_path)
                    try:
                        stat = path_obj.stat()
                        enriched_results.append({
                            "path": file_path,
                            "name": path_obj.name,
                            "type": "directory" if path_obj.is_dir() else "file",
                            "size": stat.st_size if path_obj.is_file() else None,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "parent": str(path_obj.parent)
                        })
                    except (OSError, PermissionError):
                        # Si on ne peut pas accéder aux stats, ajouter juste le chemin
                        enriched_results.append({
                            "path": file_path,
                            "name": path_obj.name,
                            "type": "unknown"
                        })
            
            return {
                "success": True,
                "search_pattern": search_pattern,
                "search_path": search_path,
                "file_type": file_type,
                "case_sensitive": case_sensitive,
                "found_count": len(enriched_results),
                "results": enriched_results,
                "command_used": find_cmd if self.system_detector.is_macos or self.system_detector.is_linux else cmd
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la recherche: {str(e)}"}

    def _smart_terminal_command(self, task_description: str, preferred_command: str = None) -> Dict[str, Any]:
        """Exécute une commande terminal intelligente selon la tâche demandée"""
        try:
            task_lower = task_description.lower()
            
            # Mapping des tâches courantes vers des commandes
            command_suggestions = {
                # Gestion des fichiers
                "trouver fichier": ("find", "recherche de fichiers"),
                "lister fichier": ("ls -la", "liste détaillée des fichiers"),
                "espace disque": ("df -h", "utilisation de l'espace disque"),
                "taille dossier": ("du -sh", "taille des dossiers"),
                
                # Système
                "processus": ("ps aux", "liste des processus"),
                "mémoire": ("free -h", "utilisation mémoire"),
                "cpu": ("top -n 1", "utilisation CPU"),
                "réseau": ("netstat -an", "connexions réseau"),
                
                # Applications
                "ouvrir": ("open", "ouverture d'application/fichier"),
                "chercher app": ("mdfind", "recherche d'application sur macOS"),
            }
            
            # Adapter les commandes selon l'OS
            suggested_command = None
            explanation = ""
            
            for keyword, (base_cmd, desc) in command_suggestions.items():
                if keyword in task_lower:
                    if self.system_detector.is_macos:
                        if base_cmd == "find":
                            suggested_command = f"find ~ -name '*pattern*' -type f 2>/dev/null"
                        elif base_cmd == "ls -la":
                            suggested_command = "ls -la"
                        elif base_cmd == "df -h":
                            suggested_command = "df -h"
                        elif base_cmd == "du -sh":
                            suggested_command = "du -sh *"
                        elif base_cmd == "ps aux":
                            suggested_command = "ps aux | head -10"
                        elif base_cmd == "free -h":
                            suggested_command = "vm_stat"
                        elif base_cmd == "top -n 1":
                            suggested_command = "top -l 1 -n 5"
                        elif base_cmd == "netstat -an":
                            suggested_command = "netstat -an | head -10"
                        elif base_cmd == "open":
                            suggested_command = "open -a Application"
                        elif base_cmd == "mdfind":
                            suggested_command = "mdfind 'kMDItemKind == \"Application\"'"
                        
                    elif self.system_detector.is_windows:
                        if base_cmd == "find":
                            suggested_command = 'dir /S /B | findstr "pattern"'
                        elif base_cmd == "ls -la":
                            suggested_command = "dir"
                        elif base_cmd == "df -h":
                            suggested_command = "wmic logicaldisk get caption,size,freespace"
                        elif base_cmd == "ps aux":
                            suggested_command = "tasklist"
                        elif base_cmd == "netstat -an":
                            suggested_command = "netstat -an"
                        elif base_cmd == "open":
                            suggested_command = "start application"
                        
                    else:  # Linux
                        suggested_command = base_cmd
                    
                    explanation = desc
                    break
            
            # Utiliser la commande préférée si fournie
            if preferred_command:
                command_to_execute = preferred_command
                explanation = f"Commande personnalisée: {preferred_command}"
            elif suggested_command:
                command_to_execute = suggested_command
            else:
                return {
                    "success": False,
                    "error": f"Tâche non reconnue: '{task_description}'",
                    "suggestions": list(command_suggestions.keys())
                }
            
            # Exécuter la commande
            result = subprocess.run(
                command_to_execute, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "task_description": task_description,
                "command_executed": command_to_execute,
                "explanation": explanation,
                "output": result.stdout if result.returncode == 0 else result.stderr,
                "return_code": result.returncode,
                "os_detected": self.system_detector.system_type.value
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Commande expirée (timeout)"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}
