# -*- coding: utf-8 -*-
"""
Outils de date et heure
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import calendar

class DateTimeTools:
    def __init__(self):
        pass

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne les schémas des outils de date/heure"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "Obtient la date et l'heure actuelles",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "description": "Format de sortie (iso, custom, french)"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_time",
                    "description": "Ajoute du temps à une date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base_date": {
                                "type": "string",
                                "description": "Date de base (format ISO ou 'now' pour maintenant)"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Nombre de jours à ajouter"
                            },
                            "hours": {
                                "type": "integer",
                                "description": "Nombre d'heures à ajouter"
                            },
                            "minutes": {
                                "type": "integer",
                                "description": "Nombre de minutes à ajouter"
                            }
                        },
                        "required": ["base_date"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_age",
                    "description": "Calcule l'âge à partir d'une date de naissance",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "birth_date": {
                                "type": "string",
                                "description": "Date de naissance (format YYYY-MM-DD)"
                            }
                        },
                        "required": ["birth_date"],
                        "additionalProperties": False
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_calendar",
                    "description": "Affiche le calendrier d'un mois",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "integer",
                                "description": "Année (défaut: année actuelle)"
                            },
                            "month": {
                                "type": "integer",
                                "description": "Mois (1-12, défaut: mois actuel)"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés"""
        try:
            method_map = {
                "get_current_time": self._get_current_time,
                "add_time": self._add_time,
                "calculate_age": self._calculate_age,
                "get_calendar": self._get_calendar
            }
            
            if tool_name in method_map:
                return method_map[tool_name](**arguments)
            else:
                return {"success": False, "error": f"Outil inconnu: {tool_name}"}
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'exécution: {str(e)}"}

    def _get_current_time(self, format: str = "iso") -> Dict[str, Any]:
        """Obtient la date et l'heure actuelles"""
        try:
            now = datetime.now()
            
            formats = {
                "iso": now.isoformat(),
                "french": now.strftime("%d/%m/%Y à %H:%M:%S"),
                "custom": now.strftime("%A %d %B %Y, %H:%M:%S")
            }
            
            return {
                "success": True,
                "current_time": formats.get(format, now.isoformat()),
                "timestamp": now.timestamp(),
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
                "weekday": now.strftime("%A"),
                "timezone": str(now.astimezone().tzinfo)
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la récupération de l'heure: {str(e)}"}

    def _add_time(self, base_date: str, days: int = 0, hours: int = 0, minutes: int = 0) -> Dict[str, Any]:
        """Ajoute du temps à une date"""
        try:
            if base_date.lower() == "now":
                base_dt = datetime.now()
            else:
                base_dt = datetime.fromisoformat(base_date.replace('Z', '+00:00'))
            
            result_dt = base_dt + timedelta(days=days, hours=hours, minutes=minutes)
            
            return {
                "success": True,
                "base_date": base_dt.isoformat(),
                "added_time": f"{days} jours, {hours} heures, {minutes} minutes",
                "result_date": result_dt.isoformat(),
                "result_formatted": result_dt.strftime("%d/%m/%Y à %H:%M:%S")
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de l'ajout de temps: {str(e)}"}

    def _calculate_age(self, birth_date: str) -> Dict[str, Any]:
        """Calcule l'âge"""
        try:
            birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            
            age_years = today.year - birth_dt.year
            age_months = today.month - birth_dt.month
            age_days = today.day - birth_dt.day
            
            if age_days < 0:
                age_months -= 1
                age_days += calendar.monthrange(today.year, today.month - 1)[1]
            
            if age_months < 0:
                age_years -= 1
                age_months += 12
            
            total_days = (today - birth_dt).days
            
            return {
                "success": True,
                "birth_date": birth_date,
                "current_date": today.strftime("%Y-%m-%d"),
                "age_years": age_years,
                "age_months": age_months,
                "age_days": age_days,
                "total_days": total_days,
                "formatted": f"{age_years} ans, {age_months} mois et {age_days} jours"
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors du calcul d'âge: {str(e)}"}

    def _get_calendar(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Affiche le calendrier"""
        try:
            now = datetime.now()
            if year is None:
                year = now.year
            if month is None:
                month = now.month
            
            cal = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]
            
            # Créer un calendrier formaté
            calendar_lines = []
            calendar_lines.append(f"{month_name} {year}")
            calendar_lines.append("Lu Ma Me Je Ve Sa Di")
            
            for week in cal:
                week_str = ""
                for day in week:
                    if day == 0:
                        week_str += "   "
                    else:
                        week_str += f"{day:2d} "
                calendar_lines.append(week_str.rstrip())
            
            return {
                "success": True,
                "year": year,
                "month": month,
                "month_name": month_name,
                "calendar": calendar_lines,
                "days_in_month": calendar.monthrange(year, month)[1],
                "first_weekday": calendar.monthrange(year, month)[0]
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la génération du calendrier: {str(e)}"}
