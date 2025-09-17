#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le nouveau système de contexte conversationnel de JARVIS
Démontre l'activation automatique après les questions
"""

from src.voice.speech_recognition import SpeechRecognizer
import time

def test_conversational_context():
    """Teste le système de contexte conversationnel"""
    print("🧪 === Test du Contexte Conversationnel JARVIS ===")
    print()
    
    sr = SpeechRecognizer()
    
    # Test 1: Mode normal - nécessite le mot-clé
    print("📋 Test 1: Mode normal")
    print(f"✅ Mot-clé requis: {sr.require_wake_word}")
    print(f"✅ En attente de réponse: {sr.is_waiting_for_response()}")
    
    # Simuler une phrase sans mot-clé
    result = sr.check_wake_word("comment ça va")
    print(f"Résultat sans mot-clé: {result}")
    print()
    
    # Test 2: Avec mot-clé
    print("📋 Test 2: Avec mot-clé")
    result = sr.check_wake_word("jarvis comment ça va")
    print(f"Résultat avec mot-clé: {result}")
    print()
    
    # Test 3: Activation du mode question
    print("📋 Test 3: Activation du mode question")
    sr.enable_response_mode()
    print(f"✅ En attente de réponse: {sr.is_waiting_for_response()}")
    
    # Tester une réponse sans mot-clé
    result = sr.check_wake_word("ça va bien merci")
    print(f"Résultat réponse sans mot-clé: {result}")
    print(f"✅ Encore en attente: {sr.is_waiting_for_response()}")
    print()
    
    # Test 4: Timeout
    print("📋 Test 4: Test du timeout (simulé)")
    sr.enable_response_mode()
    # Simuler un délai dépassé
    sr.conversation_timeout = 0.1  # 0.1 seconde pour le test
    time.sleep(0.2)
    
    result = sr.check_wake_word("réponse tardive")
    print(f"Résultat après timeout: {result}")
    print(f"✅ En attente après timeout: {sr.is_waiting_for_response()}")
    print()
    
    print("✅ Tests terminés !")
    print()
    print("🎯 Utilisation dans JARVIS :")
    print("1. JARVIS pose une question qui finit par '?'")
    print("2. Le mode attente s'active automatiquement")
    print("3. Vous pouvez répondre sans redire 'jarvis'")
    print("4. Après votre réponse, retour au mode normal")
    print("5. Timeout automatique après 30 secondes")

if __name__ == "__main__":
    test_conversational_context()
