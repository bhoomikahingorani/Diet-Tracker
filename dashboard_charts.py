# dashboard_charts.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from typing import Dict, List, Optional, Tuple
import seaborn as sns
import matplotlib.pyplot as plt

class DashboardCharts:
    """Handles all chart visualizations for the nutrition dashboard"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9f00',
            'info': '#17a2b8',
            'nutrients': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        }
    
    def create_macronutrient_pie_chart(self, food_data: Dict, title: str = "Macronutrient Distribution") -> go.Figure:
        """
        Create a pie chart showing macronutrient distribution for a food item
        
        Args:
            food_data (Dict): Food item data
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly pie chart
        """
        try:
            # Calculate calories from macronutrients
            protein_cals = food_data.get('Protein (g)', 0) * 4
            carb_cals = food_data.get('Carbohydrate (g)', 0) * 4
            fat_cals = food_data.get('Total Fat (g)', 0) * 9
            
            # Handle case where all values are zero
            total_cals = protein_cals + carb_cals + fat_cals
            if total_cals == 0:
                return self._create_empty_chart("No macronutrient data available")
            
            labels = ['Protein', 'Carbohydrates', 'Fat']
            values = [protein_cals, carb_cals, fat_cals]
            colors = [self.color_palette['danger'], self.color_palette['warning'], self.color_palette['success']]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>%{value:.1f} kcal<br>%{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                showlegend=True,
                height=400,
                margin=dict(t=50, b=20, l=20, r=20)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating pie chart: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def create_nutrient_comparison_bar(self, foods: List[Dict], nutrients: List[str], 
                                     title: str = "Nutrient Comparison") -> go.Figure:
        """
        Create a grouped bar chart comparing nutrients across multiple foods
        
        Args:
            foods (List[Dict]): List of food items
            nutrients (List[str]): List of nutrients to compare
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly bar chart
        """
        try:
            if not foods or not nutrients:
                return self._create_empty_chart("No data available for comparison")
            
            fig = go.Figure()
            
            # Create bars for each nutrient
            for i, nutrient in enumerate(nutrients):
                food_names = [food.get('Main food description', 'Unknown')[:30] + '...' 
                             if len(food.get('Main food description', '')) > 30 
                             else food.get('Main food description', 'Unknown') for food in foods]
                
                values = [food.get(nutrient, 0) for food in foods]
                
                fig.add_trace(go.Bar(
                    name=nutrient.replace(' (g)', '').replace(' (mg)', '').replace(' (kcal)', ''),
                    x=food_names,
                    y=values,
                    marker_color=self.color_palette['nutrients'][i % len(self.color_palette['nutrients'])],
                    hovertemplate=f'<b>%{{x}}</b><br>{nutrient}: %{{y}}<extra></extra>'
                ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                xaxis_title="Foods",
                yaxis_title="Amount",
                barmode='group',
                height=500,
                xaxis=dict(tickangle=45),
                margin=dict(t=50, b=100, l=50, r=20),
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating bar chart: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def create_nutrient_density_scatter(self, df: pd.DataFrame, x_nutrient: str, 
                                      y_nutrient: str, size_nutrient: str = None,
                                      title: str = "Nutrient Density Analysis") -> go.Figure:
        """
        Create a scatter plot showing relationship between nutrients
        
        Args:
            df (pd.DataFrame): Food database
            x_nutrient (str): X-axis nutrient
            y_nutrient (str): Y-axis nutrient
            size_nutrient (str): Nutrient for bubble size (optional)
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly scatter plot
        """
        try:
            if x_nutrient not in df.columns or y_nutrient not in df.columns:
                return self._create_empty_chart("Selected nutrients not found in database")
            
            # Filter out zero values for better visualization
            filtered_df = df[(df[x_nutrient] > 0) & (df[y_nutrient] > 0)].copy()
            
            if filtered_df.empty:
                return self._create_empty_chart("No data points with non-zero values")
            
            # Limit to top 200 foods for performance
            filtered_df = filtered_df.head(200)
            
            hover_text = []
            for _, row in filtered_df.iterrows():
                text = f"<b>{row['Main food description'][:40]}</b><br>"
                text += f"{x_nutrient}: {row[x_nutrient]:.2f}<br>"
                text += f"{y_nutrient}: {row[y_nutrient]:.2f}"
                if size_nutrient and size_nutrient in df.columns:
                    text += f"<br>{size_nutrient}: {row[size_nutrient]:.2f}"
                hover_text.append(text)
            
            if size_nutrient and size_nutrient in df.columns:
                fig = go.Figure(data=go.Scatter(
                    x=filtered_df[x_nutrient],
                    y=filtered_df[y_nutrient],
                    mode='markers',
                    marker=dict(
                        size=filtered_df[size_nutrient],
                        sizemode='diameter',
                        sizeref=2. * max(filtered_df[size_nutrient]) / (40.**2),
                        sizemin=4,
                        color=filtered_df[size_nutrient],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title=size_nutrient)
                    ),
                    hovertemplate='%{hovertext}<extra></extra>',
                    hovertext=hover_text
                ))
            else:
                fig = go.Figure(data=go.Scatter(
                    x=filtered_df[x_nutrient],
                    y=filtered_df[y_nutrient],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=self.color_palette['primary'],
                        opacity=0.7
                    ),
                    hovertemplate='%{hovertext}<extra></extra>',
                    hovertext=hover_text
                ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                xaxis_title=x_nutrient,
                yaxis_title=y_nutrient,
                height=500,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating scatter plot: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def create_top_foods_chart(self, df: pd.DataFrame, nutrient: str, top_n: int = 10,
                              title: str = None) -> go.Figure:
        """
        Create a horizontal bar chart of top foods for a specific nutrient
        
        Args:
            df (pd.DataFrame): Food database
            nutrient (str): Nutrient to analyze
            top_n (int): Number of top foods to show
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly horizontal bar chart
        """
        try:
            if nutrient not in df.columns:
                return self._create_empty_chart(f"Nutrient '{nutrient}' not found in database")
            
            # Get top foods
            top_foods = df.nlargest(top_n, nutrient)
            top_foods = top_foods[top_foods[nutrient] > 0]  # Remove zero values
            
            if top_foods.empty:
                return self._create_empty_chart(f"No foods found with {nutrient} data")
            
            # Truncate long food names
            food_names = [name[:50] + '...' if len(name) > 50 else name 
                         for name in top_foods['Main food description']]
            
            fig = go.Figure(data=go.Bar(
                y=food_names,
                x=top_foods[nutrient],
                orientation='h',
                marker=dict(
                    color=self.color_palette['primary'],
                    colorscale='Blues',
                    showscale=False
                ),
                hovertemplate='<b>%{y}</b><br>%{x:.2f} ' + self._get_nutrient_unit(nutrient) + '<extra></extra>'
            ))
            
            chart_title = title or f"Top {top_n} Foods - {nutrient}"
            
            fig.update_layout(
                title=dict(text=chart_title, x=0.5, font=dict(size=16)),
                xaxis_title=f"{nutrient}",
                yaxis_title="Foods",
                height=max(400, top_n * 40),
                margin=dict(t=50, b=50, l=200, r=50),
                yaxis=dict(categoryorder='total ascending')
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating top foods chart: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def create_nutrient_distribution_histogram(self, df: pd.DataFrame, nutrient: str,
                                             bins: int = 30, title: str = None) -> go.Figure:
        """
        Create a histogram showing the distribution of a nutrient across all foods
        
        Args:
            df (pd.DataFrame): Food database
            nutrient (str): Nutrient to analyze
            bins (int): Number of histogram bins
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly histogram
        """
        try:
            if nutrient not in df.columns:
                return self._create_empty_chart(f"Nutrient '{nutrient}' not found in database")
            
            # Filter out zero values for better distribution visualization
            data = df[df[nutrient] > 0][nutrient]
            
            if data.empty:
                return self._create_empty_chart(f"No non-zero values found for {nutrient}")
            
            fig = go.Figure(data=go.Histogram(
                x=data,
                nbinsx=bins,
                marker=dict(
                    color=self.color_palette['primary'],
                    opacity=0.7
                ),
                hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
            ))
            
            chart_title = title or f"Distribution of {nutrient}"
            
            fig.update_layout(
                title=dict(text=chart_title, x=0.5, font=dict(size=16)),
                xaxis_title=f"{nutrient}",
                yaxis_title="Number of Foods",
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
                bargap=0.1
            )
            
            # Add statistics annotation
            mean_val = data.mean()
            median_val = data.median()
            
            fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {mean_val:.2f}")
            fig.add_vline(x=median_val, line_dash="dash", line_color="green", 
                         annotation_text=f"Median: {median_val:.2f}")
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating histogram: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def create_correlation_heatmap(self, df: pd.DataFrame, nutrients: List[str] = None,
                                  title: str = "Nutrient Correlation Matrix") -> go.Figure:
        """
        Create a correlation heatmap for nutrients
        
        Args:
            df (pd.DataFrame): Food database
            nutrients (List[str]): List of nutrients to include
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly heatmap
        """
        try:
            if nutrients is None:
                # Default nutrients for correlation
                nutrients = [
                    'Energy (kcal)', 'Protein (g)', 'Carbohydrate (g)', 'Total Fat (g)',
                    'Fiber, total dietary (g)', 'Sugars, total (g)', 'Sodium (mg)',
                    'Calcium (mg)', 'Iron (mg)', 'Vitamin C (mg)'
                ]
            
            # Filter available nutrients
            available_nutrients = [n for n in nutrients if n in df.columns]
            
            if len(available_nutrients) < 2:
                return self._create_empty_chart("Not enough nutrients available for correlation")
            
            # Calculate correlation matrix
            corr_data = df[available_nutrients].corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_data.values,
                x=[n.replace(' (g)', '').replace(' (mg)', '').replace(' (kcal)', '') 
                   for n in corr_data.columns],
                y=[n.replace(' (g)', '').replace(' (mg)', '').replace(' (kcal)', '') 
                   for n in corr_data.index],
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_data.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                height=500,
                margin=dict(t=50, b=50, l=100, r=50),
                xaxis=dict(tickangle=45)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating correlation heatmap: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def create_meal_planning_chart(self, selected_foods: List[Dict], 
                                 daily_targets: Dict = None,
                                 title: str = "Meal Nutrition Summary") -> go.Figure:
        """
        Create a chart showing nutritional totals for selected foods vs daily targets
        
        Args:
            selected_foods (List[Dict]): List of selected food items with portions
            daily_targets (Dict): Daily nutritional targets
            title (str): Chart title
            
        Returns:
            go.Figure: Plotly grouped bar chart
        """
        try:
            if not selected_foods:
                return self._create_empty_chart("No foods selected for meal planning")
            
            # Default daily targets (based on general recommendations)
            if daily_targets is None:
                daily_targets = {
                    'Energy (kcal)': 2000,
                    'Protein (g)': 50,
                    'Carbohydrate (g)': 250,
                    'Total Fat (g)': 65,
                    'Fiber, total dietary (g)': 25,
                    'Sodium (mg)': 2300
                }
            
            # Calculate totals from selected foods
            totals = {}
            for nutrient in daily_targets.keys():
                total = 0
                for food in selected_foods:
                    portion = food.get('portion', 100) / 100  # Convert from grams to ratio
                    total += food.get(nutrient, 0) * portion
                totals[nutrient] = total
            
            nutrients = list(daily_targets.keys())
            current_values = [totals.get(n, 0) for n in nutrients]
            target_values = [daily_targets.get(n, 0) for n in nutrients]
            
            fig = go.Figure()
            
            # Add current values bars
            fig.add_trace(go.Bar(
                name='Current',
                x=nutrients,
                y=current_values,
                marker_color=self.color_palette['primary'],
                hovertemplate='<b>%{x}</b><br>Current: %{y:.1f}<extra></extra>'
            ))
            
            # Add target values bars
            fig.add_trace(go.Bar(
                name='Target',
                x=nutrients,
                y=target_values,
                marker_color=self.color_palette['secondary'],
                opacity=0.7,
                hovertemplate='<b>%{x}</b><br>Target: %{y:.1f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                xaxis_title="Nutrients",
                yaxis_title="Amount",
                barmode='group',
                height=500,
                margin=dict(t=50, b=100, l=50, r=20),
                xaxis=dict(tickangle=45),
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating meal planning chart: {str(e)}")
            return self._create_empty_chart("Error creating chart")
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """
        Create an empty chart with a message
        
        Args:
            message (str): Message to display
            
        Returns:
            go.Figure: Empty chart with message
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(t=50, b=50, l=50, r=50)
        )
        return fig
    
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
    
    def create_dashboard_summary(self, df: pd.DataFrame) -> Dict[str, go.Figure]:
        """
        Create a collection of summary charts for the dashboard
        
        Args:
            df (pd.DataFrame): Food database
            
        Returns:
            Dict[str, go.Figure]: Dictionary of charts
        """
        charts = {}
        
        try:
            # 1. Top 10 highest calorie foods
            charts['high_calorie'] = self.create_top_foods_chart(
                df, 'Energy (kcal)', 10, "Top 10 Highest Calorie Foods"
            )
            
            # 2. Top 10 highest protein foods
            charts['high_protein'] = self.create_top_foods_chart(
                df, 'Protein (g)', 10, "Top 10 Highest Protein Foods"
            )
            
            # 3. Calorie distribution
            charts['calorie_dist'] = self.create_nutrient_distribution_histogram(
                df, 'Energy (kcal)', 50, "Calorie Distribution Across Foods"
            )
            
            # 4. Protein vs Fat scatter plot
            if 'Protein (g)' in df.columns and 'Total Fat (g)' in df.columns:
                charts['protein_fat_scatter'] = self.create_nutrient_density_scatter(
                    df, 'Protein (g)', 'Total Fat (g)', 'Energy (kcal)',
                    "Protein vs Fat Content (Size = Calories)"
                )
            
            # 5. Nutrient correlation heatmap
            charts['correlation'] = self.create_correlation_heatmap(df)
            
            return charts
            
        except Exception as e:
            st.error(f"Error creating dashboard summary: {str(e)}")
            return {}
    
    def display_chart_with_controls(self, chart_func, chart_params: Dict, 
                                   control_key: str) -> go.Figure:
        """
        Display a chart with interactive controls
        
        Args:
            chart_func: Chart creation function
            chart_params (Dict): Parameters for the chart function
            control_key (str): Unique key for the controls
            
        Returns:
            go.Figure: The created chart
        """
        try:
            # Create expandable controls
            with st.expander("Chart Controls", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'height' in chart_params:
                        chart_params['height'] = st.slider(
                            "Chart Height", 300, 800, 
                            chart_params.get('height', 500),
                            key=f"{control_key}_height"
                        )
                
                with col2:
                    if 'top_n' in chart_params:
                        chart_params['top_n'] = st.slider(
                            "Number of Items", 5, 20, 
                            chart_params.get('top_n', 10),
                            key=f"{control_key}_top_n"
                        )
            
            # Create and return the chart
            return chart_func(**chart_params)
            
        except Exception as e:
            st.error(f"Error displaying chart with controls: {str(e)}")
            return self._create_empty_chart("Error creating chart")
