import streamlit as st
import base64
import time
import json
from datetime import datetime
from google import genai
import io
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import hashlib

# Page configuration
st.set_page_config(
    page_title="Bugs.qa - AI Bug Solver",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Google AI client
@st.cache_resource
def init_genai_client():
    try:
        # Get API key from environment variables (Streamlit Secrets)
        api_key = os.environ.get('GOOGLE_API_KEY')
        
        if not api_key:
            st.error("Google API key not found. Please set the GOOGLE_API_KEY in your environment variables or Streamlit secrets.")
            return None
            
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Failed to initialize AI client: {str(e)}")
        return None

# Enhanced custom CSS with advanced styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        color: #1f2937;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        min-height: 100vh;
    }
    
    /* Ensure all text is readable */
    .stMarkdown, .stText, p, div, span, label {
        color: #1f2937 !important;
    }
    
    /* Streamlit specific text elements */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label, .stSlider label {
        color: #374151 !important;
        font-weight: 500;
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        color: #1f2937 !important;
        background-color: #ffffff !important;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Enhanced Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
        opacity: 0.3;
    }
    
    .main-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.3rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced Card Styling */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .feature-card h3, .feature-card h4, .feature-card p {
        color: #1f2937 !important;
        position: relative;
        z-index: 1;
    }
    
    /* Code Block Styling */
    .code-block {
        background: #1e293b;
        color: #e2e8f0;
        font-family: 'JetBrains Mono', monospace;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        overflow-x: auto;
        position: relative;
        border: 1px solid #334155;
    }
    
    .code-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #334155;
    }
    
    .code-lang {
        background: #667eea;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Enhanced Upload Zone */
    .upload-zone {
        border: 3px dashed #667eea;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8edff 100%);
        margin: 1.5rem 0;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-zone::before {
        content: '📁';
        font-size: 4rem;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        opacity: 0.1;
        z-index: 0;
    }
    
    .upload-zone:hover {
        border-color: #5a67d8;
        background: linear-gradient(135deg, #f0f3ff 0%, #dde4ff 100%);
        transform: scale(1.02);
    }
    
    .upload-zone h4, .upload-zone p {
        color: #374151 !important;
        margin: 0.5rem 0;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover:before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Enhanced Solution Box */
    .solution-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #bbf7d0;
        border-left: 6px solid #10b981;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #1f2937;
        position: relative;
        overflow: hidden;
    }
    
    .solution-box::before {
        content: '✅';
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 1.5rem;
        opacity: 0.3;
    }
    
    .solution-box h3 {
        color: #059669 !important;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid #fecaca;
        border-left: 6px solid #ef4444;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #1f2937;
    }
    
    /* Enhanced Stats Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Progress Bar */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%);
        color: #1f2937;
    }
    
    .sidebar h3, .sidebar p, .sidebar div {
        color: #1f2937 !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        color: #374151 !important;
        background: transparent;
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        color: #1f2937 !important;
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Animation Classes */
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .slide-in-left {
        animation: slideInLeft 0.8s ease-out;
    }
    
    .slide-in-right {
        animation: slideInRight 0.8s ease-out;
    }
    
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes slideInLeft {
        from { 
            opacity: 0; 
            transform: translateX(-50px); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0); 
        }
    }
    
    @keyframes slideInRight {
        from { 
            opacity: 0; 
            transform: translateX(50px); 
        }
        to { 
            opacity: 1; 
            transform: translateX(0); 
        }
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8, #6d28d9);
    }
    
    </style>
    """, unsafe_allow_html=True)

# Initialize enhanced session state
def init_session_state():
    if 'bug_history' not in st.session_state:
        st.session_state.bug_history = []
    if 'total_bugs_solved' not in st.session_state:
        st.session_state.total_bugs_solved = 0
    if 'user_satisfaction' not in st.session_state:
        st.session_state.user_satisfaction = 95.0
    if 'code_snippets' not in st.session_state:
        st.session_state.code_snippets = []
    if 'error_patterns' not in st.session_state:
        st.session_state.error_patterns = {}
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'theme': 'light',
            'language': 'Python',
            'complexity': 'intermediate'
        }

# Enhanced header with animations
def render_header():
    st.markdown("""
    <div class="main-header fade-in">
        <h1 class="main-title">🐛 Bugs.qa</h1>
        <p class="main-subtitle">Advanced AI-Powered Bug Analysis & Solution Platform</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced sidebar with more features
def render_sidebar():
    with st.sidebar:
        st.markdown("### 📊 Real-time Analytics")
        
        # Enhanced stats with progress bars
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-card slide-in-left">
                <p class="stat-number">{st.session_state.total_bugs_solved}</p>
                <p class="stat-label">Bugs Solved</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            satisfaction_rate = st.session_state.user_satisfaction
            st.markdown(f"""
            <div class="stat-card slide-in-right">
                <p class="stat-number">{satisfaction_rate:.0f}%</p>
                <p class="stat-label">Success Rate</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Success rate progress bar
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {satisfaction_rate}%"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Enhanced feature list
        st.markdown("""
        ### 🚀 Advanced Features
        - **🔍 Smart Bug Detection**: AI-powered error analysis
        - **📱 Multi-format Support**: Text, Images, Code files
        - **🎨 Error Visualization**: Interactive charts and graphs
        - **💡 Solution Generator**: Auto-generate fixed code
        - **🔧 Code Diff Viewer**: Before/after comparisons
        - **📈 Pattern Analysis**: Identify recurring issues
        - **🌐 Multi-language Support**: 20+ programming languages
        - **📋 Export & Share**: Generate detailed reports
        - **🎯 Smart Suggestions**: Proactive improvement tips
        """)
        
        st.markdown("---")
        
        # Enhanced filters
        st.markdown("### 🎯 Bug Configuration")
        
        severity = st.selectbox(
            "🚨 Bug Severity:",
            ["🟢 Low", "🟡 Medium", "🟠 High", "🔴 Critical"],
            index=1,
            help="Select the severity level of your bug"
        )
        
        language = st.selectbox(
            "💻 Language/Framework:",
            ["🤖 Auto-detect", "🐍 Python", "⚡ JavaScript", "☕ Java", "⚙️ C++", 
             "🔷 C#", "🚀 Go", "🦀 Rust", "🐘 PHP", "💎 Ruby", "⚛️ React", 
             "📱 Flutter", "🍃 Node.js", "🌐 HTML/CSS", "📊 SQL", "🔧 Other"],
            index=0,
            help="Choose your programming language for better analysis"
        )
        
        complexity = st.radio(
            "🎓 Code Complexity:",
            ["Beginner", "Intermediate", "Advanced"],
            index=1,
            help="Select your coding experience level"
        )
        
        analysis_depth = st.slider(
            "🔬 Analysis Depth:",
            min_value=1,
            max_value=5,
            value=3,
            help="1=Quick Fix, 5=Deep Analysis"
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Clear History", help="Clear all bug history"):
            st.session_state.bug_history = []
            st.session_state.total_bugs_solved = 0
            st.success("History cleared!")
        
        if st.button("📊 Generate Report", help="Export comprehensive report"):
            generate_bug_report()
        
        return severity.split(' ')[1], language.split(' ')[1], complexity, analysis_depth

# Enhanced bug analysis with visualization
def analyze_bug_advanced(client, bug_input, input_type, severity, language, complexity, analysis_depth):
    try:
        base_prompt = f"""
        You are an advanced software debugging AI assistant with expertise in multiple programming languages and frameworks.
        
        **Context:**
        - Bug Severity: {severity}
        - Programming Language/Framework: {language}
        - Code Complexity Level: {complexity}
        - Analysis Depth: {analysis_depth}/5
        
        **Bug Input Type:** {input_type}
        """
        
        if input_type == "text":
            detailed_prompt = base_prompt + f"""
            
            **Bug Description/Error:**
            ```
            {bug_input}
            ```
            
            **Required Analysis (Depth Level {analysis_depth}):**
            
            ## 🔍 **IMMEDIATE DIAGNOSIS**
            Provide a quick summary of what's wrong.
            
            ## 🎯 **ROOT CAUSE ANALYSIS**
            Identify the exact cause with detailed explanation.
            
            ## 💡 **STEP-BY-STEP SOLUTION**
            1. Immediate fix steps
            2. Implementation details
            3. Testing approach
            
            ## 👨‍💻 **CORRECTED CODE**
            Provide the complete, error-free code with explanations:
            ```{language.lower()}
            // Your fixed code here
            ```
            
            ## 🔧 **CODE IMPROVEMENTS**
            Suggest optimizations and best practices.
            
            ## 🛡️ **PREVENTION STRATEGIES**
            How to avoid this issue in the future.
            
            ## ⚡ **ALTERNATIVE SOLUTIONS**
            Provide 2-3 different approaches to solve this.
            
            ## 🧪 **TESTING RECOMMENDATIONS**
            - Unit tests to write
            - Edge cases to consider
            - Validation steps
            
            ## 📊 **PERFORMANCE IMPACT**
            Analyze if the fix affects performance.
            
            ## 🔗 **RELATED ISSUES**
            Common related problems to watch for.
            
            Please format your response with clear headers and provide practical, actionable solutions.
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=detailed_prompt
            )
            
        else:  # image input
            image_prompt = base_prompt + f"""
            
            **Instructions for Image Analysis:**
            Please analyze this screenshot/image of a bug/error and provide comprehensive debugging assistance.
            
            **Required Analysis:**
            
            ## 👁️ **VISUAL ANALYSIS**
            Describe exactly what you see in the image.
            
            ## 🔍 **ERROR IDENTIFICATION**
            Identify the specific error or issue shown.
            
            ## 🎯 **ROOT CAUSE ANALYSIS**
            Explain why this error is occurring.
            
            ## 💡 **COMPLETE SOLUTION**
            Provide step-by-step fix instructions.
            
            ## 👨‍💻 **CORRECTED CODE**
            Write the complete, error-free code:
            ```{language.lower()}
            // Your fixed code here
            ```
            
            ## 🔧 **IMPROVEMENTS & OPTIMIZATIONS**
            Suggest enhancements to the code.
            
            ## 🛡️ **PREVENTION TIPS**
            How to avoid this issue going forward.
            
            ## 🧪 **TESTING STRATEGY**
            Recommend testing approaches.
            
            Be specific and provide complete, working solutions.
            """
            
            # Upload image to Gemini
            uploaded_file = client.files.upload(file=bug_input)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[uploaded_file, image_prompt]
            )
        
        return response.text
    
    except Exception as e:
        return f"❌ **Analysis Error:** {str(e)}\n\nPlease check your input and try again."

