# -*- coding: utf-8 -*-
import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.voice_queue = queue.Queue()
        
        # Configuration du mot-clé d'activation
        self.wake_word = "jarvis"
        self.require_wake_word = True

        # Calibrage automatique
        self.calibrate_microphone()

    def calibrate_microphone(self):
        """Calibre le microphone pour réduire le bruit ambiant"""
        try:
            print("🎤 Calibrage du microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibré !")
        except Exception as e:
            print(f"⚠️ Erreur calibrage micro: {e}")
    
    def check_wake_word(self, text: str) -> Optional[str]:
        """Vérifie si le mot-clé d'activation est présent et retourne le message sans le mot-clé"""
        if not self.require_wake_word:
            return text
            
        if not text:
            return None
            
        # Convertir en minuscules pour la comparaison
        text_lower = text.lower().strip()
        wake_word_lower = self.wake_word.lower()
        
        # Vérifier si la phrase commence par le mot-clé
        if text_lower.startswith(wake_word_lower):
            # Extraire le message après le mot-clé
            remaining_text = text[len(self.wake_word):].strip()
            if remaining_text:  # S'assurer qu'il y a du contenu après "jarvis"
                print(f"🎯 Mot-clé '{self.wake_word}' détecté - Message: '{remaining_text}'")
                return remaining_text
            else:
                print(f"👋 Bonjour ! Dites 'jarvis' suivi de votre demande.")
                return None
        else:
            print(f"💤 Mot-clé '{self.wake_word}' non détecté au début - Ignoré")
            return None

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Écoute une fois et retourne le texte reconnu après vérification du mot-clé"""
        try:
            if self.require_wake_word:
                print(f"🎤 Dites '{self.wake_word}' puis votre demande...")
            else:
                print("🎤 Écoute en cours... (parlez maintenant)")

            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            print("🔄 Reconnaissance en cours...")

            # Reconnaissance vocale français
            raw_text = self.recognizer.recognize_google(audio, language='fr-FR')
            print(f"📝 Reconnu: {raw_text}")
            
            # Vérifier le mot-clé d'activation
            processed_text = self.check_wake_word(raw_text)
            return processed_text

        except sr.WaitTimeoutError:
            print("⏰ Timeout - aucune parole détectée")
            return None
        except sr.UnknownValueError:
            print("❌ Impossible de comprendre l'audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Erreur service reconnaissance: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur écoute: {e}")
            return None

    def listen_continuous(self, callback: Callable[[str], None]):
        """Écoute en continu et appelle le callback pour chaque phrase avec mot-clé"""
        def listen_worker():
            if self.require_wake_word:
                print(f"🎤 Écoute continue activée - Dites '{self.wake_word}' pour interagir")
            else:
                print("🎤 Écoute continue activée")

            while self.is_listening:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)

                    try:
                        raw_text = self.recognizer.recognize_google(audio, language='fr-FR')

                        # Vérifier commande d'arrêt (toujours actives même sans mot-clé)
                        if any(word in raw_text.lower() for word in ['arrêter', 'stop', 'pause', 'silence']):
                            print("🔇 Écoute continue désactivée")
                            self.is_listening = False
                            break

                        # Vérifier le mot-clé d'activation
                        processed_text = self.check_wake_word(raw_text)
                        if processed_text:
                            callback(processed_text)

                    except (sr.UnknownValueError, sr.RequestError):
                        pass

                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Erreur écoute continue: {e}")
                    time.sleep(1)

        self.is_listening = True
        listen_thread = threading.Thread(target=listen_worker, daemon=True)
        listen_thread.start()

    def stop_listening(self):
        """Arrête l'écoute continue"""
        self.is_listening = False
    
    def set_wake_word_required(self, required: bool):
        """Active ou désactive l'exigence du mot-clé d'activation"""
        self.require_wake_word = required
        if required:
            print(f"🎯 Activation par mot-clé '{self.wake_word}' activée")
        else:
            print("🔓 Mode libre activé (sans mot-clé)")
    
    def set_wake_word(self, wake_word: str):
        """Change le mot-clé d'activation"""
        old_word = self.wake_word
        self.wake_word = wake_word.lower().strip()
        print(f"🔄 Mot-clé changé: '{old_word}' → '{self.wake_word}'")