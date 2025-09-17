#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration des nouveaux outils JARVIS
"""

import sys
import os

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.tool_manager import ToolManager

def demo_outils():
    """Démonstration des outils JARVIS"""
    print("🎯 === DÉMONSTRATION DES OUTILS JARVIS ===\n")
    
    # Initialiser le gestionnaire d'outils
    tool_manager = ToolManager()
    
    print("📊 Outils disponibles:")
    categories = tool_manager.get_tools_by_category()
    for category, tools in categories.items():
        print(f"  {category}: {len(tools)} outils")
    print()
    
    # Tests de démonstration
    demos = [
        {
            "title": "🕒 Date et heure actuelles",
            "tool": "get_current_time",
            "args": {"format": "french"}
        },
        {
            "title": "🧮 Calcul mathématique",
            "tool": "calculate", 
            "args": {"expression": "sqrt(144) + 5 * 2"}
        },
        {
            "title": "🌡️ Conversion d'unités",
            "tool": "convert_units",
            "args": {"value": 25, "from_unit": "celsius", "to_unit": "fahrenheit"}
        },
        {
            "title": "📁 Liste des fichiers sur le bureau",
            "tool": "list_files",
            "args": {}
        },
        {
            "title": "⚙️ Informations système",
            "tool": "get_system_info", 
            "args": {}
        },
        {
            "title": "💾 Utilisation de la mémoire",
            "tool": "get_memory_info",
            "args": {}
        },
        {
            "title": "🔍 Recherche de fichiers avec terminal", 
            "tool": "find_files_terminal",
            "args": {"search_pattern": "jarvis", "file_type": "all"}
        },
        {
            "title": "🧠 Commande terminal intelligente",
            "tool": "smart_terminal_command",
            "args": {"task_description": "voir l'espace disque disponible"}
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"{i}. {demo['title']}")
        print("-" * 50)
        
        try:
            result = tool_manager.execute_tool(demo['tool'], demo['args'])
            
            if result["success"]:
                print("✅ Succès !")
                
                # Affichage personnalisé selon le type de résultat
                if "current_time" in result:
                    print(f"   📅 {result['current_time']}")
                    print(f"   📍 Jour: {result['weekday']}")
                
                elif "result" in result and "expression" in result:
                    print(f"   🔢 {result['expression']} = {result['result']}")
                
                elif "converted_value" in result:
                    print(f"   🌡️ {result['formatted']}")
                
                elif "items" in result:
                    total = result.get('total_count', 0)
                    files = result.get('files_count', 0)
                    dirs = result.get('directories_count', 0)
                    print(f"   📊 {total} éléments ({files} fichiers, {dirs} dossiers)")
                
                elif "system_info" in result:
                    info = result['system_info']
                    print(f"   💻 Système: {info.get('system', 'Inconnu')}")
                    print(f"   🏗️ Architecture: {info.get('architecture', 'Inconnu')}")
                    print(f"   🔧 CPU: {info.get('cpu_count', '?')} cœurs")
                
                elif "virtual_memory" in result:
                    mem = result['virtual_memory']
                    print(f"   💾 RAM totale: {mem['total']}")
                    print(f"   ✅ RAM disponible: {mem['available']}")
                    print(f"   📊 Utilisation: {mem['percentage']}%")
                
                elif "found_count" in result:
                    print(f"   🔍 {result['found_count']} éléments trouvés")
                    if result['found_count'] > 0:
                        for item in result['results'][:3]:
                            print(f"      📁 {item['name']} ({item['type']})")
                        if result['found_count'] > 3:
                            print(f"      ... et {result['found_count'] - 3} autres")
                
                elif "command_executed" in result:
                    print(f"   🖥️ Commande: {result['command_executed']}")
                    if result.get('output'):
                        output_lines = result['output'].split('\n')[:3]
                        for line in output_lines:
                            if line.strip():
                                print(f"      {line.strip()}")
                        if len(result['output'].split('\n')) > 3:
                            print("      ...")
                
            else:
                print(f"❌ Erreur: {result['error']}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print()
    
    print("🎉 Démonstration terminée !")
    print("\n💡 Pour utiliser ces outils dans JARVIS:")
    print("   • Mode vocal: 'JARVIS outils' puis 'JARVIS test outils'")
    print("   • Mode texte: tapez 'outils' puis 'test outils'")
    print("\n🚀 Explorez toutes les possibilités avec 'outil [nom_de_l_outil]' pour plus d'infos !")

if __name__ == "__main__":
    try:
        demo_outils()
    except KeyboardInterrupt:
        print("\n\n👋 Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {str(e)}")
        print("Assurez-vous que toutes les dépendances sont installées (pip install -r requirements.txt)")
