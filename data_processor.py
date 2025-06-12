# data_processor.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import streamlit as st
import os

class DataProcessor:
    """Handles loading and processing of food database"""
    
    def __init__(self):
        self.required_columns = [
            'Food code', 'Main food description', 'Energy (kcal)', 
            'Protein (g)', 'Carbohydrate (g)', 'Total Fat (g)'
        ]
    
    @st.cache_data
    def load_food_database(_self, csv_path: str = 'D:/SJRI/Nutrient_Values.csv') -> pd.DataFrame:
        """
        Load the USDA food database from CSV
        
        Args:
            csv_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded food database
        """
        try:
            # If no path provided, look for common file names
            if csv_path is None:
                possible_paths = [
                    'usda_food_data.csv',
                    'food_database.csv',
                    'data/usda_food_data.csv',
                    'data/food_database.csv'
                ]
                
                csv_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        csv_path = path
                        break
                
                # If no file found, create sample data for demo
                if csv_path is None:
                    return _self._create_sample_data()
            
            # Load the CSV file
            df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
            
            # Validate required columns
            missing_cols = [col for col in _self.required_columns if col not in df.columns]
            if missing_cols:
                st.warning(f"Missing columns in dataset: {missing_cols}")
                return _self._create_sample_data()
            
            # Clean and prepare data
            df = _self._clean_data(df)
            
            st.success(f"✅ Loaded {len(df)} food items from database")
            return df
            
        except FileNotFoundError:
            st.error(f"Food database file not found: {csv_path}")
            return _self._create_sample_data()
        except Exception as e:
            st.error(f"Error loading food database: {str(e)}")
            return _self._create_sample_data()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare the food database
        
        Args:
            df (pd.DataFrame): Raw food database
            
        Returns:
            pd.DataFrame: Cleaned food database
        """
        try:
            # Convert numeric columns
            numeric_columns = [
                'Energy (kcal)', 'Protein (g)', 'Carbohydrate (g)', 'Total Fat (g)',
                'Fiber, total dietary (g)', 'Sugars, total (g)', 'Sodium (mg)',
                'Calcium (mg)', 'Iron (mg)', 'Vitamin C (mg)'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Clean food descriptions
            df['Main food description'] = df['Main food description'].astype(str).str.strip()
            
            # Remove rows with missing essential data
            df = df.dropna(subset=['Main food description'])
            df = df[df['Main food description'] != '']
            
            # Ensure Food code is string
            df['Food code'] = df['Food code'].astype(str)
            
            return df
            
        except Exception as e:
            st.error(f"Error cleaning data: {str(e)}")
            return df
    
    def _create_sample_data(self) -> pd.DataFrame:
        """
        Create sample food data for demonstration
        
        Returns:
            pd.DataFrame: Sample food database
        """
        sample_data = {
            'Food code': ['11100000', '11111000', '21201000', '23101000', '13101000', 
                         '15121000', '18601000', '19101000', '63101000', '74101000'],
            'Main food description': [
                'Milk, reduced fat', 'Milk, whole', 'Apple, raw', 'Chicken breast, cooked',
                'Egg, whole, cooked', 'Salmon, cooked', 'White bread', 'Rice, cooked',
                'Broccoli, cooked', 'Banana, raw'
            ],
            'Energy (kcal)': [52, 61, 52, 165, 155, 208, 265, 130, 34, 89],
            'Protein (g)': [3.33, 3.27, 0.26, 31.02, 13.0, 25.4, 9.0, 2.7, 2.8, 1.1],
            'Carbohydrate (g)': [4.83, 4.63, 13.81, 0, 1.1, 0, 49.0, 28.2, 7.0, 22.8],
            'Total Fat (g)': [2.14, 3.2, 0.17, 3.57, 10.6, 12.4, 3.2, 0.3, 0.4, 0.3],
            'Fiber, total dietary (g)': [0, 0, 2.4, 0, 0, 0, 2.7, 0.4, 5.1, 2.6],
            'Sugars, total (g)': [4.88, 4.81, 10.39, 0, 0.6, 0, 5.0, 0.1, 1.5, 12.2],
            'Sodium (mg)': [39, 38, 1, 74, 124, 59, 681, 1, 41, 1],
            'Calcium (mg)': [125, 123, 6, 15, 50, 12, 151, 10, 47, 5],
            'Iron (mg)': [0, 0, 0.12, 1.04, 1.8, 0.8, 3.6, 0.8, 0.7, 0.3],
            'Vitamin C (mg)': [0.1, 0, 4.6, 0, 0, 0, 0, 0, 89.2, 8.7]
        }
        
        df = pd.DataFrame(sample_data)
        st.info("📝 Using sample food database. Upload your USDA CSV file for full functionality.")
        return df
    
    def search_foods(self, df: pd.DataFrame, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for foods in the database
        
        Args:
            df (pd.DataFrame): Food database
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: List of matching food items
        """
        try:
            if not query or len(query) < 2:
                return []
            
            # Case-insensitive search
            query = query.lower().strip()
            
            # Search in food descriptions
            mask = df['Main food description'].str.lower().str.contains(
                query, na=False, regex=False
            )
            
            results = df[mask].head(limit)
            
            # Convert to list of dictionaries
            return results.to_dict('records')
            
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return []
    
    def get_food_by_code(self, df: pd.DataFrame, food_code: str) -> Optional[Dict]:
        """
        Get a specific food item by its code
        
        Args:
            df (pd.DataFrame): Food database
            food_code (str): Food code to search for
            
        Returns:
            Optional[Dict]: Food item if found, None otherwise
        """
        try:
            result = df[df['Food code'] == str(food_code)]
            if not result.empty:
                return result.iloc[0].to_dict()
            return None
            
        except Exception as e:
            st.error(f"Error getting food by code: {str(e)}")
            return None
    
    def get_foods_rich_in_nutrient(self, df: pd.DataFrame, nutrient: str, 
                                 limit: int = 10) -> List[Dict]:
        """
        Get foods that are rich in a specific nutrient
        
        Args:
            df (pd.DataFrame): Food database
            nutrient (str): Nutrient column name
            limit (int): Number of foods to return
            
        Returns:
            List[Dict]: Foods rich in the nutrient
        """
        try:
            if nutrient not in df.columns:
                return []
            
            # Sort by nutrient content and get top foods
            sorted_df = df.nlargest(limit, nutrient)
            
            # Filter out foods with zero content
            sorted_df = sorted_df[sorted_df[nutrient] > 0]
            
            results = []
            for _, row in sorted_df.iterrows():
                results.append({
                    'name': row['Main food description'],
                    'food_code': row['Food code'],
                    'nutrient_value': row[nutrient],
                    'unit': self._get_nutrient_unit(nutrient)
                })
            
            return results
            
        except Exception as e:
            st.error(f"Error finding foods rich in {nutrient}: {str(e)}")
            return []
    
    def _get_nutrient_unit(self, nutrient: str) -> str:
        """
        Get the unit for a nutrient
        
        Args:
            nutrient (str): Nutrient name
            
        Returns:
            str: Unit for the nutrient
        """
        if '(g)' in nutrient:
            return 'g'
        elif '(mg)' in nutrient:
            return 'mg'
        elif '(mcg)' in nutrient:
            return 'mcg'
        elif '(kcal)' in nutrient:
            return 'kcal'
        else:
            return ''
    
    def get_nutrient_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get statistics about nutrients in the database
        
        Args:
            df (pd.DataFrame): Food database
            
        Returns:
            Dict: Nutrient statistics
        """
        try:
            stats = {}
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if any(nutrient in col for nutrient in ['Energy', 'Protein', 'Fat', 'Carbohydrate']):
                    stats[col] = {
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'std': df[col].std(),
                        'min': df[col].min(),
                        'max': df[col].max()
                    }
            
            return stats
            
        except Exception as e:
            st.error(f"Error calculating nutrient statistics: {str(e)}")
            return {}
