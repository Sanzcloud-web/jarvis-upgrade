# -*- coding: utf-8 -*-
"""
Calculatrice avancée avec support des expressions mathématiques
"""

import math
import re
from typing import Dict, Any, List

class Calculator:
    def __init__(self):
        self.allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        self.allowed_names.update({"abs": abs, "round": round})

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils de calcul"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Effectue un calcul mathématique à partir d'une expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Expression mathématique à calculer (ex: '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)')"
                            }
                        },
                        "required": ["expression"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "convert_units",
                    "description": "Convertit des unités de mesure",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "description": "Valeur à convertir"
                            },
                            "from_unit": {
                                "type": "string",
                                "description": "Unité de départ (ex: 'km', 'lb', 'celsius')"
                            },
                            "to_unit": {
                                "type": "string",
                                "description": "Unité d'arrivée (ex: 'm', 'kg', 'fahrenheit')"
                            }
                        },
                        "required": ["value", "from_unit", "to_unit"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "percentage_calculation",
                    "description": "Calculs de pourcentages",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Type d'opération: 'percentage_of', 'what_percentage', 'add_percentage', 'subtract_percentage'"
                            },
                            "value1": {
                                "type": "number",
                                "description": "Première valeur"
                            },
                            "value2": {
                                "type": "number",
                                "description": "Deuxième valeur ou pourcentage"
                            }
                        },
                        "required": ["operation", "value1", "value2"],
                        "additionalProperties": False
                    },
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés"""
        try:
            method_map = {
                "calculate": self._calculate,
                "convert_units": self._convert_units,
                "percentage_calculation": self._percentage_calculation
            }
            
            if tool_name in method_map:
                return method_map[tool_name](**arguments)
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _calculate(self, expression: str) -> Dict[str, Any]:
        """Calcule une expression mathématique"""
        try:
            # Nettoyer l'expression
            expression = expression.strip()
            
            # Remplacer quelques alias courants
            replacements = {
                'π': 'pi',
                '×': '*',
                '÷': '/',
                '²': '**2',
                '³': '**3',
                '^': '**'
            }
            
            for old, new in replacements.items():
                expression = expression.replace(old, new)
            
            # Vérifier la sécurité de l'expression
            if not self._is_safe_expression(expression):
                return {"success": False, "error": "Expression non autorisée pour des raisons de sécurité"}
            
            # Évaluer l'expression
            result = eval(expression, {"__builtins__": {}}, self.allowed_names)
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "formatted_result": f"{result:,.6g}".rstrip('0').rstrip('.') if isinstance(result, float) else str(result)
            }
        except ZeroDivisionError:
            return {"success": False, "error": "Division par zéro"}
        except ValueError as e:
            return {"success": False, "error": f"Erreur de valeur: {str(e)}"}
        except SyntaxError:
            return {"success": False, "error": "Syntaxe d'expression invalide"}
        except Exception as e:
            return {"success": False, "error": f"Erreur de calcul: {str(e)}"}

    def _is_safe_expression(self, expression: str) -> bool:
        """Vérifie si l'expression est sûre à évaluer"""
        # Interdire certains mots-clés dangereux
        forbidden = ['import', 'exec', 'eval', 'open', 'file', '__', 'globals', 'locals']
        expression_lower = expression.lower()
        
        for word in forbidden:
            if word in expression_lower:
                return False
        
        # Autoriser seulement certains caractères
        allowed_chars = set('0123456789+-*/().abcdefghijklmnopqrstuvwxyz_,= ')
        return all(c in allowed_chars for c in expression_lower)

    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Convertit des unités"""
        try:
            conversions = {
                # Longueur (tout en mètres)
                'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000,
                'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.34,
                
                # Poids (tout en kilogrammes)
                'g': 0.001, 'kg': 1, 't': 1000,
                'oz': 0.0283495, 'lb': 0.453592,
                
                # Température (cas spécial)
                'celsius': 'C', 'fahrenheit': 'F', 'kelvin': 'K',
                
                # Volume (tout en litres)
                'ml': 0.001, 'l': 1, 'gal': 3.78541,
                
                # Superficie (tout en mètres carrés)
                'm2': 1, 'km2': 1000000, 'ha': 10000,
                'ft2': 0.092903, 'acre': 4046.86
            }
            
            from_unit = from_unit.lower()
            to_unit = to_unit.lower()
            
            # Cas spécial pour la température
            if from_unit in ['celsius', 'fahrenheit', 'kelvin']:
                return self._convert_temperature(value, from_unit, to_unit)
            
            if from_unit not in conversions or to_unit not in conversions:
                return {"success": False, "error": f"Unité non supportée: {from_unit} ou {to_unit}"}
            
            # Conversion via l'unité de base
            base_value = value * conversions[from_unit]
            result = base_value / conversions[to_unit]
            
            return {
                "success": True,
                "original_value": value,
                "original_unit": from_unit,
                "converted_value": round(result, 6),
                "converted_unit": to_unit,
                "formatted": f"{value} {from_unit} = {result:.6g} {to_unit}"
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur de conversion: {str(e)}"}

    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Convertit la température"""
        try:
            # Convertir d'abord vers Celsius
            if from_unit == 'fahrenheit':
                celsius = (value - 32) * 5/9
            elif from_unit == 'kelvin':
                celsius = value - 273.15
            else:  # celsius
                celsius = value
            
            # Puis vers l'unité cible
            if to_unit == 'fahrenheit':
                result = celsius * 9/5 + 32
            elif to_unit == 'kelvin':
                result = celsius + 273.15
            else:  # celsius
                result = celsius
            
            return {
                "success": True,
                "original_value": value,
                "original_unit": from_unit,
                "converted_value": round(result, 2),
                "converted_unit": to_unit,
                "formatted": f"{value}° {from_unit} = {result:.2f}° {to_unit}"
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur de conversion température: {str(e)}"}

    def _percentage_calculation(self, operation: str, value1: float, value2: float) -> Dict[str, Any]:
        """Calculs de pourcentages"""
        try:
            result = None
            description = ""
            
            if operation == "percentage_of":
                # value2% de value1
                result = (value2 / 100) * value1
                description = f"{value2}% de {value1} = {result}"
                
            elif operation == "what_percentage":
                # value1 est quel pourcentage de value2
                if value2 == 0:
                    return {"success": False, "error": "Division par zéro"}
                result = (value1 / value2) * 100
                description = f"{value1} est {result}% de {value2}"
                
            elif operation == "add_percentage":
                # Ajouter value2% à value1
                result = value1 + (value1 * value2 / 100)
                description = f"{value1} + {value2}% = {result}"
                
            elif operation == "subtract_percentage":
                # Soustraire value2% de value1
                result = value1 - (value1 * value2 / 100)
                description = f"{value1} - {value2}% = {result}"
                
            else:
                return {"success": False, "error": f"Opération inconnue: {operation}"}
            
            return {
                "success": True,
                "operation": operation,
                "value1": value1,
                "value2": value2,
                "result": round(result, 6),
                "description": description
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur de calcul de pourcentage: {str(e)}"}
