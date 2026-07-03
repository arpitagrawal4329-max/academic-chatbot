import streamlit as st
from google import genai
from google.genai import types
import os
import uuid

# ==========================================
# 1. PAGE CONFIGURATION & APP THEMING
# ==========================================
st.set_page_config(
    page_title="Academic AI Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"  # Forces side menu bar open initially
)

# Custom CSS styling for WhatsApp bubbles, side menus, and fixing text field collision overlaps
st.markdown("""
    <style>
    .main {
        background-color: #131314;
        color: #e3e3e3;
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
    /* Fixed overlapping styling for compact custom layouts */
    div[data-testid="stTextInput"] label {
        display: none !important;
    }
    .stButton>button {
        background-color: #4b6cb7;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        height: 42px;
        width: 100%;
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
# 3. BACKEND AUTHENTICATION SETUP
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
client_ready = False

if not api_key:
    st.error("🔑 API Key Configuration Missing!")
    st.info("Please configure GEMINI_API_KEY in the Streamlit Advanced Settings -> Secrets drawer.")
else:
    try:
        client = genai.Client(api_key=api_key)
        client_ready = True
    except Exception as e:
        st.error(f"Failed to initialize backend processing core: {e}")

# ==========================================
# 4. SESSION STATE SESSION MANAGER (SIDEBAR CHATS)
# ==========================================
# Master library dict storing all distinct chat logs
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

# Tracks which session ID is active right now
if "active_chat_id" not in st.session_state:
    # Initialize a clean first chat session tracking parameter automatically
    first_id = str(uuid.uuid4())
    st.session_state.all_chats[first_id] = {
        "title": "Chat 1: Physics/Math Session",
        "history": []
    }
    st.session_state.active_chat_id = first_id

# ==========================================
# 5. SIDEBAR NAVIGATION MENU (PAST CHATS BAR)
# ==========================================
with st.sidebar:
    st.title("💬 Chat Sessions Menu")
    
    # Action Button: Start a completely brand new chat window thread
    if st.button("➕ Start New Separate Chat", key="new_chat_btn_sidebar"):
        new_id = str(uuid.uuid4())
        chat_num = len(st.session_state.all_chats) + 1
        st.session_state.all_chats[new_id] = {
            "title": f"Chat {chat_num}: Dynamic Session",
            "history": []
        }
        st.session_state.active_chat_id = new_id
        st.rerun()
        
    st.markdown("---")
    st.subheader("Your Past Conversations:")
    
    # Display lists of selectable conversation threads
    for chat_id, chat_data in list(st.session_state.all_chats.items()):
        # Highlights current active selection dynamically
        button_label = f"📁 {chat_data['title']}"
        if chat_id == st.session_state.active_chat_id:
            button_label = f"🔥 Active: {chat_data['title']}"
            
        if st.button(button_label, key=f"select_session_{chat_id}"):
            st.session_state.active_chat_id = chat_id
            st.rerun()
            
    st.markdown("---")
    # Clean up operations shifted completely here into side menu drawer area
    if st.button("🗑️ Wipe Active Chat History", key="clear_active_history_btn"):
        st.session_state.all_chats[st.session_state.active_chat_id]["history"] = []
        st.rerun()

# Extract active current session profile tracking values dynamically
current_session = st.session_state.all_chats[st.session_state.active_chat_id]

# ==========================================
# 6. APPLICATION MAIN INTERFACE TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Step-by-Step Chat Solver", 
    "📝 Quick Revision Notes", 
    "📐 Formula Reference", 
    "🧠 Brain Booster Flashcards"
])

# ------------------------------------------
# TAB 1: TUTOR SOLVER (COMPACT NO-OVERLAP INPUT)
# ------------------------------------------
with tab1:
    st.subheader(f"Active Session: {current_session['title']}")
    st.write("Type a query or upload elements inside the optimized horizontal layout below.")

    # Chat Log View Engine (Tied entirely to selected current_session dictionary)
    st.write("---")
    if not current_session["history"]:
        st.caption("Conversation is clear. Send a query below to prompt step-by-step breakdown explanations.")
    else:
        for chat in current_session["history"]:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # Compact Input Panel Layout (Columns aligned horizontally)
    col_text, col_file, col_btn = st.columns([5, 4, 1])

    with col_text:
        user_query = st.text_input(
            label="HiddenLabelTextFix",
            placeholder="Ask your query here...",
            key="chat_message_field"
        )
        
    with col_file:
        uploaded_files = st.file_uploader(
            label="HiddenLabelFileFix",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="academic_media_uploader"
        )
        
    with col_btn:
        submit_btn = st.button("➔", key="send_arrow_btn")

    # Dynamic Multimodal Evaluation Sequence
    if submit_btn:
        has_text = bool(user_query.strip())
        has_files = bool(uploaded_files)

        if not client_ready:
            st.error("AI service offline. Provide functional secret key validations.")
        elif not has_text and not has_files:
            st.warning("Please type text or attach content maps first.")
        else:
            contents_payload = []
            
            # Pass contextual thread references to avoid losing previous answers
            history_context = "You are an expert high school tutor assistant. Review the history context window if needed:\n"
            for past_msg in current_session["history"][-6:]:
                history_context += f"{past_msg['role']}: {past_msg['text']}\n"
            contents_payload.append(history_context)

            # Format text titles to register into historical log states elegantly
            if has_text and has_files:
                display_log_text = f"{user_query} <i>(+{len(uploaded_files)} document attachments)</i>"
            elif has_files:
                display_log_text = f"<i>[Sent {len(uploaded_files)} visual/document inputs for analysis]</i>"
            else:
                display_log_text = user_query

            # Append File Assets
            if has_files:
                for f in uploaded_files:
                    file_bytes = f.read()
                    mime_type = f.type
                    contents_payload.append(
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    )

            # Append Text Assets
            if has_text:
                contents_payload.append(user_query)
            else:
                contents_payload.append("Analyze the attached image/document page completely and provide a structural solution.")

            # Append values permanently to active profile map
            current_session["history"].append({"role": "user", "text": display_log_text})

            with st.spinner("Tutor is calculating solutions..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload
                    )
                    
                    # Update active session with model response
                    current_session["history"].append({"role": "model", "text": response.text})
                    
                    # If this was a fresh text session, rename title automatically based on question snippet
                    if len(current_session["history"]) <= 2 and has_text:
                        current_session["title"] = user_query[:22] + "..."
                        
                    st.rerun()

                except Exception as api_err:
                    st.error("The calculation core encountered an error responding.")
                    st.code(f"Diagnostic Error Data: {api_err}")

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
        """, unsafe_allow_html=True)
        
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
# 7. FOOTER ARCHITECTURE
# ==========================================
st.markdown("---")
st.caption("✨ Academic AI Assistant Engine Running Multi-Session Custom Chat Core.")
