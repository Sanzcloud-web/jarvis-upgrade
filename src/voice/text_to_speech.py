# -*- coding: utf-8 -*-
import pyttsx3
import threading
from typing import Optional
from ..utils.system_utils import system_detector, SystemType

class TextToSpeech:
    def __init__(self, speed_factor: float = 1.3):
        # Afficher les informations système
        print(f"🖥️ Initialisation TTS sur {system_detector.system_type.value}")
        
        self.engine = None
        self.is_speaking = False
        self.should_stop = False
        
        # Essayer plusieurs méthodes d'initialisation selon le système
        self._init_tts_engine(speed_factor)
    
    def _init_tts_engine(self, speed_factor: float):
        """Initialise le moteur TTS avec gestion robuste des erreurs"""
        try:
            # Méthode 1: Initialisation standard
            self.engine = pyttsx3.init()
            self._configure_voice_for_system()
            
            # Configuration de la vitesse et du volume
            base_rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', int(base_rate * speed_factor))
            self.engine.setProperty('volume', 0.9)
            
            print(f"✅ JARVIS TTS activé avec pyttsx3 sur {system_detector.system_type.value} (vitesse x{speed_factor})")
            return
            
        except Exception as e:
            print(f"⚠️ Erreur pyttsx3 standard: {e}")
            
        # Méthode 2: Essayer avec un driver spécifique pour macOS
        if system_detector.is_macos:
            try:
                self.engine = pyttsx3.init(driverName='nsss')  # NSSpeechSynthesizer pour macOS
                self._configure_voice_for_system()
                
                base_rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', int(base_rate * speed_factor))
                self.engine.setProperty('volume', 0.9)
                
                print(f"✅ JARVIS TTS activé avec driver nsss sur macOS (vitesse x{speed_factor})")
                return
                
            except Exception as e:
                print(f"⚠️ Erreur driver nsss: {e}")
        
        # Méthode 3: Mode dégradé sans TTS
        print(f"⚠️ TTS non disponible - mode texte seulement")
        self.engine = None

    def _configure_voice_for_system(self):
        """Configure la voix selon le système d'exploitation"""
        if not self.engine:
            return
            
        voices = self.engine.getProperty('voices')
        if not voices:
            print("⚠️ Aucune voix disponible")
            return
        
        selected_voice = None
        
        if system_detector.is_windows:
            # Sur Windows, chercher des voix françaises spécifiques
            french_voices = [
                'Hortense',  # Voix française Windows
                'Julie',     # Voix française alternative
                'French'     # Nom générique
            ]
            
            for voice in voices:
                voice_name = voice.name.lower()
                if any(french in voice_name for french in ['french', 'hortense', 'julie', 'fr-fr']):
                    selected_voice = voice
                    break
                    
        elif system_detector.is_macos:
            # Sur macOS, chercher des voix françaises spécifiques
            french_voices = [
                'Amelie',    # Voix française macOS
                'Thomas',    # Voix française alternative
                'French'     # Nom générique
            ]
            
            for voice in voices:
                voice_name = voice.name.lower()
                if any(french in voice_name for french in ['amelie', 'thomas', 'french', 'fr_fr']):
                    selected_voice = voice
                    break
                    
        elif system_detector.is_linux:
            # Sur Linux, chercher des voix françaises disponibles
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower() if hasattr(voice, 'id') else ''
                if any(french in voice_name + voice_id for french in ['french', 'fr', 'france']):
                    selected_voice = voice
                    break
        
        # Si aucune voix française trouvée, chercher de manière générique
        if not selected_voice:
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower() if hasattr(voice, 'id') else ''
                if 'fr' in voice_name or 'fr' in voice_id or 'french' in voice_name:
                    selected_voice = voice
                    break
        
        # Configurer la voix sélectionnée
        if selected_voice:
            self.engine.setProperty('voice', selected_voice.id)
            print(f"✅ Voix sélectionnée: {selected_voice.name}")
        else:
            # Utiliser la première voix disponible par défaut
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                print(f"⚠️ Voix par défaut: {voices[0].name} (aucune voix française trouvée)")
            else:
                print("❌ Aucune voix disponible")

    def speak(self, text: str):
        """Fait parler JARVIS avec différentes méthodes selon la disponibilité"""
        if not text.strip():
            return
            
        # Méthode 1: Utiliser pyttsx3 si disponible
        if self.engine:
            try:
                self.is_speaking = True
                self.should_stop = False

                # Parler directement tout le texte
                self.engine.say(text)
                self.engine.runAndWait()

                self.is_speaking = False
                return

            except KeyboardInterrupt:
                # Gestion de l'interruption par Ctrl+C
                if self.engine:
                    self.engine.stop()
                self.is_speaking = False
                raise  # Relancer l'exception pour qu'elle soit gérée au niveau supérieur
            except Exception as e:
                print(f"⚠️ Erreur pyttsx3: {e}")
                self.is_speaking = False
        
        # Méthode 2: Utiliser la commande système native
        self._speak_with_system_command(text)
    
    def _speak_with_system_command(self, text: str):
        """Utilise les commandes système natives pour la synthèse vocale"""
        import subprocess
        import shlex
        
        try:
            self.is_speaking = True
            
            if system_detector.is_macos:
                # Sur macOS, utiliser la commande 'say'
                safe_text = shlex.quote(text)
                subprocess.run(['say', '-v', 'Thomas', text], check=True)
                print("🔊 TTS via commande 'say' sur macOS")
                
            elif system_detector.is_windows:
                # Sur Windows, utiliser PowerShell et SAPI
                ps_command = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
                subprocess.run(['powershell', '-Command', ps_command], check=True)
                print("🔊 TTS via PowerShell SAPI sur Windows")
                
            elif system_detector.is_linux:
                # Sur Linux, essayer espeak ou festival
                try:
                    subprocess.run(['espeak', '-v', 'fr', text], check=True)
                    print("🔊 TTS via espeak sur Linux")
                except FileNotFoundError:
                    try:
                        subprocess.run(['festival', '--tts'], input=text, text=True, check=True)
                        print("🔊 TTS via festival sur Linux")
                    except FileNotFoundError:
                        print(f"💬 JARVIS dit: {text}")
                        print("ℹ️ Installez espeak ou festival pour la synthèse vocale")
            else:
                # Système non supporté - affichage texte seulement
                print(f"💬 JARVIS dit: {text}")
                
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erreur commande système TTS: {e}")
            print(f"💬 JARVIS dit: {text}")
        except Exception as e:
            print(f"⚠️ Erreur TTS système: {e}")
            print(f"💬 JARVIS dit: {text}")
        finally:
            self.is_speaking = False
    

    def speak_async(self, text: str):
        """Parle de manière asynchrone (non-bloquant)"""
        speak_thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        speak_thread.start()

    def stop_speaking(self):
        """Arrête JARVIS de parler immédiatement"""
        self.should_stop = True
        if self.engine:
            try:
                self.engine.stop()  # Arrête le moteur TTS immédiatement
            except:
                pass

    def set_rate(self, rate: int):
        """Modifie la vitesse de parole"""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass

    def set_volume(self, volume: float):
        """Modifie le volume (0.0 à 1.0)"""
        if self.engine:
            try:
                self.engine.setProperty('volume', min(1.0, max(0.0, volume)))
            except:
                pass