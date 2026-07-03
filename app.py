import streamlit as st
from google import genai
from google.genai import types
import os

# ==========================================
# 1. PAGE CONFIGURATION & APP THEMING
# ==========================================
st.set_page_config(
    page_title="Academic AI Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling injected to create a WhatsApp-like thread look
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
    .chat-bubble-user {
        background-color: #0b554a;
        padding: 12px;
        border-radius: 10px 10px 0px 10px;
        margin: 10px 0px;
        max-width: 85%;
        margin-left: auto;
        color: white;
    }
    .chat-bubble-ai {
        background-color: #202124;
        padding: 12px;
        border-radius: 10px 10px 10px 0px;
        margin: 10px 0px;
        max-width: 85%;
        margin-right: auto;
        color: #e3e3e3;
        border: 1px solid #3c4043;
    }
    .feature-card {
        background-color: #232329;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

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
""", unsafe_allow_html=True)

# ==========================================
# 3. BACKEND AUTHENTICATION & STATE SETUP
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
client_ready = False

if not api_key:
    st.error("🔑 API Key Configuration Missing!")
    st.info("Please open 'Manage app' -> 'Advanced Settings' -> 'Secrets' and set your key as: GEMINI_API_KEY = 'your_key'")
else:
    try:
        client = genai.Client(api_key=api_key)
        client_ready = True
    except Exception as e:
        st.error(f"Failed to initialize backend processing core: {e}")

# Initialize persistent chat history container if it doesn't exist yet
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# 4. APPLICATION TABS SETUP
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Step-by-Step Chat Solver", 
    "📝 Quick Revision Notes", 
    "📐 Formula Reference", 
    "🧠 Brain Booster Flashcards"
])

# ------------------------------------------
# TAB 1: STEP-BY-STEP SOLVER (UNIFIED WHATSAPP INPUT)
# ------------------------------------------
with tab1:
    st.header("Interactive Tutor Chat")
    st.write("Type a query or upload images/PDF worksheets directly inside the conversation box below.")

    # Chat Log View Engine (Displays continuous message threads)
    st.write("---")
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # Unified Workspace Input Console
    with st.form(key="unified_chat_form", clear_on_submit=True):
        user_query = st.text_input(
            label="Type your academic question:",
            placeholder="Type your question here...",
            key="chat_message_field"
        )
        
        uploaded_files = st.file_uploader(
            label="Attach files to your question (Optional Images or PDFs):",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="academic_media_uploader"
        )
        
        submit_btn = st.form_submit_button(label="Send to Tutor")

    # Processing Input Actions
    if submit_btn:
        if not client_ready:
            st.error("AI service is offline. Please configure a valid API Key.")
        elif not user_query.strip() and not uploaded_files:
            st.warning("Please enter a question or upload a document first.")
        else:
            contents_payload = []
            display_text = user_query if user_query.strip() else "[Sent Attachment File]"

            if uploaded_files:
                for f in uploaded_files:
                    file_bytes = f.read()
                    mime_type = f.type
                    contents_payload.append(
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    )
                display_text += f" (+{len(uploaded_files)} attachment files)"

            # Append input entry locally
            st.session_state.chat_history.append({"role": "user", "text": display_text})

            if user_query.strip():
                contents_payload.append(user_query)

            with st.spinner("Tutor is calculating solution steps..."):
                try:
                    # Provide continuous thread context coaching structure
                    history_context = "You are an expert high school tutor assistant. Review the history context window if needed:\n"
                    for past_msg in st.session_state.chat_history[-6:]:
                        history_context += f"{past_msg['role']}: {past_msg['text']}\n"
                    
                    contents_payload.insert(0, history_context)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload
                    )
                    
                    st.session_state.chat_history.append({"role": "model", "text": response.text})
                    st.rerun()

                except Exception as api_err:
                    st.error("The calculation core encountered an error analyzing this query.")
                    st.code(f"Diagnostic Log: {api_err}")

    if st.button("Clear Chat History", key="clear_session_trigger"):
        st.session_state.chat_history = []
        st.rerun()

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
        """, unsafe_allow_html=True)
        
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
        """, unsafe_allow_html=True)

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
st.caption("✨ Academic AI Assistant Engine Running Multi-Modal Persistent Architecture.")
