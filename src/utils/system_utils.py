# -*- coding: utf-8 -*-
"""
Utilitaires système pour la détection automatique de plateforme
et l'adaptation des commandes selon le système d'exploitation
"""

import platform
import sys
import subprocess
import os
from typing import Dict, List, Optional, Tuple
from enum import Enum

class SystemType(Enum):
    """Types de systèmes supportés"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"

class SystemDetector:
    """Détecteur de système et adaptateur de commandes"""
    
    def __init__(self):
        self._system_type = self._detect_system()
        self._system_info = self._get_system_info()
        
    def _detect_system(self) -> SystemType:
        """Détecte le type de système d'exploitation"""
        system = platform.system().lower()
        
        if system == "windows":
            return SystemType.WINDOWS
        elif system == "darwin":
            return SystemType.MACOS
        elif system == "linux":
            return SystemType.LINUX
        else:
            return SystemType.UNKNOWN
    
    def _get_system_info(self) -> Dict[str, str]:
        """Récupère les informations détaillées du système"""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "node": platform.node()
        }
        
        # Informations spécifiques selon le système
        if self._system_type == SystemType.WINDOWS:
            info["windows_edition"] = platform.win32_edition() if hasattr(platform, 'win32_edition') else "Unknown"
            info["windows_version"] = platform.win32_ver()[0] if platform.win32_ver() else "Unknown"
            
        elif self._system_type == SystemType.MACOS:
            info["mac_version"] = platform.mac_ver()[0]
            
        return info
    
    @property
    def system_type(self) -> SystemType:
        """Retourne le type de système détecté"""
        return self._system_type
    
    @property
    def system_info(self) -> Dict[str, str]:
        """Retourne les informations système"""
        return self._system_info
    
    @property
    def is_windows(self) -> bool:
        """Vérifie si le système est Windows"""
        return self._system_type == SystemType.WINDOWS
    
    @property
    def is_macos(self) -> bool:
        """Vérifie si le système est macOS"""
        return self._system_type == SystemType.MACOS
    
    @property
    def is_linux(self) -> bool:
        """Vérifie si le système est Linux"""
        return self._system_type == SystemType.LINUX
    
    def get_command_adapted(self, command_map: Dict[SystemType, str]) -> str:
        """
        Retourne la commande adaptée au système actuel
        
        Args:
            command_map: Dictionnaire des commandes par système
            
        Returns:
            La commande adaptée au système actuel
        """
        return command_map.get(self._system_type, command_map.get(SystemType.LINUX, ""))
    
    def get_executable_path(self, program_name: str) -> Optional[str]:
        """
        Trouve le chemin d'un exécutable selon le système
        
        Args:
            program_name: Nom du programme à chercher
            
        Returns:
            Le chemin vers l'exécutable ou None si non trouvé
        """
        if self.is_windows:
            # Sur Windows, ajouter .exe si nécessaire
            if not program_name.endswith('.exe'):
                program_name += '.exe'
        
        # Utiliser 'which' sur Unix/Linux/macOS ou 'where' sur Windows
        try:
            if self.is_windows:
                result = subprocess.run(['where', program_name], 
                                      capture_output=True, text=True, check=True)
            else:
                result = subprocess.run(['which', program_name], 
                                      capture_output=True, text=True, check=True)
            
            return result.stdout.strip().split('\n')[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def check_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """
        Vérifie la disponibilité des dépendances système
        
        Args:
            dependencies: Liste des programmes à vérifier
            
        Returns:
            Dictionnaire avec le statut de chaque dépendance
        """
        status = {}
        for dep in dependencies:
            status[dep] = self.get_executable_path(dep) is not None
        return status
    
    def run_system_command(self, command_map: Dict[SystemType, str], 
                          capture_output: bool = True) -> Tuple[bool, str]:
        """
        Exécute une commande adaptée au système
        
        Args:
            command_map: Commandes par système
            capture_output: Capturer la sortie ou non
            
        Returns:
            Tuple (succès, sortie/erreur)
        """
        command = self.get_command_adapted(command_map)
        if not command:
            return False, "Commande non supportée sur ce système"
        
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    return False, result.stderr
            else:
                result = subprocess.run(command, shell=True)
                return result.returncode == 0, ""
        except Exception as e:
            return False, str(e)
    
    def get_temp_directory(self) -> str:
        """Retourne le répertoire temporaire selon le système"""
        if self.is_windows:
            return os.environ.get('TEMP', os.environ.get('TMP', 'C:\\temp'))
        else:
            return '/tmp'
    
    def get_config_directory(self, app_name: str) -> str:
        """Retourne le répertoire de configuration selon le système"""
        if self.is_windows:
            return os.path.join(os.environ.get('APPDATA', ''), app_name)
        elif self.is_macos:
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app_name)
        else:  # Linux/Unix
            return os.path.join(os.path.expanduser('~'), f'.{app_name.lower()}')
    
    def display_system_info(self):
        """Affiche les informations système détectées"""
        print(f"🖥️ Système détecté: {self._system_type.value}")
        print(f"📊 Informations système:")
        for key, value in self._system_info.items():
            print(f"   • {key}: {value}")

# Instance globale pour usage facile
system_detector = SystemDetector()

# Fonctions utilitaires pour un accès rapide
def get_system_type() -> SystemType:
    """Retourne le type de système"""
    return system_detector.system_type

def is_windows() -> bool:
    """Vérifie si le système est Windows"""
    return system_detector.is_windows

def is_macos() -> bool:
    """Vérifie si le système est macOS"""
    return system_detector.is_macos

def is_linux() -> bool:
    """Vérifie si le système est Linux"""
    return system_detector.is_linux

def adapt_command(command_map: Dict[SystemType, str]) -> str:
    """Adapte une commande au système actuel"""
    return system_detector.get_command_adapted(command_map)

def check_program_available(program: str) -> bool:
    """Vérifie si un programme est disponible"""
    return system_detector.get_executable_path(program) is not None