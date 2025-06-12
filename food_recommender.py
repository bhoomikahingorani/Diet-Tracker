# food_recommender.py
import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import random

class FoodRecommender:
    """Provides food recommendations based on nutritional needs"""
    
    def __init__(self):
        # Nutrient-to-column mapping
        self.nutrient_columns = {
            'protein': 'Protein (g)',
            'fiber': 'Fiber, total dietary (g)',
            'calcium': 'Calcium (mg)',
            'iron': 'Iron (mg)',
            'vitamin_c': 'Vitamin C (mg)',
            'fat': 'Total Fat (g)',
            'carbs': 'Carbohydrate (g)'
        }
        
        # Food pairing knowledge base
        self.food_pairings = {
            'iron': {
                'enhancers': ['vitamin_c'],
                'inhibitors': ['calcium'],
                'pairing_foods': ['citrus fruits', 'bell peppers', 'strawberries', 'tomatoes']
            },
            'calcium': {
                'enhancers': ['vitamin_d'],
                'inhibitors': ['fiber'],
                'pairing_foods': ['fatty fish', 'egg yolks', 'fortified foods']
            },
            'protein': {
                'enhancers': ['vitamin_c'],
                'pairing_foods': ['beans with rice', 'hummus with whole grain', 'nuts with fruits']
            }
        }
    
    def get_recommendations(self, deficiencies: Dict[str, Any], 
                          food_data: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Get food recommendations based on nutrient deficiencies
        
        Args:
            deficiencies (Dict[str, Any]): Nutrient deficiencies from analysis
            food_data (pd.DataFrame): Food database
            
        Returns:
            Dict[str, List[Dict]]: Recommended foods for each deficient nutrient
        """
        try:
            recommendations = {}
            
            for nutrient, info in deficiencies.items():
                if nutrient in self.nutrient_columns:
                    column_name = self.nutrient_columns[nutrient]
                    
                    if column_name in food_data.columns:
                        # Get foods rich in this nutrient
                        rich_foods = self._get_foods_rich_in_nutrient(
                            food_data, column_name, limit=10
                        )
                        
                        if rich_foods:
                            recommendations[nutrient] = rich_foods
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error getting food recommendations: {str(e)}")
            return {}
    
    def _get_foods_rich_in_nutrient(self, df: pd.DataFrame, nutrient_column: str, 
                                   limit: int = 10) -> List[Dict]:
        """
        Get foods that are rich in a specific nutrient
        
        Args:
            df (pd.DataFrame): Food database
            nutrient_column (str): Column name for the nutrient
            limit (int): Number of foods to return
            
        Returns:
            List[Dict]: Foods rich in the nutrient
        """
        try:
            # Filter out foods with zero or very low nutrient content
            filtered_df = df[df[nutrient_column] > 0].copy()
            
            if filtered_df.empty:
                return []
            
            # Sort by nutrient content
            sorted_df = filtered_df.nlargest(limit * 2, nutrient_column)
            
            # Remove duplicate similar foods (basic deduplication)
            unique_foods = self._deduplicate_foods(sorted_df, limit)
            
            results = []
            for _, row in unique_foods.iterrows():
                results.append({
                    'name': row['Main food description'],
                    'food_code': row['Food code'],
                    'nutrient_value': row[nutrient_column],
                    'unit': self._get_nutrient_unit(nutrient_column),
                    'calories_per_100g': row.get('Energy (kcal)', 0)
                })
            
            return results[:limit]
            
        except Exception as e:
            st.error(f"Error finding foods rich in {nutrient_column}: {str(e)}")
            return []
    
    def _deduplicate_foods(self, df: pd.DataFrame, limit: int) -> pd.DataFrame:
        """
        Remove similar foods to provide variety in recommendations
        
        Args:
            df (pd.DataFrame): Sorted food dataframe
            limit (int): Target number of unique foods
            
        Returns:
            pd.DataFrame: Deduplicated foods
        """
        try:
            seen_keywords = set()
            unique_foods = []
            
            for _, row in df.iterrows():
                food_name = row['Main food description'].lower()
                
                # Extract key words from food name
                words = food_name.split()
                main_keywords = [word for word in words if len(word) > 3]
                
                # Check if this food is too similar to already selected ones
                is_similar = any(keyword in seen_keywords for keyword in main_keywords[:2])
                
                if not is_similar or len(unique_foods) < limit // 2:
                    unique_foods.append(row)
                    seen_keywords.update(main_keywords[:2])
                
                if len(unique_foods) >= limit:
                    break
            
            return pd.DataFrame(unique_foods)
            
        except Exception as e:
            return df.head(limit)
    
    def _get_nutrient_unit(self, column_name: str) -> str:
        """Get unit for nutrient column"""
        if '(g)' in column_name:
            return 'g'
        elif '(mg)' in column_name:
            return 'mg'
        elif '(mcg)' in column_name:
            return 'mcg'
        else:
            return ''
    
    def get_ai_suggestions(self, daily_log: List[Dict], totals: Dict[str, float]) -> List[Dict]:
        """
        Generate AI-powered food pairing and nutrition suggestions
        
        Args:
            daily_log (List[Dict]): Current day's food log
            totals (Dict[str, float]): Current nutritional totals
            
        Returns:
            List[Dict]: AI suggestions with titles, descriptions, and reasons
        """
        try:
            suggestions = []
            
            # Analyze current foods for pairing opportunities
            current_foods = [entry['name'].lower() for entry in daily_log]
            
            # Iron absorption enhancement
            if any('iron' in food or 'meat' in food or 'spinach' in food for food in current_foods):
                if not any('citrus' in food or 'orange' in food or 'lemon' in food for food in current_foods):
                    suggestions.append({
                        'title': '🍊 Boost Iron Absorption',
                        'description': 'Add citrus fruits or bell peppers to your next meal',
                        'reason': 'Vitamin C enhances iron absorption from plant-based sources by up to 300%'
                    })
            
            # Protein completeness
            if any('beans' in food or 'lentil' in food for food in current_foods):
                if not any('rice' in food or 'grain' in food for food in current_foods):
                    suggestions.append({
                        'title': '🌾 Complete Your Protein',
                        'description': 'Pair your legumes with whole grains like brown rice or quinoa',
                        'reason': 'This combination provides all essential amino acids for complete protein'
                    })
            
            # Calcium and Vitamin D
            if totals.get('calcium', 0) > 300:  # If having calcium-rich foods
                suggestions.append({
                    'title': '☀️ Maximize Calcium Absorption',
                    'description': 'Consider adding fatty fish or spending time in sunlight',
                    'reason': 'Vitamin D is essential for calcium absorption and bone health'
                })
            
            # Antioxidant synergy
            if any('tomato' in food for food in current_foods):
                suggestions.append({
                    'title': '🥑 Enhance Antioxidant Power',
                    'description': 'Add healthy fats like avocado or olive oil',
                    'reason': 'Fats help absorb lycopene and other fat-soluble antioxidants from tomatoes'
                })
            
            # Fiber and hydration
            if totals.get('fiber', 0) > 15:
                suggestions.append({
                    'title': '💧 Stay Hydrated',
                    'description': 'Increase water intake with your high-fiber foods',
                    'reason': 'Adequate hydration prevents digestive discomfort from fiber-rich foods'
                })
            
            # Meal timing suggestions
            suggestions.extend(self._get_meal_timing_suggestions(daily_log))
            
            # Macronutrient balance suggestions
            suggestions.extend(self._get_balance_suggestions(totals))
            
            return suggestions[:6]  # Limit to 6 suggestions
            
        except Exception as e:
            st.error(f"Error generating AI suggestions: {str(e)}")
            return []
    
    def _get_meal_timing_suggestions(self, daily_log: List[Dict]) -> List[Dict]:
        """Generate meal timing suggestions"""
        suggestions = []
        
        try:
            if not daily_log:
                return suggestions
            
            # Check if protein is distributed throughout the day
            morning_protein = sum(entry.get('protein', 0) for entry in daily_log 
                                if 'timestamp' in entry and entry['timestamp'].hour < 12)
            
            if morning_protein < 20:
                suggestions.append({
                    'title': '🌅 Morning Protein Boost',
                    'description': 'Add protein-rich foods to your breakfast',
                    'reason': 'Morning protein helps maintain muscle mass and keeps you satisfied longer'
                })
            
            return suggestions
            
        except Exception as e:
            return suggestions
    
    def _get_balance_suggestions(self, totals: Dict[str, float]) -> List[Dict]:
        """Generate macronutrient balance suggestions"""
        suggestions = []
        
        try:
            total_calories = totals.get('calories', 0)
            if total_calories == 0:
                return suggestions
            
            # Calculate macro percentages
            protein_pct = (totals.get('protein', 0) * 4 / total_calories) * 100
            carb_pct = (totals.get('carbs', 0) * 4 / total_calories) * 100
            fat_pct = (totals.get('fat', 0) * 9 / total_calories) * 100
            
            # Check for imbalances
            if protein_pct < 15:
                suggestions.append({
                    'title': '💪 Increase Protein Intake',
                    'description': 'Aim for 15-25% of calories from protein',
                    'reason': 'Adequate protein supports muscle maintenance and satiety'
                })
            
            if carb_pct < 45:
                suggestions.append({
                    'title': '🌾 Add Healthy Carbs',
                    'description': 'Include whole grains, fruits, and vegetables',
                    'reason': 'Carbohydrates are your body\'s preferred energy source'
                })
            
            if fat_pct < 20:
                suggestions.append({
                    'title': '🥑 Include Healthy Fats',
                    'description': 'Add nuts, seeds, olive oil, or fatty fish',
                    'reason': 'Healthy fats support hormone production and nutrient absorption'
                })
            
            return suggestions
            
        except Exception as e:
            return suggestions
    
    def get_recipe_suggestions(self, deficiencies: Dict[str, Any]) -> List[Dict]:
        """
        Suggest simple recipes based on nutrient deficiencies
        
        Args:
            deficiencies (Dict[str, Any]): Nutrient deficiencies
            
        Returns:
            List[Dict]: Recipe suggestions
        """
        try:
            recipes = []
            
            if 'iron' in deficiencies and 'vitamin_c' in deficiencies:
                recipes.append({
                    'name': 'Spinach and Strawberry Salad',
                    'ingredients': ['Fresh spinach', 'Strawberries', 'Walnuts', 'Balsamic vinaigrette'],
                    'benefits': 'High in iron (spinach) with vitamin C (strawberries) for better absorption'
                })
            
            if 'protein' in deficiencies:
                recipes.append({
                    'name': 'Quinoa Power Bowl',
                    'ingredients': ['Quinoa', 'Black beans', 'Avocado', 'Cherry tomatoes', 'Lime'],
                    'benefits': 'Complete protein from quinoa and beans combination'
                })
            
            if 'calcium' in deficiencies:
                recipes.append({
                    'name': 'Greek Yogurt Parfait',
                    'ingredients': ['Greek yogurt', 'Almonds', 'Chia seeds', 'Berries'],
                    'benefits': 'Multiple calcium sources plus vitamin D for absorption'
                })
            
            if 'fiber' in deficiencies:
                recipes.append({
                    'name': 'Three-Bean Chili',
                    'ingredients': ['Mixed beans', 'Vegetables', 'Tomatoes', 'Spices'],
                    'benefits': 'High fiber content supports digestive health'
                })
            
            return recipes[:3]  # Return top 3 recipes
            
        except Exception as e:
            st.error(f"Error generating recipe suggestions: {str(e)}")
            return []
    
    def get_supplement_recommendations(self, deficiencies: Dict[str, Any]) -> List[Dict]:
        """
        Suggest supplements for severe deficiencies (educational purposes only)
        
        Args:
            deficiencies (Dict[str, Any]): Nutrient deficiencies
            
        Returns:
            List[Dict]: Supplement information
        """
        try:
            supplements = []
            
            for nutrient, info in deficiencies.items():
                if info['percentage'] < 50:  # Severe deficiency
                    supplement_info = self._get_supplement_info(nutrient)
                    if supplement_info:
                        supplements.append(supplement_info)
            
            return supplements
            
        except Exception as e:
            st.error(f"Error generating supplement recommendations: {str(e)}")
            return []
    
    def _get_supplement_info(self, nutrient: str) -> Dict:
        """Get supplement information for a nutrient"""
        supplement_map = {
            'vitamin_c': {
                'name': 'Vitamin C',
                'note': 'Consider citrus fruits or supplements if dietary intake is insufficient',
                'warning': 'Consult healthcare provider before taking supplements'
            },
            'iron': {
                'name': 'Iron',
                'note': 'Iron supplements may be needed for severe deficiency',
                'warning': 'Iron supplements can cause side effects - consult a doctor'
            },
            'calcium': {
                'name': 'Calcium',
                'note': 'Calcium supplements with Vitamin D for better absorption',
                'warning': 'Balance with magnesium and don\'t exceed recommended doses'
            }
        }
        
        return supplement_map.get(nutrient)
