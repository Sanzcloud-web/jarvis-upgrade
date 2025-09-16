# -*- coding: utf-8 -*-
import os
import tempfile
import pygame
from gtts import gTTS
from typing import Optional

class TextToSpeech:
    def __init__(self):
        try:
            # Initialiser pygame pour la lecture audio
            pygame.mixer.init()
            print("🔊 JARVIS TTS Google activé")
        except Exception as e:
            print(f"⚠️ Erreur initialisation TTS: {e}")

    def speak(self, text: str):
        """Fait parler JARVIS avec Google TTS"""
        try:
            print(f"🔊 JARVIS dit: {text}")

            # Créer l'audio avec Google TTS (français)
            tts = gTTS(text=text, lang='fr', slow=False)

            # Sauvegarder dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file_path = tmp_file.name

            # Sauvegarder l'audio TTS
            tts.save(tmp_file_path)

            # Jouer l'audio
            pygame.mixer.music.load(tmp_file_path)
            pygame.mixer.music.play()

            # Attendre que l'audio soit terminé
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

            # Nettoyer le fichier temporaire
            try:
                os.unlink(tmp_file_path)
            except:
                pass

        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")

    def speak_async(self, text: str):
        """Parle de manière asynchrone (non-bloquant)"""
        try:
            # Créer l'audio avec Google TTS (français)
            tts = gTTS(text=text, lang='fr', slow=False)

            # Sauvegarder dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file_path = tmp_file.name

            # Sauvegarder l'audio TTS
            tts.save(tmp_file_path)

            # Jouer l'audio sans attendre
            pygame.mixer.music.load(tmp_file_path)
            pygame.mixer.music.play()

        except Exception as e:
            print(f"❌ Erreur synthèse vocale async: {e}")

    def set_rate(self, rate: int):
        """Modifie la vitesse de parole (non applicable pour Google TTS)"""
        pass

    def set_volume(self, volume: float):
        """Modifie le volume (non applicable pour Google TTS)"""
        pass