import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import time
import random

# Import custom modules
from data_processor import DataProcessor
from nutrition_analyzer import NutritionAnalyzer
from food_recommender import FoodRecommender
from dashboard_charts import DashboardCharts

# Page configuration with enhanced settings
st.set_page_config(
    page_title="Smart Diet Tracker",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",  # Start collapsed for cleaner look
    menu_items={
        'Get Help': 'https://github.com/your-repo/smart-diet-tracker',
        'Report a bug': "https://github.com/your-repo/smart-diet-tracker/issues",
        'About': "Smart Diet Tracker - Your AI-powered nutrition companion"
    }
)

# Enhanced CSS with modern design principles
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #10B981;
        --primary-dark: #059669;
        --secondary-color: #8B5CF6;
        --accent-color: #F59E0B;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --info-color: #3B82F6;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --hover-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --border-radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global styles */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Enhanced header with dynamic elements */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        padding: 2rem 3rem;
        border-radius: 0 0 24px 24px;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .header-content {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .dynamic-emoji {
        font-size: 3rem;
        animation: bounce 2s infinite;
        margin-right: 1rem;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .date-display {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        padding: 0.8rem 1.5rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(255, 255, 255, 0.3);
        font-weight: 500;
        text-align: center;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--hover-shadow);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--background-gradient);
    }
    
    /* Enhanced food item cards */
    .food-item {
        background: white;
        padding: 1.2rem;
        border-radius: var(--border-radius);
        margin: 0.8rem 0;
        border-left: 4px solid var(--success-color);
        box-shadow: var(--card-shadow);
        transition: var(--transition);
        position: relative;
    }
    
    .food-item:hover {
        transform: translateX(4px);
        box-shadow: var(--hover-shadow);
        border-left-color: var(--primary-dark);
    }
    
    .food-item-header {
        font-weight: 600;
        font-size: 1.1rem;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .food-item-details {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 400;
    }
    
    /* Enhanced alert boxes */
    .alert-box {
        padding: 1.2rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border: 1px solid;
        position: relative;
        transition: var(--transition);
    }
    
    .alert-box:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-color: #f59e0b;
        color: #92400e;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-color: var(--success-color);
        color: #065f46;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-color: var(--error-color);
        color: #991b1b;
    }
    
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-color: var(--info-color);
        color: #1e40af;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        border-radius: var(--border-radius);
        border: none;
        font-weight: 500;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
    }
    
    /* Loading animations */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 0.5rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e5e7eb;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        border-radius: var(--border-radius);
        padding: 0.5rem;
        box-shadow: var(--card-shadow);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: var(--transition);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--background-gradient);
        color: white;
    }
    
    /* Progress indicators */
    .progress-ring {
        transform: rotate(-90deg);
    }
    
    .progress-ring-circle {
        transition: stroke-dashoffset 0.35s;
        transform-origin: 50% 50%;
    }
    
    /* Tooltip enhancements */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Micro-interactions */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Enhanced form controls */
    .stNumberInput input {
        border-radius: var(--border-radius);
        border: 2px solid #e5e7eb;
        transition: var(--transition);
    }
    
    .stNumberInput input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }
    
    .stTextInput input {
        border-radius: var(--border-radius);
        border: 2px solid #e5e7eb;
        transition: var(--transition);
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }
    
    /* Save confirmation animation */
    .save-confirmation {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success-color);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--hover-shadow);
        animation: slideInRight 0.3s ease-out;
        z-index: 1000;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Chart loading placeholder */
    .chart-loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 400px;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: var(--border-radius);
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
</style>
""", unsafe_allow_html=True)

class EnhancedDietTrackerApp:
    def __init__(self):
        """Initialize the Enhanced Diet Tracker Application"""
        self.init_session_state()
        self.data_processor = DataProcessor()
        self.nutrition_analyzer = NutritionAnalyzer()
        self.food_recommender = FoodRecommender()
        self.dashboard = DashboardCharts()
        
    def init_session_state(self):
        """Initialize session state variables with enhanced tracking"""
        if 'daily_log' not in st.session_state:
            st.session_state.daily_log = []
        if 'food_data' not in st.session_state:
            st.session_state.food_data = None
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'last_save_time' not in st.session_state:
            st.session_state.last_save_time = None
        if 'show_save_confirmation' not in st.session_state:
            st.session_state.show_save_confirmation = False
        if 'daily_emoji' not in st.session_state:
            # Set a daily emoji that changes each day
            today = datetime.now().date()
            random.seed(today.toordinal())  # Consistent emoji for the day
            emojis = ["🥗", "🍎", "🥕", "🥦", "🍊", "🍇", "🥑", "🌶️", "🍅", "🥬"]
            st.session_state.daily_emoji = random.choice(emojis)

    def get_dynamic_greeting(self) -> str:
        """Get time-based greeting"""
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning! 🌅"
        elif hour < 17:
            return "Good Afternoon! ☀️"
        else:
            return "Good Evening! 🌙"

    def load_data(self) -> bool:
        """Load and cache the food database with loading animation"""
        try:
            if st.session_state.food_data is None:
                # Show enhanced loading
                loading_placeholder = st.empty()
                loading_placeholder.markdown("""
                <div class="chart-loading">
                    <div>
                        <div class="loading-spinner"></div>
                        Loading nutrition database...
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Simulate realistic loading time
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # Simulate loading
                    progress_bar.progress(i + 1)
                
                st.session_state.food_data = self.data_processor.load_food_database()
                loading_placeholder.empty()
                progress_bar.empty()
                
                # Show success confirmation
                st.success("✅ Database loaded successfully!")
                time.sleep(1)
                
            return True
        except Exception as e:
            st.error(f"❌ Error loading food database: {str(e)}")
            return False

    def render_enhanced_header(self):
        """Render the enhanced application header"""
        current_time = datetime.now()
        formatted_date = current_time.strftime("%A, %B %d, %Y")
        formatted_time = current_time.strftime("%I:%M %p")
        
        st.markdown(f"""
        <div class="main-header">
            <div class="header-content">
                <div style="display: flex; align-items: center;">
                    <span class="dynamic-emoji">{st.session_state.daily_emoji}</span>
                    <div>
                        <h1 class="header-title">Smart Diet Tracker</h1>
                        <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">{self.get_dynamic_greeting()}</p>
                    </div>
                </div>
                <div class="date-display">
                    <div style="font-size: 1.2rem; font-weight: 600;">{formatted_date}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">{formatted_time}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def show_save_confirmation(self, message: str = "Changes saved successfully!"):
        """Show animated save confirmation"""
        if st.session_state.show_save_confirmation:
            st.markdown(f"""
            <div class="save-confirmation">
                ✅ {message}
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-hide after 3 seconds
            time.sleep(3)
            st.session_state.show_save_confirmation = False

    def render_enhanced_food_search(self):
        """Enhanced food search interface with better UX"""
        st.markdown("### 🔍 Discover & Add Foods")
        st.markdown("*Search through our comprehensive nutrition database*")
        
        # Enhanced search input with better placeholder
        search_query = st.text_input(
            "Search for food items",
            placeholder="Try 'grilled chicken', 'quinoa salad', or 'greek yogurt'...",
            help="💡 Pro tip: Use specific terms for better results (e.g., 'baked salmon' vs 'fish')",
            key="food_search"
        )
        
        if search_query:
            # Show loading state
            with st.spinner("🔍 Searching nutrition database..."):
                search_results = self.data_processor.search_foods(
                    st.session_state.food_data, 
                    search_query
                )
            
            if search_results:
                st.markdown(f"""
                <div class="info-box">
                    <strong>🎯 Found {len(search_results)} results</strong> - Showing top 10 matches
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced results display
                for idx, food in enumerate(search_results[:10]):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([4, 1.5, 1, 1])
                        
                        with col1:
                            calories = food.get('Energy (kcal)', 0)
                            protein = food.get('Protein (g)', 0)
                            
                            # Color-code based on nutritional value
                            if calories > 300:
                                cal_color = "#ef4444"  # High calorie
                            elif calories > 150:
                                cal_color = "#f59e0b"  # Medium calorie
                            else:
                                cal_color = "#10b981"  # Low calorie
                            
                            st.markdown(f"""
                            <div class="food-item">
                                <div class="food-item-header">{food['Main food description']}</div>
                                <div class="food-item-details">
                                    <span style="color: {cal_color}; font-weight: 600;">⚡ {calories} cal</span> • 
                                    <span style="color: #8b5cf6; font-weight: 600;">💪 {protein}g protein</span> • 
                                    <span style="color: #6b7280;">🍃 {food.get('Carbohydrate (g)', 0)}g carbs</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            serving_size = st.number_input(
                                "Servings",
                                min_value=0.1,
                                max_value=10.0,
                                value=1.0,
                                step=0.1,
                                key=f"serving_{idx}",
                                help="Adjust portion size"
                            )
                        
                        with col3:
                            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                            portion_info = st.selectbox(
                                "Unit",
                                ["serving", "cup", "oz", "grams"],
                                key=f"unit_{idx}",
                                help="Portion unit"
                            )
                        
                        with col4:
                            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                            if st.button("➕ Add", key=f"add_{idx}", help="Add to daily log"):
                                self.add_food_to_log(food, serving_size)
                                st.session_state.show_save_confirmation = True
                                st.success("✅ Added to your log!")
                                time.sleep(1)
                                st.rerun()
            else:
                st.markdown("""
                <div class="warning-box">
                    <strong>🤔 No results found</strong><br>
                    Try different keywords or check spelling. Consider searching for:
                    <ul style="margin: 0.5rem 0 0 1rem;">
                        <li>Generic names (e.g., "chicken" instead of brand names)</li>
                        <li>Common food categories (e.g., "bread", "milk", "apple")</li>
                        <li>Cooking methods (e.g., "baked", "grilled", "raw")</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

    def render_enhanced_daily_log(self):
        """Enhanced daily log with better visual hierarchy"""
        st.markdown("### 📝 Today's Nutrition Log")
        
        if not st.session_state.daily_log:
            st.markdown("""
            <div class="info-box pulse">
                <strong>🍽️ Your food journal is empty</strong><br>
                Start tracking by searching and adding foods in the "Discover & Add Foods" tab above!
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Log summary header
        total_items = len(st.session_state.daily_log)
        total_calories = sum(entry['calories'] for entry in st.session_state.daily_log)
        
        st.markdown(f"""
        <div class="success-box">
            <strong>📊 Log Summary:</strong> {total_items} items • {total_calories:.0f} total calories
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced log display
        for idx, entry in enumerate(st.session_state.daily_log):
            col1, col2, col3 = st.columns([5, 1.5, 0.8])
            
            with col1:
                # Calculate nutrition density indicators
                protein_ratio = (entry['protein'] * 4) / entry['calories'] if entry['calories'] > 0 else 0
                
                # Protein quality indicator
                if protein_ratio > 0.3:
                    protein_quality = "🟢 High"
                elif protein_ratio > 0.15:
                    protein_quality = "🟡 Good"
                else:
                    protein_quality = "🔴 Low"
                
                st.markdown(f"""
                <div class="food-item">
                    <div class="food-item-header">{entry['name']}</div>
                    <div class="food-item-details">
                        <strong>Portion:</strong> {entry['serving_size']:.1f} serving(s) • 
                        <strong style="color: #ef4444;">⚡ {entry['calories']:.0f} cal</strong><br>
                        <strong>Macros:</strong> 
                        P: <span style="color: #8b5cf6; font-weight: 600;">{entry['protein']:.1f}g</span> • 
                        C: <span style="color: #f59e0b; font-weight: 600;">{entry['carbs']:.1f}g</span> • 
                        F: <span style="color: #10b981; font-weight: 600;">{entry['fat']:.1f}g</span><br>
                        <small>Protein Quality: {protein_quality} • Fiber: {entry['fiber']:.1f}g</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                time_ago = datetime.now() - entry['timestamp']
                if time_ago.seconds < 3600:
                    time_display = f"{time_ago.seconds // 60}m ago"
                else:
                    time_display = entry['timestamp'].strftime("%I:%M %p")
                
                st.markdown(f"""
                <div style="text-align: center; padding-top: 1rem;">
                    <div style="font-size: 0.9rem; color: #6b7280;">🕐 {time_display}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"remove_{idx}", help="Remove from log"):
                    st.session_state.daily_log.pop(idx)
                    st.session_state.show_save_confirmation = True
                    st.rerun()

    def render_enhanced_sidebar(self):
        """Enhanced sidebar with modern toggle controls"""
        with st.sidebar:
            st.markdown("### ⚙️ Smart Controls")
            
            # Enhanced goal setting with visual indicators
            st.markdown("#### 🎯 Daily Nutrition Goals")
            
            # Calories goal with visual feedback
            calories_goal = st.slider(
                "Daily Calories Target",
                min_value=1200,
                max_value=3500,
                value=getattr(st.session_state, 'calories_goal', 2000),
                step=50,
                help="Adjust based on your activity level and goals"
            )
            
            # Show calories progress if there's data
            if st.session_state.daily_log:
                current_calories = sum(entry['calories'] for entry in st.session_state.daily_log)
                progress = min(current_calories / calories_goal, 1.0)
                st.progress(progress)
                st.caption(f"Progress: {current_calories:.0f} / {calories_goal} cal ({progress*100:.0f}%)")
            
            # Protein goal
            protein_goal = st.slider(
                "Daily Protein Target (g)",
                min_value=50,
                max_value=250,
                value=getattr(st.session_state, 'protein_goal', 150),
                step=5,
                help="Higher for muscle building, moderate for maintenance"
            )
            
            # Show protein progress
            if st.session_state.daily_log:
                current_protein = sum(entry['protein'] for entry in st.session_state.daily_log)
                protein_progress = min(current_protein / protein_goal, 1.0)
                st.progress(protein_progress)
                st.caption(f"Progress: {current_protein:.0f} / {protein_goal}g ({protein_progress*100:.0f}%)")
            
            # Store goals
            st.session_state.calories_goal = calories_goal
            st.session_state.protein_goal = protein_goal
            
            st.divider()
            
            # Enhanced action buttons
            st.markdown("#### 🔧 Quick Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Clear Log", help="Remove all foods from today's log", use_container_width=True):
                    if st.session_state.daily_log:
                        st.session_state.daily_log = []
                        st.success("✅ Log cleared!")
                        st.rerun()
            
            with col2:
                if st.session_state.daily_log:
                    df = pd.DataFrame(st.session_state.daily_log)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Export",
                        data=csv,
                        file_name=f"nutrition_log_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        help="Download your nutrition data",
                        use_container_width=True
                    )
            
            # Enhanced settings section
            st.markdown("#### 🎨 Display Settings")
            
            # Theme toggle (placeholder for future enhancement)
            dark_mode = st.toggle("🌙 Dark Mode", help="Toggle dark theme (coming soon)")
            
            # Notification settings
            notifications = st.toggle("🔔 Smart Reminders", value=True, help="Get nutrition reminders")
            
            # Advanced settings in expander
            with st.expander("🔬 Advanced Settings"):
                st.markdown("**Nutrition Preferences**")
                metric_system = st.radio("Units", ["Imperial", "Metric"])
                decimal_places = st.select_slider("Precision", [0, 1, 2], value=1)
                
                st.markdown("**Analysis Settings**")
                analysis_sensitivity = st.slider("Analysis Sensitivity", 1, 5, 3, help="Higher values show more detailed insights")
                show_micronutrients = st.checkbox("Show Micronutrients", value=False)
                
                # Store advanced settings
                st.session_state.metric_system = metric_system
                st.session_state.decimal_places = decimal_places
                st.session_state.analysis_sensitivity = analysis_sensitivity
                st.session_state.show_micronutrients = show_micronutrients

    def add_food_to_log(self, food: Dict, serving_size: float):
        """Add food to daily log with enhanced data structure"""
        try:
            # Calculate nutritional values based on serving size
            entry = {
                'name': food['Main food description'],
                'serving_size': serving_size,
                'calories': food.get('Energy (kcal)', 0) * serving_size,
                'protein': food.get('Protein (g)', 0) * serving_size,
                'carbs': food.get('Carbohydrate (g)', 0) * serving_size,
                'fat': food.get('Total Fat (g)', 0) * serving_size,
                'fiber': food.get('Fibre (g)', 0) * serving_size,
                'sugar': food.get('Sugars (g)', 0) * serving_size,
                'sodium': food.get('Sodium (mg)', 0) * serving_size,
                'timestamp': datetime.now(),
                'food_id': food.get('Food code', ''),
                'category': food.get('Major food group', 'Other')
            }
            
            st.session_state.daily_log.append(entry)
            st.session_state.last_save_time = datetime.now()
            
        except Exception as e:
            st.error(f"Error adding food to log: {str(e)}")

    def render_enhanced_nutrition_summary(self):
        """Enhanced nutrition summary with better visualizations"""
        if not st.session_state.daily_log:
            st.markdown("""
            <div class="info-box">
                <strong>📊 No data to analyze yet</strong><br>
                Add some foods to see your nutrition summary and insights!
            </div>
            """, unsafe_allow_html=True)
            return

        # Calculate totals
        totals = {
            'calories': sum(entry['calories'] for entry in st.session_state.daily_log),
            'protein': sum(entry['protein'] for entry in st.session_state.daily_log),
            'carbs': sum(entry['carbs'] for entry in st.session_state.daily_log),
            'fat': sum(entry['fat'] for entry in st.session_state.daily_log),
            'fiber': sum(entry['fiber'] for entry in st.session_state.daily_log),
            'sugar': sum(entry['sugar'] for entry in st.session_state.daily_log),
            'sodium': sum(entry['sodium'] for entry in st.session_state.daily_log)
        }

        # Enhanced metrics display
        st.markdown("### 📊 Daily Nutrition Summary")
        
        # Main metrics in enhanced cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            calories_goal = getattr(st.session_state, 'calories_goal', 2000)
            calories_progress = min(totals['calories'] / calories_goal, 1.0) * 100
            
            # Color coding based on goal achievement
            if calories_progress < 80:
                color = "#ef4444"  # Red - under target
            elif calories_progress <= 110:
                color = "#10b981"  # Green - on target
            else:
                color = "#f59e0b"  # Orange - over target
            
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {color}; margin: 0;">🔥 {totals['calories']:.0f}</h3>
                <p style="margin: 0; color: #6b7280;">Calories</p>
                <div style="width: 100%; background: #e5e7eb; border-radius: 10px; height: 8px; margin-top: 8px;">
                    <div style="width: {min(calories_progress, 100):.0f}%; background: {color}; height: 8px; border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
                <small style="color: #6b7280;">{calories_progress:.0f}% of goal</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            protein_goal = getattr(st.session_state, 'protein_goal', 150)
            protein_progress = min(totals['protein'] / protein_goal, 1.0) * 100
            protein_color = "#8b5cf6"
            
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {protein_color}; margin: 0;">💪 {totals['protein']:.0f}g</h3>
                <p style="margin: 0; color: #6b7280;">Protein</p>
                <div style="width: 100%; background: #e5e7eb; border-radius: 10px; height: 8px; margin-top: 8px;">
                    <div style="width: {min(protein_progress, 100):.0f}%; background: {protein_color}; height: 8px; border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
                <small style="color: #6b7280;">{protein_progress:.0f}% of goal</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            carb_color = "#f59e0b"
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {carb_color}; margin: 0;">🌾 {totals['carbs']:.0f}g</h3>
                <p style="margin: 0; color: #6b7280;">Carbohydrates</p>
                <div style="margin-top: 8px;">
                    <small style="color: #6b7280;">Fiber: {totals['fiber']:.0f}g</small><br>
                    <small style="color: #6b7280;">Sugar: {totals['sugar']:.0f}g</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            fat_color = "#10b981"
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {fat_color}; margin: 0;">🥑 {totals['fat']:.0f}g</h3>
                <p style="margin: 0; color: #6b7280;">Total Fat</p>
                <div style="margin-top: 8px;">
                    <small style="color: #6b7280;">Sodium: {totals['sodium']:.0f}mg</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Macronutrient distribution chart
        st.markdown("#### 🥧 Macronutrient Distribution")
        
        # Calculate calories from macros
        protein_cals = totals['protein'] * 4
        carb_cals = totals['carbs'] * 4
        fat_cals = totals['fat'] * 9
        
        if protein_cals + carb_cals + fat_cals > 0:
            fig = px.pie(
                values=[protein_cals, carb_cals, fat_cals],
                names=['Protein', 'Carbohydrates', 'Fat'],
                color_discrete_sequence=['#8b5cf6', '#f59e0b', '#10b981'],
                title="Calories by Macronutrient"
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>%{value:.0f} calories<br>%{percent}<extra></extra>'
            )
            
            fig.update_layout(
                showlegend=True,
                height=400,
                font=dict(size=12),
                title_x=0.5
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def render_enhanced_nutrition_analysis(self):
        """Enhanced nutrition analysis with AI insights"""
        if not st.session_state.daily_log:
            return

        st.markdown("### 🔍 Smart Nutrition Analysis")

        # Calculate analysis metrics
        totals = {
            'calories': sum(entry['calories'] for entry in st.session_state.daily_log),
            'protein': sum(entry['protein'] for entry in st.session_state.daily_log),
            'carbs': sum(entry['carbs'] for entry in st.session_state.daily_log),
            'fat': sum(entry['fat'] for entry in st.session_state.daily_log),
            'fiber': sum(entry['fiber'] for entry in st.session_state.daily_log)
        }

        calories_goal = getattr(st.session_state, 'calories_goal', 2000)
        protein_goal = getattr(st.session_state, 'protein_goal', 150)

        # Generate insights
        insights = []
        
        # Calorie analysis
        if totals['calories'] < calories_goal * 0.8:
            insights.append({
                'type': 'warning',
                'title': '⚠️ Low Calorie Intake',
                'message': f"You're {calories_goal - totals['calories']:.0f} calories below your goal. Consider adding nutrient-dense foods."
            })
        elif totals['calories'] > calories_goal * 1.15:
            insights.append({
                'type': 'info',
                'title': '📊 High Calorie Intake',
                'message': f"You're {totals['calories'] - calories_goal:.0f} calories over your goal. Monitor portion sizes if weight management is a concern."
            })
        else:
            insights.append({
                'type': 'success',
                'title': '✅ Calorie Goal Achieved',
                'message': "Great job staying within your calorie target!"
            })

        # Protein analysis
        if totals['protein'] < protein_goal * 0.8:
            insights.append({
                'type': 'warning',
                'title': '💪 Boost Your Protein',
                'message': f"Add {protein_goal - totals['protein']:.0f}g more protein. Try lean meats, eggs, or protein powder."
            })
        else:
            insights.append({
                'type': 'success',
                'title': '💪 Protein Target Met',
                'message': "Excellent protein intake for muscle maintenance and growth!"
            })

        # Fiber analysis
        if totals['fiber'] < 25:
            insights.append({
                'type': 'info',
                'title': '🌾 Increase Fiber Intake',
                'message': "Add more fruits, vegetables, and whole grains for better digestive health."
            })

        # Display insights
        for insight in insights:
            box_class = f"{insight['type']}-box"
            st.markdown(f"""
            <div class="{box_class}">
                <strong>{insight['title']}</strong><br>
                {insight['message']}
            </div>
            """, unsafe_allow_html=True)

        # --- Food Recommendations Section ---
        # Analyze nutrition for deficiencies
        analysis = self.nutrition_analyzer.analyze_nutrition(totals)
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
                                st.markdown(f"• <b>{food['name']}</b>", unsafe_allow_html=True)
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
                                        st.session_state.show_save_confirmation = True
                                        st.success("✅ Added to your log!")
                                        st.rerun()

    def render_enhanced_ai_suggestions(self):
        """Enhanced AI-powered food recommendations"""
        if not st.session_state.daily_log:
            return

        st.markdown("### 🤖 AI-Powered Recommendations")

        # Analyze current intake
        totals = {
            'calories': sum(entry['calories'] for entry in st.session_state.daily_log),
            'protein': sum(entry['protein'] for entry in st.session_state.daily_log),
            'fiber': sum(entry['fiber'] for entry in st.session_state.daily_log)
        }

        calories_goal = getattr(st.session_state, 'calories_goal', 2000)
        protein_goal = getattr(st.session_state, 'protein_goal', 150)

        # Generate recommendations
        recommendations = []

        # Calorie-based recommendations
        remaining_calories = calories_goal - totals['calories']
        if remaining_calories > 200:
            recommendations.extend([
                "🥜 Mixed nuts (almonds, walnuts) - healthy fats and protein",
                "🍌 Banana with peanut butter - quick energy and potassium",
                "🥤 Protein smoothie with berries - vitamins and minerals"
            ])

        # Protein-based recommendations
        protein_needed = protein_goal - totals['protein']
        if protein_needed > 20:
            recommendations.extend([
                "🐟 Grilled salmon or tuna - omega-3 fatty acids",
                "🥚 Greek yogurt with berries - probiotics and protein",
                "🍗 Lean chicken breast - complete amino acids"
            ])

        # Fiber recommendations
        if totals['fiber'] < 25:
            recommendations.extend([
                "🥦 Steamed broccoli or Brussels sprouts - fiber and vitamins",
                "🍎 Apple with skin - soluble and insoluble fiber",
                "🌾 Oatmeal with chia seeds - heart-healthy fiber"
            ])

        if recommendations:
            st.markdown("**🎯 Personalized Suggestions:**")
            for rec in recommendations[:5]:  # Show top 5
                st.markdown(f"• {rec}")
        else:
            st.markdown("""
            <div class="success-box">
                <strong>🎉 Perfect Balance!</strong><br>
                Your nutrition looks well-balanced for today. Keep up the great work!
            </div>
            """, unsafe_allow_html=True)

    def render_enhanced_dashboard(self):
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

    def run(self):
        """Main application runner with enhanced flow"""
        # Load data with enhanced loading
        if not self.load_data():
            return
        
        # Render enhanced components
        self.render_enhanced_header()
        self.render_enhanced_sidebar()
        
        # Show save confirmation if needed
        if st.session_state.show_save_confirmation:
            self.show_save_confirmation()
        
        # Enhanced main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Discover & Add", 
            "📝 Today's Log", 
            "📊 Nutrition Summary", 
            "🎯 Smart Analysis", 
            "📈 Dashboard"
        ])
        
        with tab1:
            self.render_enhanced_food_search()
        
        with tab2:
            self.render_enhanced_daily_log()
        
        with tab3:
            self.render_enhanced_nutrition_summary()
        
        with tab4:
            self.render_enhanced_nutrition_analysis()
            self.render_enhanced_ai_suggestions()
        
        with tab5:
            self.render_enhanced_dashboard()

# Run the enhanced application
if __name__ == "__main__":
    app = EnhancedDietTrackerApp()
    app.run()