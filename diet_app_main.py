import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

# Import custom modules
from data_processor import DataProcessor
from nutrition_analyzer import NutritionAnalyzer
from food_recommender import FoodRecommender
from dashboard_charts import DashboardCharts

# Page configuration
st.set_page_config(
    page_title="Smart Diet Tracker",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .food-item {
        background: #0c0d0d;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #856404;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

class DietTrackerApp:
    def __init__(self):
        """Initialize the Diet Tracker Application"""
        self.init_session_state()
        self.data_processor = DataProcessor()
        self.nutrition_analyzer = NutritionAnalyzer()
        self.food_recommender = FoodRecommender()
        self.dashboard = DashboardCharts()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'daily_log' not in st.session_state:
            st.session_state.daily_log = []
        if 'food_data' not in st.session_state:
            st.session_state.food_data = None
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []

    def load_data(self) -> bool:
        """Load and cache the food database"""
        try:
            if st.session_state.food_data is None:
                with st.spinner("Loading food database..."):
                    # You would replace this with your actual CSV file path
                    # For demo purposes, I'll create sample data structure
                    st.session_state.food_data = self.data_processor.load_food_database()
            return True
        except Exception as e:
            st.error(f"Error loading food database: {str(e)}")
            return False

    def render_header(self):
        """Render the application header"""
        st.markdown("<h1 class='main-header'>🥗 Smart Diet Tracker</h1>", unsafe_allow_html=True)
        st.markdown("Track your daily nutrition intake with intelligent recommendations")
        
        # Current date display
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info(f"📅 Today's Date: {datetime.now().strftime('%B %d, %Y')}")

    def render_food_search(self):
        """Render the food search interface"""
        st.subheader("🔍 Search & Add Foods")
        
        # Search input
        search_query = st.text_input(
            "Search for food items",
            placeholder="Enter food name (e.g., 'apple', 'chicken breast')",
            help="Type to search through thousands of food items"
        )
        
        if search_query:
            try:
                # Search for foods
                search_results = self.data_processor.search_foods(
                    st.session_state.food_data, 
                    search_query
                )
                
                if search_results:
                    st.write(f"Found {len(search_results)} results:")
                    
                    # Display search results
                    for idx, food in enumerate(search_results[:10]):  # Limit to top 10
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{food['Main food description']}**")
                            st.caption(f"Calories: {food.get('Energy (kcal)', 'N/A')} | "
                                     f"Protein: {food.get('Protein (g)', 'N/A')}g")
                        
                        with col2:
                            serving_size = st.number_input(
                                "Serving",
                                min_value=0.1,
                                max_value=10.0,
                                value=1.0,
                                step=0.1,
                                key=f"serving_{idx}",
                                help="Number of servings"
                            )
                        
                        with col3:
                            if st.button(f"Add", key=f"add_{idx}"):
                                self.add_food_to_log(food, serving_size)
                                st.success("Added to log!")
                                st.rerun()
                else:
                    st.warning("No foods found matching your search.")
                    
            except Exception as e:
                st.error(f"Search error: {str(e)}")

    def add_food_to_log(self, food: Dict, serving_size: float):
        """Add a food item to the daily log"""
        try:
            # Calculate nutritional values based on serving size
            log_entry = {
                'name': food['Main food description'],
                'serving_size': serving_size,
                'timestamp': datetime.now(),
                'food_code': food.get('Food code', ''),
                'calories': float(food.get('Energy (kcal)', 0)) * serving_size,
                'protein': float(food.get('Protein (g)', 0)) * serving_size,
                'carbs': float(food.get('Carbohydrate (g)', 0)) * serving_size,
                'fat': float(food.get('Total Fat (g)', 0)) * serving_size,
                'fiber': float(food.get('Fiber, total dietary (g)', 0)) * serving_size,
                'sugar': float(food.get('Sugars, total (g)', 0)) * serving_size,
                'sodium': float(food.get('Sodium (mg)', 0)) * serving_size,
                'calcium': float(food.get('Calcium (mg)', 0)) * serving_size,
                'iron': float(food.get('Iron (mg)', 0)) * serving_size,
                'vitamin_c': float(food.get('Vitamin C (mg)', 0)) * serving_size,
            }
            
            st.session_state.daily_log.append(log_entry)
            
        except Exception as e:
            st.error(f"Error adding food to log: {str(e)}")

    def render_daily_log(self):
        """Render the daily food log"""
        st.subheader("📝 Today's Food Log")
        
        if not st.session_state.daily_log:
            st.info("No foods logged yet. Start by searching and adding foods above!")
            return
        
        # Display logged foods
        for idx, entry in enumerate(st.session_state.daily_log):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="food-item">
                        <strong>{entry['name']}</strong><br>
                        <small>Serving: {entry['serving_size']:.1f} | 
                        {entry['calories']:.0f} cal | 
                        P: {entry['protein']:.1f}g | 
                        C: {entry['carbs']:.1f}g | 
                        F: {entry['fat']:.1f}g</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.caption(entry['timestamp'].strftime("%I:%M %p"))
                
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_{idx}"):
                        st.session_state.daily_log.pop(idx)
                        st.rerun()

    def render_nutrition_summary(self):
        """Render live nutritional totals"""
        st.subheader("📊 Nutritional Summary")
        
        if not st.session_state.daily_log:
            st.info("Add foods to see nutritional breakdown")
            return
        
        # Calculate totals
        totals = self.nutrition_analyzer.calculate_totals(st.session_state.daily_log)
        
        # Display main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Calories", f"{totals['calories']:.0f}", help="Total calories consumed")
        with col2:
            st.metric("Protein", f"{totals['protein']:.1f}g", help="Total protein intake")
        with col3:
            st.metric("Carbs", f"{totals['carbs']:.1f}g", help="Total carbohydrates")
        with col4:
            st.metric("Fat", f"{totals['fat']:.1f}g", help="Total fat intake")
        
        # Additional nutrients
        with st.expander("View More Nutrients"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Fiber", f"{totals['fiber']:.1f}g")
                st.metric("Sugar", f"{totals['sugar']:.1f}g")
            with col2:
                st.metric("Sodium", f"{totals['sodium']:.0f}mg")
                st.metric("Calcium", f"{totals['calcium']:.0f}mg")
            with col3:
                st.metric("Iron", f"{totals['iron']:.1f}mg")
                st.metric("Vitamin C", f"{totals['vitamin_c']:.1f}mg")

    def render_nutrition_analysis(self):
        """Render nutrition analysis and recommendations"""
        if not st.session_state.daily_log:
            return
        
        st.subheader("🎯 Nutrition Analysis & Recommendations")
        
        # Calculate totals and analyze
        totals = self.nutrition_analyzer.calculate_totals(st.session_state.daily_log)
        analysis = self.nutrition_analyzer.analyze_nutrition(totals)
        
        # Display deficiencies
        if analysis['deficiencies']:
            st.markdown("### ⚠️ Nutrient Gaps")
            for nutrient, info in analysis['deficiencies'].items():
                st.markdown(f"""
                <div class="warning-box">
                    <strong>{nutrient.title()}</strong>: {info['current']:.1f}{info['unit']} / {info['target']:.1f}{info['unit']} 
                    ({info['percentage']:.0f}% of target)
                </div>
                """, unsafe_allow_html=True)
        
        # Display excesses
        if analysis['excesses']:
            st.markdown("### 🔴 Nutrient Excesses")
            for nutrient, info in analysis['excesses'].items():
                st.markdown(f"""
                <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 1rem; border-radius: 8px; margin: 1rem 0; color: #721c24;">
                    <strong>{nutrient.title()}</strong>: {info['current']:.1f}{info['unit']} / {info['target']:.1f}{info['unit']} 
                    ({info['percentage']:.0f}% of target)
                </div>
                """, unsafe_allow_html=True)
        
        # Food recommendations
        if analysis['deficiencies']:
            recommendations = self.food_recommender.get_recommendations(
                analysis['deficiencies'], 
                st.session_state.food_data
            )
            
            if recommendations:
                st.markdown("### 💡 Recommended Foods")
                for nutrient, foods in recommendations.items():
                    with st.expander(f"Foods rich in {nutrient.title()}"):
                        for food in foods[:5]:  # Show top 5
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"• **{food['name']}**")
                                st.caption(f"{nutrient.title()}: {food['nutrient_value']:.1f}{food.get('unit', '')}")
                            with col2:
                                if st.button(f"Add", key=f"rec_{food['food_code']}_{nutrient}"):
                                    # Find full food data and add to log
                                    full_food = self.data_processor.get_food_by_code(
                                        st.session_state.food_data, 
                                        food['food_code']
                                    )
                                    if full_food:
                                        self.add_food_to_log(full_food, 1.0)
                                        st.success("Added to log!")
                                        st.rerun()

    def render_ai_suggestions(self):
        """Render AI-powered food pairing suggestions"""
        if not st.session_state.daily_log:
            return
            
        st.subheader("🤖 AI Nutrition Coach")
        
        try:
            # Get current nutrition status
            totals = self.nutrition_analyzer.calculate_totals(st.session_state.daily_log)
            
            # Generate AI suggestions
            suggestions = self.food_recommender.get_ai_suggestions(
                st.session_state.daily_log, 
                totals
            )
            
            if suggestions:
                st.markdown("### 🍽️ Smart Food Pairing Suggestions")
                for suggestion in suggestions:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>{suggestion['title']}</strong><br>
                        {suggestion['description']}
                        <br><small><strong>Why:</strong> {suggestion['reason']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error generating AI suggestions: {str(e)}")

    def render_dashboard(self):
        """Render nutrition dashboard with charts"""
        if not st.session_state.daily_log:
            st.info("Add foods to your daily log to see dashboard visualizations")
            return
            
        st.subheader("📈 Nutrition Dashboard")
        
        # Calculate totals for charts
        totals = self.nutrition_analyzer.calculate_totals(st.session_state.daily_log)
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Macronutrient pie chart using existing method
            st.plotly_chart(
                self.dashboard.create_macronutrient_pie_chart(totals, "Daily Macronutrient Breakdown"),
                use_container_width=True
            )
            
            # Top nutrients consumed today (create a simple food data structure from daily log)
            daily_foods = []
            for entry in st.session_state.daily_log:
                food_item = {
                    'Main food description': entry['name'],
                    'Energy (kcal)': entry['calories'] / entry['serving_size'],  # Per unit
                    'Protein (g)': entry['protein'] / entry['serving_size'],
                    'Total Fat (g)': entry['fat'] / entry['serving_size'],
                    'Carbohydrate (g)': entry['carbs'] / entry['serving_size']
                }
                daily_foods.append(food_item)
            
            if daily_foods:
                st.plotly_chart(
                    self.dashboard.create_nutrient_comparison_bar(
                        daily_foods, 
                        ['Energy (kcal)', 'Protein (g)', 'Total Fat (g)', 'Carbohydrate (g)'],
                        "Today's Foods - Nutrient Comparison"
                    ),
                    use_container_width=True
                )
        
        with col2:
            # Create a meal planning chart showing current vs targets
            selected_foods = []
            for entry in st.session_state.daily_log:
                food_with_portion = {
                    'Main food description': entry['name'],
                    'Energy (kcal)': entry['calories'] / entry['serving_size'],
                    'Protein (g)': entry['protein'] / entry['serving_size'],
                    'Carbohydrate (g)': entry['carbs'] / entry['serving_size'],
                    'Total Fat (g)': entry['fat'] / entry['serving_size'],
                    'Fiber, total dietary (g)': entry['fiber'] / entry['serving_size'],
                    'Sodium (mg)': entry['sodium'] / entry['serving_size'],
                    'portion': entry['serving_size'] * 100  # Convert to grams
                }
                selected_foods.append(food_with_portion)
            
            # Get daily targets from session state or use defaults
            daily_targets = {
                'Energy (kcal)': getattr(st.session_state, 'calories_goal', 2000),
                'Protein (g)': getattr(st.session_state, 'protein_goal', 150),
                'Carbohydrate (g)': 250,
                'Total Fat (g)': 65,
                'Fiber, total dietary (g)': 25,
                'Sodium (mg)': 2300
            }
            
            st.plotly_chart(
                self.dashboard.create_meal_planning_chart(
                    selected_foods, 
                    daily_targets,
                    "Daily Progress vs Goals"
                ),
                use_container_width=True
            )
            
            # Timeline of calorie intake throughout the day
            if len(st.session_state.daily_log) > 1:
                # Create a simple timeline chart
                timeline_data = []
                cumulative_calories = 0
                for entry in st.session_state.daily_log:
                    cumulative_calories += entry['calories']
                    timeline_data.append({
                        'time': entry['timestamp'].strftime('%H:%M'),
                        'calories': entry['calories'],
                        'cumulative': cumulative_calories,
                        'food': entry['name'][:20] + '...' if len(entry['name']) > 20 else entry['name']
                    })
                
                # Create a simple line chart for timeline
                import plotly.graph_objects as go
                
                fig = go.Figure()
                
                # Add cumulative calories line
                fig.add_trace(go.Scatter(
                    x=[d['time'] for d in timeline_data],
                    y=[d['cumulative'] for d in timeline_data],
                    mode='lines+markers',
                    name='Cumulative Calories',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{text}</b><br>Time: %{x}<br>Total: %{y:.0f} cal<extra></extra>',
                    text=[d['food'] for d in timeline_data]
                ))
                
                # Add individual meal bars
                fig.add_trace(go.Bar(
                    x=[d['time'] for d in timeline_data],
                    y=[d['calories'] for d in timeline_data],
                    name='Meal Calories',
                    marker_color='rgba(255, 127, 14, 0.6)',
                    hovertemplate='<b>%{text}</b><br>Time: %{x}<br>Calories: %{y:.0f}<extra></extra>',
                    text=[d['food'] for d in timeline_data]
                ))
                
                fig.update_layout(
                    title=dict(text="Calorie Intake Timeline", x=0.5, font=dict(size=16)),
                    xaxis_title="Time",
                    yaxis_title="Calories",
                    height=400,
                    margin=dict(t=50, b=50, l=50, r=50),
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional dashboard section with expandable charts
        with st.expander("📊 Additional Analytics", expanded=False):
            if st.session_state.food_data is not None:
                col3, col4 = st.columns(2)
                
                with col3:
                    # Show correlation heatmap for nutrients in current log
                    current_nutrients = ['Energy (kcal)', 'Protein (g)', 'Carbohydrate (g)', 
                                    'Total Fat (g)', 'Fiber, total dietary (g)', 'Sodium (mg)']
                    
                    st.plotly_chart(
                        self.dashboard.create_correlation_heatmap(
                            st.session_state.food_data, 
                            current_nutrients,
                            "Nutrient Correlations in Database"
                        ),
                        use_container_width=True
                    )
                
                with col4:
                    # Show top protein foods from database for reference
                    st.plotly_chart(
                        self.dashboard.create_top_foods_chart(
                            st.session_state.food_data,
                            'Protein (g)',
                            8,
                            "Top Protein Foods (Database)"
                        ),
                        use_container_width=True
                    )
            
            # Daily summary metrics
            st.markdown("### 📋 Daily Summary")
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                st.metric(
                    "Total Foods", 
                    len(st.session_state.daily_log),
                    help="Number of food items logged today"
                )
            
            with summary_col2:
                avg_cal_per_food = totals['calories'] / len(st.session_state.daily_log) if st.session_state.daily_log else 0
                st.metric(
                    "Avg Cal/Food", 
                    f"{avg_cal_per_food:.0f}",
                    help="Average calories per food item"
                )
            
            with summary_col3:
                protein_percentage = (totals['protein'] * 4 / totals['calories'] * 100) if totals['calories'] > 0 else 0
                st.metric(
                    "Protein %", 
                    f"{protein_percentage:.1f}%",
                    help="Percentage of calories from protein"
                )
            
            with summary_col4:
                first_meal = min(st.session_state.daily_log, key=lambda x: x['timestamp']) if st.session_state.daily_log else None
                last_meal = max(st.session_state.daily_log, key=lambda x: x['timestamp']) if st.session_state.daily_log else None
                
                if first_meal and last_meal and len(st.session_state.daily_log) > 1:
                    eating_window = last_meal['timestamp'] - first_meal['timestamp']
                    hours = eating_window.total_seconds() / 3600
                    st.metric(
                        "Eating Window", 
                        f"{hours:.1f}h",
                        help="Time between first and last meal"
                    )
                else:
                    st.metric("Eating Window", "N/A")

    def render_sidebar(self):
        """Render sidebar with additional controls"""
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Clear log button
            if st.button("🗑️ Clear All Foods", type="secondary"):
                if st.session_state.daily_log:
                    st.session_state.daily_log = []
                    st.success("Food log cleared!")
                    st.rerun()
            
            # Export data
            if st.session_state.daily_log:
                if st.button("📊 Export Data"):
                    # Create downloadable CSV
                    df = pd.DataFrame(st.session_state.daily_log)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"nutrition_log_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            # Daily goals settings
            st.header("🎯 Daily Goals")
            calories_goal = st.slider("Calories Goal", 1200, 3000, 2000)
            protein_goal = st.slider("Protein Goal (g)", 50, 200, 150)
            
            # Store goals in session state
            st.session_state.calories_goal = calories_goal
            st.session_state.protein_goal = protein_goal

    def run(self):
        """Main application runner"""
        # Load data
        if not self.load_data():
            return
        
        # Render components
        self.render_header()
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Search & Add", 
            "📝 Daily Log", 
            "📊 Summary", 
            "🎯 Analysis", 
            "📈 Dashboard"
        ])
        
        with tab1:
            self.render_food_search()
        
        with tab2:
            self.render_daily_log()
        
        with tab3:
            self.render_nutrition_summary()
        
        with tab4:
            self.render_nutrition_analysis()
            self.render_ai_suggestions()
        
        with tab5:
            self.render_dashboard()

# Run the application
if __name__ == "__main__":
    app = DietTrackerApp()
    app.run()
