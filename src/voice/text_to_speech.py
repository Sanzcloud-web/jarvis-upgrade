# -*- coding: utf-8 -*-
import pyttsx3
import threading
from typing import Optional

class TextToSpeech:
    def __init__(self, speed_factor: float = 1.3):
        try:
            # Initialiser pyttsx3 pour TTS en temps réel
            self.engine = pyttsx3.init()
            
            # Configuration de la voix
            voices = self.engine.getProperty('voices')
            if voices:
                # Essayer de trouver une voix française
                for voice in voices:
                    if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Configuration de la vitesse et du volume
            base_rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', int(base_rate * speed_factor))
            self.engine.setProperty('volume', 0.9)
            
            self.is_speaking = False
            self.should_stop = False
            print(f"🔊 JARVIS TTS basique activé (vitesse x{speed_factor})")
        except Exception as e:
            print(f"⚠️ Erreur initialisation TTS: {e}")
            self.engine = None
            self.is_speaking = False
            self.should_stop = False

    def speak(self, text: str):
        """Fait parler JARVIS avec pyttsx3 de manière simple et efficace"""
        if not self.engine:
            print("❌ Moteur TTS non disponible")
            return
            
        try:
            self.is_speaking = True
            self.should_stop = False

            # Parler directement tout le texte
            self.engine.say(text)
            self.engine.runAndWait()

            self.is_speaking = False

        except KeyboardInterrupt:
            # Gestion de l'interruption par Ctrl+C
            self.engine.stop()
            self.is_speaking = False
            raise  # Relancer l'exception pour qu'elle soit gérée au niveau supérieur
        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")
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