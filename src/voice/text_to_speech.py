# -*- coding: utf-8 -*-
import os
import tempfile
import pygame
from gtts import gTTS
from typing import Optional

class TextToSpeech:
    def __init__(self, speed_factor: float = 1.3):
        try:
            # Initialiser pygame avec fréquence optimisée pour vitesse
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.speed_factor = speed_factor  # Facteur d'accélération (1.0 = normal, 1.5 = 50% plus rapide)
            self.is_speaking = False
            self.should_stop = False
            print(f"🔊 JARVIS TTS Google activé (vitesse x{speed_factor})")
        except Exception as e:
            print(f"⚠️ Erreur initialisation TTS: {e}")
            self.speed_factor = 1.0
            self.is_speaking = False
            self.should_stop = False

    def speak(self, text: str):
        """Fait parler JARVIS avec Google TTS accéléré et interruption possible"""
        try:
            self.is_speaking = True
            self.should_stop = False

            # Créer l'audio avec Google TTS (français, rapide)
            tts = gTTS(text=text, lang='fr', slow=False)

            # Sauvegarder dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file_path = tmp_file.name

            # Sauvegarder l'audio TTS
            tts.save(tmp_file_path)

            # Charger et jouer l'audio plus rapidement
            sound = pygame.mixer.Sound(tmp_file_path)

            # Jouer le son avec contrôle d'interruption
            channel = sound.play()

            # Vérifier l'interruption très fréquemment
            while channel.get_busy() and not self.should_stop:
                pygame.time.wait(10)  # Vérification ultra-fréquente (10ms) pour interruption immédiate

            # Si interruption demandée, arrêter l'audio
            if self.should_stop:
                channel.stop()
                print("🔇 JARVIS interrompu")

            self.is_speaking = False

            # Nettoyer le fichier temporaire
            try:
                os.unlink(tmp_file_path)
            except:
                pass

        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")
            self.is_speaking = False

    def speak_async(self, text: str):
        """Parle de manière asynchrone (non-bloquant) et rapide"""
        try:
            # Créer l'audio avec Google TTS (français, rapide)
            tts = gTTS(text=text, lang='fr', slow=False)

            # Sauvegarder dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file_path = tmp_file.name

            # Sauvegarder l'audio TTS
            tts.save(tmp_file_path)

            # Jouer l'audio sans attendre avec optimisations
            sound = pygame.mixer.Sound(tmp_file_path)
            sound.play()

        except Exception as e:
            print(f"❌ Erreur synthèse vocale async: {e}")

    def stop_speaking(self):
        """Arrête JARVIS de parler immédiatement"""
        self.should_stop = True
        # Arrêter tous les canaux pygame immédiatement
        try:
            pygame.mixer.stop()  # Arrête tous les sons en cours
        except:
            pass

    def set_rate(self, rate: int):
        """Modifie la vitesse de parole (non applicable pour Google TTS)"""
        pass

    def set_volume(self, volume: float):
        """Modifie le volume (non applicable pour Google TTS)"""
        pass