# Code diff viewer
def display_code_diff(original_code, fixed_code, language="python"):
    st.markdown("### 🔄 Code Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ❌ Original Code (with bugs)")
        st.code(original_code, language=language)
    
    with col2:
        st.markdown("#### ✅ Fixed Code")
        st.code(fixed_code, language=language)

# Error visualization function
def create_error_visualizations():
    if not st.session_state.bug_history:
        st.info("📊 No data available yet. Analyze some bugs to see visualizations!")
        return
    
    st.markdown("### 📊 Bug Analytics Dashboard")
    
    # Prepare data
    df = pd.DataFrame(st.session_state.bug_history)
    
    # Create multiple visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Bug severity distribution
        severity_counts = df['severity'].value_counts()
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="🎯 Bug Severity Distribution",
            color_discrete_sequence=['#10b981', '#f59e0b', '#f97316', '#ef4444']
        )
        fig_severity.update_layout(
            font=dict(size=12),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # Language distribution
        language_counts = df['language'].value_counts()
        fig_lang = px.bar(
            x=language_counts.index,
            y=language_counts.values,
            title="💻 Languages with Most Bugs",
            color=language_counts.values,
            color_continuous_scale="viridis"
        )
        fig_lang.update_layout(
            xaxis_title="Programming Language",
            yaxis_title="Number of Bugs",
            height=400
        )
        st.plotly_chart(fig_lang, use_container_width=True)
    
    # Timeline analysis
    if len(df) > 1:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_bugs = df.groupby('date').size().reset_index(name='count')
        
        fig_timeline = px.line(
            daily_bugs,
            x='date',
            y='count',
            title="📈 Bug Reporting Timeline",
            markers=True
        )
        fig_timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Bugs",
            height=300
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Bug pattern analysis
    st.markdown("### 🔍 Error Pattern Analysis")
    
    # Extract common error patterns
    error_patterns = {}
    for bug in st.session_state.bug_history:
        # Simple pattern extraction (can be enhanced)
        words = bug['input'].lower().split()
        for word in words:
            if any(keyword in word for keyword in ['error', 'exception', 'failed', 'undefined', 'null']):
                error_patterns[word] = error_patterns.get(word, 0) + 1
    
    if error_patterns:
        # Top error patterns
        sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig_patterns = px.bar(
            x=[pattern[1] for pattern in sorted_patterns],
            y=[pattern[0] for pattern in sorted_patterns],
            orientation='h',
            title="🎯 Most Common Error Patterns",
            color=[pattern[1] for pattern in sorted_patterns],
            color_continuous_scale="reds"
        )
        fig_patterns.update_layout(
            xaxis_title="Frequency",
            yaxis_title="Error Pattern",
            height=400
        )
        st.plotly_chart(fig_patterns, use_container_width=True)

# Enhanced bug input section
def render_enhanced_bug_input(client, severity, language, complexity, analysis_depth):
    st.markdown("""
    <div class="feature-card fade-in">
        <h3>🔍 Advanced Bug Analysis Center</h3>
        <p>Upload your bug details in any format - code snippets, error messages, or screenshots for comprehensive AI-powered analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced input tabs
    tab1, tab2, tab3 = st.tabs(["📝 Text/Code Input", "🖼️ Image Upload", "📂 File Upload"])
    
    with tab1:
        st.markdown("""
        <div class="feature-card">
            <h4>📝 Enter Bug Details</h4>
            <p>Paste your error message, stack trace, or code snippet below for analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        bug_text = st.text_area(
            "Paste your bug details here:",
            placeholder="""Example:
Error: TypeError: undefined is not a function
Stack trace:
    at main.js:42:15
    at init (main.js:38:5)""",
            height=200,
            help="Paste your error message, stack trace, or problematic code"
        )
        
        if st.button("🔍 Analyze Text Bug", key="analyze_text"):
            if bug_text.strip():
                with st.spinner("🧠 Analyzing bug with AI..."):
                    analysis_result = analyze_bug_advanced(
                        client, 
                        bug_text, 
                        "text", 
                        severity, 
                        language, 
                        complexity, 
                        analysis_depth
                    )
                    
                    # Store in history
                    bug_entry = {
                        "input": bug_text,
                        "result": analysis_result,
                        "severity": severity,
                        "language": language,
                        "complexity": complexity,
                        "timestamp": datetime.now().isoformat(),
                        "type": "text"
                    }
                    st.session_state.bug_history.append(bug_entry)
                    st.session_state.total_bugs_solved += 1
                    
                    # Display results
                    st.markdown("## 🎯 Analysis Results")
                    st.markdown(f"<div class='solution-box'>{analysis_result}</div>", unsafe_allow_html=True)
                    
                    # Try to extract code blocks for diff view
                    code_blocks = re.findall(r'```.*?\n(.*?)\n```', analysis_result, re.DOTALL)
                    if len(code_blocks) >= 2:
                        display_code_diff(code_blocks[0], code_blocks[1], language.lower())
            else:
                st.warning("Please enter some bug details to analyze")

    with tab2:
        st.markdown("""
        <div class="feature-card">
            <h4>🖼️ Upload Screenshot</h4>
            <p>Upload an image/screenshot of your error for visual analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_image = st.file_uploader(
            "Choose an image file (PNG, JPG, JPEG):",
            type=["png", "jpg", "jpeg"],
            key="image_uploader"
        )
        
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Bug Screenshot", use_column_width=True)
            
            if st.button("🔍 Analyze Image Bug", key="analyze_image"):
                with st.spinner("👁️ Analyzing image with computer vision..."):
                    try:
                        # Convert to bytes for Gemini
                        image_bytes = uploaded_image.getvalue()
                        
                        analysis_result = analyze_bug_advanced(
                            client, 
                            image_bytes, 
                            "image", 
                            severity, 
                            language, 
                            complexity, 
                            analysis_depth
                        )
                        
                        # Store in history
                        bug_entry = {
                            "input": "Image upload",
                            "result": analysis_result,
                            "severity": severity,
                            "language": language,
                            "complexity": complexity,
                            "timestamp": datetime.now().isoformat(),
                            "type": "image"
                        }
                        st.session_state.bug_history.append(bug_entry)
                        st.session_state.total_bugs_solved += 1
                        
                        # Display results
                        st.markdown("## 🎯 Analysis Results")
                        st.markdown(f"<div class='solution-box'>{analysis_result}</div>", unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Image analysis failed: {str(e)}")

    with tab3:
        st.markdown("""
        <div class="feature-card">
            <h4>📂 Upload Code File</h4>
            <p>Upload your source code file for comprehensive analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a code file:",
            type=["py", "js", "java", "cpp", "c", "cs", "go", "rs", "php", "rb", "html", "css"],
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            file_contents = uploaded_file.getvalue().decode("utf-8")
            
            st.markdown("#### 📄 File Contents Preview")
            st.code(file_contents, language=language.lower())
            
            if st.button("🔍 Analyze Code File", key="analyze_file"):
                with st.spinner("🔎 Analyzing code file..."):
                    analysis_result = analyze_bug_advanced(
                        client, 
                        file_contents, 
                        "text", 
                        severity, 
                        language, 
                        complexity, 
                        analysis_depth
                    )
                    
                    # Store in history
                    bug_entry = {
                        "input": f"File: {uploaded_file.name}",
                        "result": analysis_result,
                        "severity": severity,
                        "language": language,
                        "complexity": complexity,
                        "timestamp": datetime.now().isoformat(),
                        "type": "file"
                    }
                    st.session_state.bug_history.append(bug_entry)
                    st.session_state.total_bugs_solved += 1
                    
                    # Display results
                    st.markdown("## 🎯 Analysis Results")
                    st.markdown(f"<div class='solution-box'>{analysis_result}</div>", unsafe_allow_html=True)

# Generate comprehensive bug report
def generate_bug_report():
    if not st.session_state.bug_history:
        st.warning("No bug history to generate report from")
        return
    
    # Create report content
    report_content = f"""
    # 🐛 Bugs.qa Analysis Report
    **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    **Total Bugs Analyzed:** {len(st.session_state.bug_history)}
    
    ## 📊 Summary Statistics
    - **Success Rate:** {st.session_state.user_satisfaction}%
    - **Most Common Language:** {max(set(b['language'] for b in st.session_state.bug_history), key=lambda x: list(b['language'] for b in st.session_state.bug_history).count(x))}
    - **Average Severity:** {sum(1 if b['severity'] == 'Low' else 2 if b['severity'] == 'Medium' else 3 if b['severity'] == 'High' else 4 for b in st.session_state.bug_history) / len(st.session_state.bug_history):.1f}
    
    ## 🏆 Top Bug Patterns
    """
    
    # Add bug details
    for i, bug in enumerate(st.session_state.bug_history, 1):
        report_content += f"""
        ### 🐞 Bug #{i}
        - **Type:** {bug['type']}
        - **Language:** {bug['language']}
        - **Severity:** {bug['severity']}
        - **Date:** {bug['timestamp']}
        
        **Input:**
        ```
        {bug['input'][:500]}{'...' if len(bug['input']) > 500 else ''}
        ```
        
        **Solution Summary:**
        {bug['result'].split('##')[0][:300]}...
        """
    
    # Create download link
    report_hash = hashlib.md5(report_content.encode()).hexdigest()[:8]
    filename = f"bug_report_{report_hash}.md"
    
    st.markdown("### 📤 Export Report")
    st.download_button(
        label="⬇️ Download Full Report",
        data=report_content,
        file_name=filename,
        mime="text/markdown"
    )

# Main app function
def main():
    # Initialize everything
    load_custom_css()
    init_session_state()
    client = init_genai_client()
    
    if client is None:
        st.error("Failed to initialize AI client. Please check your API key.")
        return
    
    # Render UI components
    render_header()
    severity, language, complexity, analysis_depth = render_sidebar()
    
    # Main content area
    render_enhanced_bug_input(client, severity, language, complexity, analysis_depth)
    
    # Show history and analytics if available
    if st.session_state.bug_history:
        st.markdown("## 📜 Bug Analysis History")
        
        with st.expander("View Recent Bug Analyses", expanded=False):
            for i, bug in enumerate(reversed(st.session_state.bug_history[-5:]), 1):
                st.markdown(f"""
                <div class="feature-card">
                    <h4>🐛 Bug #{len(st.session_state.bug_history)-i+1} - {bug['severity']} severity in {bug['language']}</h4>
                    <p><small>{bug['timestamp']}</small></p>
                    <details>
                        <summary>View Details</summary>
                        <div class="solution-box">
                            {bug['result']}
                        </div>
                    </details>
                </div>
                """, unsafe_allow_html=True)
        
        create_error_visualizations()

if __name__ == "__main__":
    main()
