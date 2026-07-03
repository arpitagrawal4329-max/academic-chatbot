import streamlit as st
from google import genai
import os
import json

# ==========================================
# 1. PAGE CONFIGURATION & APP THEMING
# ==========================================
st.set_page_config(
    page_title="Academic AI Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling injected to create a clean UI
st.markdown("""
    <style>
    .main {
        background-color: #131314;
        color: #e3e3e3;
    }
    .stButton>button {
        background-color: #4b6cb7;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #182848;
        color: white;
    }
    .credit-box {
        background-color: #1e1e24;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4b6cb7;
        margin-bottom: 25px;
    }
    .feature-card {
        background-color: #232329;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allowed_html=True)

# ==========================================
# 2. SCHOOL PROJECT CREDIT BANNER
# ==========================================
st.markdown("""
    <div class="credit-box">
        <h2 style='margin-top:0; color:#4b6cb7; font-size:24px;'>🎓 Academic AI Assistant</h2>
        <p style='margin-bottom:5px; font-size:14px;'><strong>Developed by:</strong> Harshit Agrawal & Umar Fahrukh</p>
        <p style='margin-bottom:5px; font-size:14px;'><strong>School:</strong> Acharya Tulsi Sarvodaya Bal Vidyalaya</p>
        <p style='margin-bottom:0; font-size:14px; color:#a0a0a0;'><strong>Guided by:</strong> Gopal Meena Sir</p>
    </div>
""", unsafe_allowed_html=True)

# ==========================================
# 3. BACKEND AUTHENTICATION SETUP
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
client_ready = False

if not api_key:
    st.error("🔑 API Key Configuration Missing!")
    st.info("Please open 'Manage app' -> 'Advanced Settings' -> 'Secrets' and set your key as: GEMINI_API_KEY = 'your_key'")
else:
    try:
        # Initializing the modern Google GenAI Client
        client = genai.Client(api_key=api_key)
        client_ready = True
    except Exception as e:
        st.error(f"Failed to initialize backend processing core: {e}")

# ==========================================
# 4. APPLICATION TABS SETUP
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Step-by-Step Solver", 
    "📝 Quick Revision Notes", 
    "📐 Formula Reference", 
    "🧠 Brain Booster Flashcards"
])

# ------------------------------------------
# TAB 1: STEP-BY-STEP SOLVER (MAIN CHATBOT)
# ------------------------------------------
with tab1:
    st.header("Ask Your Homework Query")
    st.write("Enter your science, math, or humanities questions below for a fully detailed, breakdown solution.")
    
    # Corrected text input string mapping with explicit visible labels to prevent line crashes
    user_query = st.text_input(
        label="Type your academic question below:", 
        placeholder="e.g., Solve the quadratic equation x^2 + 2x - 3 = 0 step by step.",
        key="main_solver_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_btn = st.button("Submit", key="solver_submit_trigger")
        
    if submit_btn or user_query:
        if not client_ready:
            st.error("AI service is currently offline. Please configure a valid API Key first.")
        elif not user_query.strip():
            st.warning("Please type a question before clicking the submit button.")
        else:
            with st.spinner("Processing query via background AI core..."):
                try:
                    # Construct structural prompt parameters for structured educational breakdown
                    structured_prompt = (
                        "You are an expert high school tutor assistant. Answer the following student "
                        "query with clear sections: 1. Core Concept, 2. Step-by-Step Mathematical/Logical "
                        f"Execution, and 3. Final Clear Answer. Student Query: {user_query}"
                    )
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=structured_prompt
                    )
                    
                    st.success("✨ Verified Solution:")
                    st.markdown(response.text)
                except Exception as api_err:
                    st.error("The AI core could not generate a response.")
                    st.info("Ensure your API Key is completely correct, hasn't expired, and starts with 'AIzaSy'.")
                    st.code(f"Error Diagnostic Log: {api_err}")

# ------------------------------------------
# TAB 2: QUICK REVISION NOTES GENERATOR
# ------------------------------------------
with tab2:
    st.header("Instant Summary Generator")
    st.write("Enter any complex topic or chapter title to automatically build structured revision summary points.")
    
    topic_input = st.text_input(
        label="Enter the chapter or topic name:", 
        placeholder="e.g., Electromagnetic Induction, Photosynthesis, Electrostatics",
        key="revision_notes_input"
    )
    
    generate_notes_btn = st.button("Generate Revision Guide", key="notes_submit_trigger")
    
    if generate_notes_btn or topic_input:
        if not client_ready:
            st.error("AI service is offline.")
        elif not topic_input.strip():
            st.warning("Please input a topic name.")
        else:
            with st.spinner("Compiling structural reference points..."):
                try:
                    notes_prompt = f"Create a high-yield summary revision guide on the academic topic: '{topic_input}'. Use clean bullet points, bold text highlighting critical definitions, and a short 'Keep in Mind' section."
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=notes_prompt
                    )
                    st.info(f"📚 Summary Overview: {topic_input}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error constructing revision notes: {e}")

# ------------------------------------------
# TAB 3: FORMULA QUICK REFERENCE CHEAT SHEET
# ------------------------------------------
with tab3:
    st.header("Formula Matrix")
    st.write("Select a target subject stream to load high-priority foundational equations.")
    
    subject_choice = st.selectbox(
        label="Choose target subject:",
        options=["Physics (Class 11/12 Core)", "Chemistry Physical Equations", "Mathematics Essentials"],
        key="subject_formula_selector"
    )
    
    if subject_choice == "Physics (Class 11/12 Core)":
        st.markdown("""
        <div class='feature-card'>
            <h4>🌌 Mechanics & Kinematics</h4>
            <ul>
                <li><strong>Equations of Motion:</strong> <code>v = u + at</code>, &nbsp; <code>s = ut + ½at²</code>, &nbsp; <code>v² = u² + 2as</code></li>
                <li><strong>Work-Energy Theorem:</strong> <code>W = ΔK = K_f - K_i</code></li>
                <li><strong>Universal Gravitation:</strong> <code>F = G*(m₁m₂)/r²</code></li>
            </ul>
        </div>
        <div class='feature-card'>
            <h4>⚡ Electrodynamics & Optics</h4>
            <ul>
                <li><strong>Coulomb's Law Force:</strong> <code>F = k*(q₁q₂)/r²</code></li>
                <li><strong>Ohm's Circuit Law:</strong> <code>V = I * R</code></li>
                <li><strong>Lens Maker Formula:</strong> <code>1/f = (μ - 1) * (1/R₁ - 1/R₂)</code></li>
            </ul>
        </div>
        """, unsafe_allowed_html=True)
        
    elif subject_choice == "Chemistry Physical Equations":
        st.markdown("""
        <div class='feature-card'>
            <h4>🧪 Thermodynamics & Gas Laws</h4>
            <ul>
                <li><strong>Ideal Gas Law State:</strong> <code>P * V = n * R * T</code></li>
                <li><strong>Gibbs Free Energy Criteria:</strong> <code>ΔG = ΔH - TΔS</code></li>
            </ul>
        </div>
        <div class='feature-card'>
            <h4>🔋 Electrochemistry & Kinetics</h4>
            <ul>
                <li><strong>Nernst Electrochemical Equation:</strong> <code>E = E° - (RT/nF) * ln(Q)</code></li>
                <li><strong>Arrhenius Activation Rate:</strong> <code>k = A * e^(-E_a / RT)</code></li>
            </ul>
        </div>
        """, unsafe_allowed_html=True)
        
    elif subject_choice == "Mathematics Essentials":
        st.markdown("""
        <div class='feature-card'>
            <h4>📐 Calculus & Algebra Matrix</h4>
            <ul>
                <li><strong>Quadratic Formula Roots:</strong> <code>x = [-b ± √(b² - 4ac)] / 2a</code></li>
                <li><strong>Fundamental Derivative:</strong> <code>d/dx(x^n) = n * x^(n-1)</code></li>
                <li><strong>Integration by Parts rule:</strong> <code>∫u dv = u*v - ∫v du</code></li>
            </ul>
        </div>
        """, unsafe_allowed_html=True)

# ------------------------------------------
# TAB 4: BRAIN BOOSTER FLASHCARDS
# ------------------------------------------
with tab4:
    st.header("Interactive Concept Flashcards")
    st.write("Toggle the boxes below to check your recall memory on tricky exam concepts.")
    
    with st.expander("❓ Question 1: What does Lenz's Law determine in electromagnetic physics?"):
        st.markdown("🎯 **Answer:** It states that the direction of the induced current always opposes the change in magnetic flux that produced it. (Obeys the Conservation of Energy).")
        
    with st.expander("❓ Question 2: Why do real gases deviate from Ideal Gas behavior?"):
        st.markdown("🎯 **Answer:** Real gases have actual intermolecular attractive forces between molecules, and their individual gas molecules occupy a finite, non-zero volume space.")
        
    with st.expander("❓ Question 3: What is geometric interpretation of a definite integral?"):
        st.markdown("🎯 **Answer:** It represents the net signed area bounded under the curve of a target function along a designated coordinate axis between the limits of integration.")

# ==========================================
# 5. FOOTER ARCHITECTURE
# ==========================================
st.markdown("---")
st.caption("✨ Academic AI Assistant Engine Running Streamlit Engine Core. Active Development Version.")
                  
