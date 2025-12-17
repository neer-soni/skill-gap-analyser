"""
SkillBridge - AI-Powered Career Gap Analyzer
Production-ready Streamlit application with Google Gemini AI
"""

import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io
import json
import time

# ===== CONFIGURATION =====
# Add your Gemini API key here
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key="AIzaSyCY0gdA1Wz7AN8VGfGrDtBR7-YkBgHl9DE")

# Page Configuration
st.set_page_config(
    page_title="SkillBridge - Career Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Dark Mode SaaS Theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0f172a;
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Input Fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(to right, #3b82f6, #10b981) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* Cards */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background-color: #3b82f6;
    }
    
    /* File Uploader */
    .uploadedFile {
        background-color: #1e293b !important;
        border: 2px dashed #334155 !important;
        border-radius: 8px !important;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning {
        border-radius: 8px !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    
    /* Journey Timeline */
    .timeline-item {
        background-color: #1e293b;
        border-left: 3px solid #3b82f6;
        padding: 16px;
        margin: 12px 0;
        border-radius: 8px;
    }
    
    .timeline-item:hover {
        background-color: #334155;
        border-left-color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'results' not in st.session_state:
    st.session_state.results = None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_image(image_file):
    """Extract text from uploaded image using OCR"""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error reading image: {str(e)}")
        return None

def analyze_with_gemini(resume_text, target_role):
    """
    Use Google Gemini AI to analyze resume and provide gap analysis
    with real market insights
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are an expert career analyst and tech recruiter with deep knowledge of current job markets.

TASK: Analyze this resume for the target role: "{target_role}"

RESUME:
{resume_text[:5000]}

Provide a comprehensive analysis in STRICT JSON format with these exact keys:

{{
  "match_score": <number 0-100>,
  "current_level": "<Junior/Mid-Level/Senior>",
  "target_level": "<level for the target role>",
  "market_insights": [
    "• 85% of {target_role} roles require skill X",
    "• Growing demand: Y skill (+40% in 2024)",
    "• 70% of companies now expect Z"
  ],
  "strengths": [
    "React expertise",
    "Strong problem-solving"
  ],
  "critical_gaps": [
    "Node.js backend (required by 90% of full-stack roles)",
    "Docker/K8s (used by 75% of companies)"
  ],
  "roadmap": [
    {{
      "week": 1,
      "title": "Node.js Fundamentals",
      "focus": "Event loop, async/await, streams",
      "type": "Code",
      "priority": "Critical"
    }},
    {{
      "week": 2,
      "title": "Express.js & REST APIs",
      "focus": "Routing, middleware, authentication",
      "type": "Architecture",
      "priority": "High"
    }},
    {{
      "week": 3,
      "title": "Database Mastery",
      "focus": "MongoDB, PostgreSQL, ORM patterns",
      "type": "Database",
      "priority": "High"
    }},
    {{
      "week": 4,
      "title": "DevOps Essentials",
      "focus": "Docker, CI/CD, AWS basics",
      "type": "Infrastructure",
      "priority": "Medium"
    }}
  ]
}}

CRITICAL RULES:
1. Use REAL current market data and percentages (2024-2025)
2. Be brutally honest about gaps
3. Keep ALL text in bullet points (•) or short phrases
4. NO paragraphs, NO long sentences
5. Market insights must include actual percentages
6. Roadmap must be 4 weeks exactly
7. Return ONLY valid JSON, nothing else
8. Ensure all strings are properly escaped"""

        response = model.generate_content(prompt)
        response_text = response.text
        
        # Clean and parse JSON
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        response_text = response_text.strip()
        
        # Find JSON object
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        results = json.loads(json_str)
        return results
        
    except json.JSONDecodeError as e:
        st.error(f"AI returned invalid format. Please try again. Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None

def display_hero():
    """Display hero section with input form"""
    st.markdown("<h1 style='text-align: center; font-size: 56px; background: linear-gradient(to right, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Don't Guess Your Career Path. Engineer It.</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-size: 20px; color: #94a3b8; margin-bottom: 48px;'>Upload your resume, pick your dream role, and get a 30-day survival plan.</p>", unsafe_allow_html=True)
    
    # Center column
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎯 Target Role")
        target_role = st.text_input(
            "",
            placeholder="e.g., Senior Full Stack Developer, ML Engineer",
            label_visibility="collapsed"
        )
        
        st.markdown("### 📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose PDF, PNG, or TXT file",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
            label_visibility="collapsed"
        )
        
        # Process uploaded file
        resume_text = ""
        if uploaded_file:
            file_type = uploaded_file.type
            
            with st.spinner("📖 Extracting text..."):
                if 'pdf' in file_type:
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif 'image' in file_type:
                    resume_text = extract_text_from_image(uploaded_file)
                elif 'text' in file_type:
                    resume_text = uploaded_file.read().decode('utf-8')
            
            if resume_text:
                st.success(f"✅ Extracted {len(resume_text)} characters")
                with st.expander("Preview extracted text"):
                    st.text_area("", resume_text[:500] + "...", height=150, disabled=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Analyze Button
        if st.button("🚀 Analyze Now", use_container_width=True):
            if not target_role:
                st.error("⚠️ Please enter a target role")
            elif not resume_text:
                st.error("⚠️ Please upload your resume")
            else:
                with st.spinner("🤖 AI is analyzing your career path..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.03)
                        progress_bar.progress(i + 1)
                    
                    results = analyze_with_gemini(resume_text, target_role)
                    
                    if results:
                        st.session_state.results = results
                        st.session_state.analyzed = True
                        st.rerun()

def display_results(results):
    """Display analysis results dashboard"""
    
    # Header
    st.markdown("<h2 style='text-align: center; font-size: 42px;'>🎯 Your Career Intelligence Report</h2>", unsafe_allow_html=True)
    
    if st.button("← New Analysis"):
        st.session_state.analyzed = False
        st.session_state.results = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Three column layout
    col1, col2, col3 = st.columns([1, 1, 1.5])
    
    # Column 1: Scorecard
    with col1:
        st.markdown("### 📊 The Scorecard")
        
        score = results['match_score']
        st.markdown(f"""
        <div style='text-align: center; padding: 32px; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155;'>
            <div style='font-size: 64px; font-weight: bold; color: #3b82f6;'>{score}%</div>
            <div style='color: #94a3b8; margin-top: 8px;'>Match Score</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #1e293b; padding: 16px; border-radius: 8px; margin: 8px 0; border: 1px solid #334155;'>
            <div style='color: #94a3b8; font-size: 14px;'>Current Level</div>
            <div style='color: #3b82f6; font-weight: bold; font-size: 18px; margin-top: 4px;'>{results['current_level']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #1e293b; padding: 16px; border-radius: 8px; margin: 8px 0; border: 1px solid #334155;'>
            <div style='color: #94a3b8; font-size: 14px;'>Target Level</div>
            <div style='color: #10b981; font-weight: bold; font-size: 18px; margin-top: 4px;'>{results['target_level']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Column 2: Reality Check
    with col2:
        st.markdown("### 🎯 The Reality Check")
        
        st.markdown("#### ✅ What You Have")
        for strength in results['strengths']:
            st.markdown(f"<div style='color: #10b981; padding: 8px 0;'>• {strength}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### ⚠️ Critical Gaps")
        for gap in results['critical_gaps']:
            st.markdown(f"<div style='color: #ef4444; padding: 8px 0;'>• {gap}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("#### 📈 Market Insights")
        for insight in results['market_insights']:
            st.markdown(f"<div style='color: #60a5fa; padding: 8px 0;'>{insight}</div>", unsafe_allow_html=True)
    
    # Column 3: 4-Week Journey
    with col3:
        st.markdown("### 🚀 Your 4-Week Sprint")
        
        icons = {
            "Code": "💻",
            "Architecture": "🏗️",
            "Database": "🗄️",
            "Infrastructure": "☁️",
            "Project": "🎯"
        }
        
        priority_colors = {
            "Critical": "#ef4444",
            "High": "#f59e0b",
            "Medium": "#3b82f6"
        }
        
        for week_data in results['roadmap']:
            icon = icons.get(week_data['type'], "📚")
            priority_color = priority_colors.get(week_data.get('priority', 'Medium'), "#3b82f6")
            
            st.markdown(f"""
            <div class='timeline-item'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span style='color: #3b82f6; font-weight: bold; font-size: 12px;'>WEEK {week_data['week']}</span>
                    <span style='background-color: #334155; padding: 4px 12px; border-radius: 12px; font-size: 11px; color: #94a3b8;'>{week_data['type']}</span>
                </div>
                <div style='font-size: 20px; font-weight: bold; margin-bottom: 8px;'>{icon} {week_data['title']}</div>
                <div style='color: #94a3b8; font-size: 14px; margin-bottom: 8px;'>• {week_data['focus']}</div>
                <div style='display: inline-block; background-color: {priority_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;'>
                    {week_data.get('priority', 'Medium')} Priority
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main application flow"""
    
    if not st.session_state.analyzed:
        display_hero()
    else:
        display_results(st.session_state.results)

if __name__ == "__main__":
    main()