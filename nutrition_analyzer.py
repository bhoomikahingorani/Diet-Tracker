# nutrition_analyzer.py
import streamlit as st
from typing import Dict, List, Any
import numpy as np

class NutritionAnalyzer:
    """Analyzes nutritional data and provides recommendations"""
    
    def __init__(self):
        # Daily recommended values (can be customized)
        self.daily_targets = {
            'calories': 2000,  # kcal
            'protein': 150,    # grams
            'carbs': 250,      # grams
            'fat': 65,         # grams
            'fiber': 25,       # grams
            'sugar': 50,       # grams (max recommended)
            'sodium': 2300,    # mg (max recommended)
            'calcium': 1000,   # mg
            'iron': 18,        # mg
            'vitamin_c': 90    # mg
        }
        
        # Nutrient ranges (min, max as percentage of target)
        self.acceptable_ranges = {
            'calories': (0.8, 1.2),    # 80-120% of target
            'protein': (0.8, 2.0),     # 80-200% of target
            'carbs': (0.45, 1.3),      # 45-130% of target
            'fat': (0.7, 1.5),         # 70-150% of target
            'fiber': (0.8, float('inf')),  # At least 80%
            'sodium': (0, 1.0),        # Max 100% of target
            'calcium': (0.8, float('inf')), # At least 80%
            'iron': (0.8, float('inf')),    # At least 80%
            'vitamin_c': (0.8, float('inf')) # At least 80%
        }
    
    def calculate_totals(self, daily_log: List[Dict]) -> Dict[str, float]:
        """
        Calculate total nutritional values from daily log
        
        Args:
            daily_log (List[Dict]): List of logged food items
            
        Returns:
            Dict[str, float]: Total nutritional values
        """
        try:
            totals = {
                'calories': 0.0,
                'protein': 0.0,
                'carbs': 0.0,
                'fat': 0.0,
                'fiber': 0.0,
                'sugar': 0.0,
                'sodium': 0.0,
                'calcium': 0.0,
                'iron': 0.0,
                'vitamin_c': 0.0
            }
            
            for entry in daily_log:
                for nutrient in totals.keys():
                    totals[nutrient] += entry.get(nutrient, 0.0)
            
            return totals
            
        except Exception as e:
            st.error(f"Error calculating nutritional totals: {str(e)}")
            return {key: 0.0 for key in totals.keys()}
    
    def analyze_nutrition(self, totals: Dict[str, float], 
                         custom_targets: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Analyze nutritional intake against targets
        
        Args:
            totals (Dict[str, float]): Current nutritional totals
            custom_targets (Dict[str, float]): Custom daily targets
            
        Returns:
            Dict[str, Any]: Analysis results including deficiencies and excesses
        """
        try:
            targets = custom_targets if custom_targets else self.daily_targets
            
            analysis = {
                'deficiencies': {},
                'excesses': {},
                'within_range': {},
                'overall_score': 0.0
            }
            
            scores = []
            
            for nutrient, current_value in totals.items():
                if nutrient not in targets:
                    continue
                
                target_value = targets[nutrient]
                if target_value == 0:
                    continue
                
                percentage = (current_value / target_value) * 100
                acceptable_range = self.acceptable_ranges.get(nutrient, (0.8, 1.2))
                
                min_acceptable = acceptable_range[0] * 100
                max_acceptable = acceptable_range[1] * 100 if acceptable_range[1] != float('inf') else float('inf')
                
                nutrient_info = {
                    'current': current_value,
                    'target': target_value,
                    'percentage': percentage,
                    'unit': self._get_nutrient_unit(nutrient)
                }
                
                if percentage < min_acceptable:
                    analysis['deficiencies'][nutrient] = nutrient_info
                    scores.append(percentage / 100)
                elif max_acceptable != float('inf') and percentage > max_acceptable:
                    analysis['excesses'][nutrient] = nutrient_info
                    scores.append(min(1.0, max_acceptable / percentage))
                else:
                    analysis['within_range'][nutrient] = nutrient_info
                    scores.append(1.0)
            
            # Calculate overall nutrition score (0-100)
            if scores:
                analysis['overall_score'] = (sum(scores) / len(scores)) * 100
            
            return analysis
            
        except Exception as e:
            st.error(f"Error analyzing nutrition: {str(e)}")
            return {'deficiencies': {}, 'excesses': {}, 'within_range': {}, 'overall_score': 0.0}
    
    def _get_nutrient_unit(self, nutrient: str) -> str:
        """
        Get the unit for a nutrient
        
        Args:
            nutrient (str): Nutrient name
            
        Returns:
            str: Unit for the nutrient
        """
        unit_map = {
            'calories': 'kcal',
            'protein': 'g',
            'carbs': 'g',
            'fat': 'g',
            'fiber': 'g',
            'sugar': 'g',
            'sodium': 'mg',
            'calcium': 'mg',
            'iron': 'mg',
            'vitamin_c': 'mg'
        }
        return unit_map.get(nutrient, '')
    
    def get_nutrition_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate text recommendations based on nutrition analysis
        
        Args:
            analysis (Dict[str, Any]): Nutrition analysis results
            
        Returns:
            List[str]: List of recommendations
        """
        try:
            recommendations = []
            
            # Overall score feedback
            score = analysis['overall_score']
            if score >= 90:
                recommendations.append("🎉 Excellent! Your nutrition is well-balanced.")
            elif score >= 75:
                recommendations.append("👍 Good nutrition overall, with room for minor improvements.")
            elif score >= 60:
                recommendations.append("⚠️ Your nutrition needs some attention in key areas.")
            else:
                recommendations.append("🚨 Your nutrition needs significant improvement.")
            
            # Specific deficiency recommendations
            deficiencies = analysis.get('deficiencies', {})
            
            if 'protein' in deficiencies:
                recommendations.append(
                    "💪 Increase protein intake with lean meats, fish, eggs, legumes, or dairy products."
                )
            
            if 'fiber' in deficiencies:
                recommendations.append(
                    "🌾 Add more fiber with whole grains, fruits, vegetables, and legumes."
                )
            
            if 'calcium' in deficiencies:
                recommendations.append(
                    "🦴 Boost calcium with dairy products, leafy greens, or fortified foods."
                )
            
            if 'iron' in deficiencies:
                recommendations.append(
                    "🩸 Increase iron with red meat, spinach, lentils, or fortified cereals."
                )
            
            if 'vitamin_c' in deficiencies:
                recommendations.append(
                    "🍊 Add vitamin C with citrus fruits, berries, bell peppers, or broccoli."
                )
            
            # Excess warnings
            excesses = analysis.get('excesses', {})
            
            if 'sodium' in excesses:
                recommendations.append(
                    "🧂 Reduce sodium intake by limiting processed foods and restaurant meals."
                )
            
            if 'sugar' in excesses:
                recommendations.append(
                    "🍭 Cut back on added sugars from sweets, sodas, and processed foods."
                )
            
            if 'calories' in excesses:
                recommendations.append(
                    "⚖️ Consider reducing portion sizes or choosing lower-calorie alternatives."
                )
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return ["Unable to generate recommendations at this time."]
    
    def calculate_macro_percentages(self, totals: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate macronutrient percentages of total calories
        
        Args:
            totals (Dict[str, float]): Nutritional totals
            
        Returns:
            Dict[str, float]: Macronutrient percentages
        """
        try:
            total_calories = totals.get('calories', 0)
            if total_calories == 0:
                return {'protein': 0, 'carbs': 0, 'fat': 0}
            
            # Convert grams to calories (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
            protein_calories = totals.get('protein', 0) * 4
            carb_calories = totals.get('carbs', 0) * 4
            fat_calories = totals.get('fat', 0) * 9
            
            return {
                'protein': (protein_calories / total_calories) * 100,
                'carbs': (carb_calories / total_calories) * 100,
                'fat': (fat_calories / total_calories) * 100
            }
            
        except Exception as e:
            st.error(f"Error calculating macro percentages: {str(e)}")
            return {'protein': 0, 'carbs': 0, 'fat': 0}
    
    def get_nutrient_goals_progress(self, totals: Dict[str, float], 
                                  custom_targets: Dict[str, float] = None) -> Dict[str, Dict]:
        """
        Calculate progress towards daily nutrient goals
        
        Args:
            totals (Dict[str, float]): Current nutritional totals
            custom_targets (Dict[str, float]): Custom daily targets
            
        Returns:
            Dict[str, Dict]: Progress information for each nutrient
        """
        try:
            targets = custom_targets if custom_targets else self.daily_targets
            progress = {}
            
            for nutrient, current_value in totals.items():
                if nutrient in targets:
                    target_value = targets[nutrient]
                    percentage = min((current_value / target_value) * 100, 100) if target_value > 0 else 0
                    
                    progress[nutrient] = {
                        'current': current_value,
                        'target': target_value,
                        'percentage': percentage,
                        'remaining': max(0, target_value - current_value),
                        'unit': self._get_nutrient_unit(nutrient),
                        'status': self._get_goal_status(percentage, nutrient)
                    }
            
            return progress
            
        except Exception as e:
            st.error(f"Error calculating goal progress: {str(e)}")
            return {}
    
    def _get_goal_status(self, percentage: float, nutrient: str) -> str:
        """
        Get status label for nutrient goal progress
        
        Args:
            percentage (float): Percentage of goal achieved
            nutrient (str): Nutrient name
            
        Returns:
            str: Status label
        """
        if nutrient in ['sodium', 'sugar']:  # For nutrients we want to limit
            if percentage <= 50:
                return "excellent"
            elif percentage <= 75:
                return "good"
            elif percentage <= 100:
                return "caution"
            else:
                return "exceeded"
        else:  # For nutrients we want to meet/exceed
            if percentage >= 100:
                return "achieved"
            elif percentage >= 80:
                return "close"
            elif percentage >= 50:
                return "moderate"
            else:
                return "low"
    
    def get_meal_timing_analysis(self, daily_log: List[Dict]) -> Dict[str, Any]:
        """
        Analyze meal timing and distribution
        
        Args:
            daily_log (List[Dict]): List of logged food items with timestamps
            
        Returns:
            Dict[str, Any]: Meal timing analysis
        """
        try:
            if not daily_log:
                return {}
            
            # Group foods by time periods
            meals = {
                'breakfast': [],  # 5 AM - 11 AM
                'lunch': [],      # 11 AM - 3 PM
                'dinner': [],     # 5 PM - 9 PM
                'snacks': []      # Other times
            }
            
            for entry in daily_log:
                hour = entry.get('timestamp').hour if 'timestamp' in entry else 12
                
                if 5 <= hour < 11:
                    meals['breakfast'].append(entry)
                elif 11 <= hour < 15:
                    meals['lunch'].append(entry)
                elif 17 <= hour < 21:
                    meals['dinner'].append(entry)
                else:
                    meals['snacks'].append(entry)
            
            # Calculate calories per meal
            meal_calories = {}
            for meal_name, items in meals.items():
                meal_calories[meal_name] = sum(item.get('calories', 0) for item in items)
            
            total_calories = sum(meal_calories.values())
            
            # Calculate meal distribution percentages
            meal_percentages = {}
            for meal_name, calories in meal_calories.items():
                meal_percentages[meal_name] = (calories / total_calories * 100) if total_calories > 0 else 0
            
            return {
                'meal_calories': meal_calories,
                'meal_percentages': meal_percentages,
                'total_calories': total_calories,
                'meal_count': len([m for m in meals.values() if m])
            }
            
        except Exception as e:
            st.error(f"Error analyzing meal timing: {str(e)}")
            return {}
