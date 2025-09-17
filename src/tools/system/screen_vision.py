# -*- coding: utf-8 -*-
"""
Module de vision d'écran pour JARVIS
Capture d'écran et analyse par IA
"""

import base64
import io
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import pyautogui
    from PIL import Image
    SCREEN_AVAILABLE = True
except ImportError:
    SCREEN_AVAILABLE = False

from ...utils.system_utils import system_detector, SystemType

class ScreenVision:
    def __init__(self):
        """Initialise le module de vision d'écran"""
        self.system_detector = system_detector
        
        # Configuration selon l'OS
        if SCREEN_AVAILABLE:
            # Désactiver le failsafe de pyautogui sur macOS
            if self.system_detector.system_type == SystemType.MACOS:
                pyautogui.FAILSAFE = False
        
        # Dossier temporaire pour les captures
        self.temp_dir = Path(tempfile.gettempdir()) / "jarvis_screenshots"
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils de vision d'écran"""
        if not SCREEN_AVAILABLE:
            return []
            
        return [
            {
                "type": "function",
                "function": {
                    "name": "screenshot_and_analyze",
                    "description": "Capture l'écran et demande à l'IA d'analyser ce qui est visible",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "analysis_prompt": {
                                "type": "string",
                                "description": "Question ou instruction spécifique pour l'analyse (ex: 'Que vois-tu ?', 'Aide-moi avec ce code', 'Résume ce texte')"
                            },
                            "save_screenshot": {
                                "type": "boolean", 
                                "description": "Sauvegarder la capture d'écran dans un fichier (défaut: false)"
                            },
                            "region": {
                                "type": "object",
                                "description": "Zone spécifique à capturer (optionnel)",
                                "properties": {
                                    "x": {"type": "integer", "description": "Position X"},
                                    "y": {"type": "integer", "description": "Position Y"},
                                    "width": {"type": "integer", "description": "Largeur"},
                                    "height": {"type": "integer", "description": "Hauteur"}
                                }
                            }
                        },
                        "required": ["analysis_prompt"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_screenshot",
                    "description": "Prend une capture d'écran simple et la sauvegarde",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier (optionnel, sinon généré automatiquement)"
                            },
                            "save_path": {
                                "type": "string", 
                                "description": "Chemin de sauvegarde (optionnel, sinon bureau/dossier temporaire)"
                            },
                            "region": {
                                "type": "object",
                                "description": "Zone spécifique à capturer (optionnel)", 
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"},
                                    "width": {"type": "integer"},
                                    "height": {"type": "integer"}
                                }
                            }
                        },
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_screen_info",
                    "description": "Obtient les informations sur l'écran (résolution, nombre d'écrans, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil de vision d'écran"""
        if not SCREEN_AVAILABLE:
            return {
                "success": False,
                "error": "Modules de capture d'écran non disponibles. Installez: pip install pillow pyautogui"
            }
        
        try:
            method_map = {
                "screenshot_and_analyze": self._screenshot_and_analyze,
                "take_screenshot": self._take_screenshot,
                "get_screen_info": self._get_screen_info
            }
            
            if tool_name in method_map:
                return method_map[tool_name](**arguments)
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}
    
    def _screenshot_and_analyze(self, analysis_prompt: str, save_screenshot: bool = False, 
                               region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Capture l'écran et demande à l'IA d'analyser
        
        Args:
            analysis_prompt: Question pour l'analyse
            save_screenshot: Sauvegarder la capture
            region: Zone spécifique à capturer
            
        Returns:
            Résultat de l'analyse avec la réponse de l'IA
        """
        try:
            # Prendre la capture d'écran
            screenshot_result = self._take_screenshot_internal(region=region)
            
            if not screenshot_result["success"]:
                return screenshot_result
                
            image_path = screenshot_result["file_path"]
            
            # Convertir l'image en base64 pour l'API Vision
            base64_image = self._image_to_base64(image_path)
            
            if not base64_image:
                return {
                    "success": False,
                    "error": "Erreur lors de la conversion de l'image en base64"
                }
            
            # Préparer pour l'analyse IA (sera implémenté dans OpenAI client)
            result = {
                "success": True,
                "screenshot_taken": True,
                "screenshot_path": image_path,
                "screenshot_base64": base64_image,
                "analysis_prompt": analysis_prompt,
                "timestamp": datetime.now().isoformat(),
                "screen_resolution": screenshot_result.get("resolution"),
                "requires_vision_analysis": True,  # Signal pour OpenAI client
                "message": "Capture d'écran prise avec succès. Analyse en cours..."
            }
            
            # Sauvegarder si demandé
            if save_screenshot:
                # Copier vers un fichier permanent
                permanent_path = self._save_permanent_screenshot(image_path)
                result["permanent_path"] = permanent_path
                result["saved"] = True
            else:
                result["saved"] = False
                
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la capture et analyse: {str(e)}"
            }
    
    def _take_screenshot(self, filename: Optional[str] = None, 
                        save_path: Optional[str] = None,
                        region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Prend une capture d'écran simple
        
        Args:
            filename: Nom du fichier
            save_path: Chemin de sauvegarde
            region: Zone à capturer
            
        Returns:
            Informations sur la capture
        """
        try:
            # Générer le nom de fichier si pas fourni
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            elif not filename.endswith(('.png', '.jpg', '.jpeg')):
                filename += ".png"
            
            # Déterminer le chemin de sauvegarde
            if save_path:
                save_dir = Path(save_path)
                save_dir.mkdir(parents=True, exist_ok=True)
                full_path = save_dir / filename
            else:
                # Sauvegarder sur le bureau par défaut
                desktop_path = self._get_desktop_path()
                full_path = desktop_path / filename
            
            # Prendre la capture
            if region:
                screenshot = pyautogui.screenshot(region=(
                    region["x"], region["y"], 
                    region["width"], region["height"]
                ))
            else:
                screenshot = pyautogui.screenshot()
            
            # Sauvegarder
            screenshot.save(str(full_path))
            
            return {
                "success": True,
                "file_path": str(full_path),
                "filename": filename,
                "resolution": f"{screenshot.width}x{screenshot.height}",
                "size_bytes": os.path.getsize(full_path),
                "timestamp": datetime.now().isoformat(),
                "region": region if region else "full_screen"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la capture d'écran: {str(e)}"
            }
    
    def _get_screen_info(self) -> Dict[str, Any]:
        """Obtient les informations sur l'écran"""
        try:
            # Informations de base
            screen_width, screen_height = pyautogui.size()
            
            info = {
                "success": True,
                "primary_screen": {
                    "width": screen_width,
                    "height": screen_height,
                    "resolution": f"{screen_width}x{screen_height}"
                },
                "screenshot_capability": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Tentative d'obtenir plus d'infos via PIL
            try:
                from PIL import ImageGrab
                # Test de capture pour vérifier les capacités
                test_img = ImageGrab.grab(bbox=(0, 0, 100, 100))
                info["pil_available"] = True
                info["color_mode"] = test_img.mode
            except:
                info["pil_available"] = False
            
            return info
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la récupération des infos écran: {str(e)}"
            }
    
    def _take_screenshot_internal(self, region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Prend une capture interne pour analyse"""
        try:
            # Prendre la capture
            if region:
                screenshot = pyautogui.screenshot(region=(
                    region["x"], region["y"], 
                    region["width"], region["height"]
                ))
            else:
                screenshot = pyautogui.screenshot()
            
            # Sauvegarder temporairement
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            temp_filename = f"jarvis_temp_{timestamp}.png"
            temp_path = self.temp_dir / temp_filename
            
            screenshot.save(str(temp_path))
            
            return {
                "success": True,
                "file_path": str(temp_path),
                "resolution": f"{screenshot.width}x{screenshot.height}",
                "size_bytes": os.path.getsize(temp_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur capture interne: {str(e)}"
            }
    
    def _image_to_base64(self, image_path: str) -> Optional[str]:
        """Convertit une image en base64 pour l'API Vision"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                return base64_string
        except Exception as e:
            print(f"Erreur conversion base64: {e}")
            return None
    
    def _save_permanent_screenshot(self, temp_path: str) -> str:
        """Sauvegarde une capture temporaire de façon permanente"""
        try:
            desktop_path = self._get_desktop_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            permanent_filename = f"jarvis_screenshot_{timestamp}.png"
            permanent_path = desktop_path / permanent_filename
            
            # Copier le fichier temporaire
            import shutil
            shutil.copy2(temp_path, permanent_path)
            
            return str(permanent_path)
            
        except Exception as e:
            print(f"Erreur sauvegarde permanente: {e}")
            return temp_path
    
    def _get_desktop_path(self) -> Path:
        """Obtient le chemin vers le bureau selon l'OS"""
        if self.system_detector.system_type == SystemType.MACOS:
            return Path.home() / "Desktop"
        elif self.system_detector.system_type == SystemType.WINDOWS:
            return Path.home() / "Desktop"
        else:  # Linux
            # Essayer plusieurs possibilités
            for desktop_name in ["Desktop", "Bureau", "Escritorio"]:
                desktop_path = Path.home() / desktop_name
                if desktop_path.exists():
                    return desktop_path
            # Fallback vers home
            return Path.home()
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> Dict[str, Any]:
        """Nettoie les fichiers temporaires anciens"""
        try:
            import time
            
            cleaned_count = 0
            cleaned_size = 0
            current_time = time.time()
            cutoff_time = current_time - (older_than_hours * 3600)
            
            for temp_file in self.temp_dir.glob("jarvis_temp_*.png"):
                if temp_file.stat().st_mtime < cutoff_time:
                    file_size = temp_file.stat().st_size
                    temp_file.unlink()
                    cleaned_count += 1
                    cleaned_size += file_size
            
            return {
                "success": True,
                "cleaned_files": cleaned_count,
                "cleaned_size_bytes": cleaned_size,
                "cleaned_size_mb": round(cleaned_size / (1024*1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur nettoyage: {str(e)}"
            }
