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
    initial_sidebar_state="expanded"
)

# Custom CSS to structure the clean Gemini-style input bar and toggle drawer
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
    /* Eliminates input field spacing collision errors entirely */
    div[data-testid="stTextInput"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"] {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
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
    .plus-btn>button {
        background-color: #2c2d31 !important;
        color: #e3e3e3 !important;
    }
    .sidebar-text {
        color: #9aa0a6;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 10px;
    }
    /* Styles the expanded attachment drawer panel */
    .drawer-container {
        background-color: #1e1e24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3c4043;
        margin-top: 5px;
        margin-bottom: 15px;
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
# 4. SESSION STATE MANAGER
# ==========================================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "active_chat_id" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.all_chats[first_id] = {
        "title": "New Problem Solving Session",
        "history": []
    }
    st.session_state.active_chat_id = first_id

# Track the layout visibility state of the attachment drawer panel
if "show_plus_menu" not in st.session_state:
    st.session_state.show_plus_menu = False

# ==========================================
# 5. SIDEBAR NAVIGATION MENU (RECENTS BAR STYLE)
# ==========================================
with st.sidebar:
    if st.button("➕ New Chat Session", key="new_chat_btn_sidebar"):
        new_id = str(uuid.uuid4())
        st.session_state.all_chats[new_id] = {
            "title": "New Problem Solving Session",
            "history": []
        }
        st.session_state.active_chat_id = new_id
        st.session_state.show_plus_menu = False
        st.rerun()
        
    st.markdown("---")
    st.markdown('<div class="sidebar-text">Recents</div>', unsafe_allow_html=True)
    
    for chat_id, chat_data in list(st.session_state.all_chats.items()):
        col_select, col_del = st.columns([5, 1])
        
        with col_select:
            truncated_title = chat_data['title'] if len(chat_data['title']) <= 25 else chat_data['title'][:22] + "..."
            btn_style = f"🔥 {truncated_title}" if chat_id == st.session_state.active_chat_id else truncated_title
            
            if st.button(btn_style, key=f"select_session_{chat_id}"):
                st.session_state.active_chat_id = chat_id
                st.session_state.show_plus_menu = False
                st.rerun()
                
        with col_del:
            if st.button("❌", key=f"delete_session_{chat_id}"):
                del st.session_state.all_chats[chat_id]
                if st.session_state.active_chat_id == chat_id:
                    remaining_ids = list(st.session_state.all_chats.keys())
                    if remaining_ids:
                        st.session_state.active_chat_id = remaining_ids[0]
                    else:
                        fallback_id = str(uuid.uuid4())
                        st.session_state.all_chats[fallback_id] = {
                            "title": "New Problem Solving Session",
                            "history": []
                        }
                        st.session_state.active_chat_id = fallback_id
                st.rerun()
                
    st.markdown("---")
    if st.button("🗑️ Clear Entire History", key="clear_all_global_history_btn"):
        st.session_state.all_chats = {}
        fallback_id = str(uuid.uuid4())
        st.session_state.all_chats[fallback_id] = {
            "title": "New Problem Solving Session",
            "history": []
        }
        st.session_state.active_chat_id = fallback_id
        st.session_state.show_plus_menu = False
        st.rerun()

current_session = st.session_state.all_chats.get(st.session_state.active_chat_id)

# ==========================================
# 6. APPLICATION MAIN INTERFACE TABS
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🔍 Question Solver", 
    "📐 Formula Reference", 
    "🧠 Brain Booster Flashcards"
])

# ------------------------------------------
# TAB 1: QUESTION SOLVER (COMPACT DYNAMIC DRAWER INTERFACE)
# ------------------------------------------
with tab1:
    st.subheader(f"Session Focus: {current_session['title']}")
    
    st.write("---")
    if not current_session["history"]:
        st.caption("No queries submitted yet. Use the action bar below to begin your study session.")
    else:
        for chat in current_session["history"]:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # Ultra-Compact Input Layout Line (Plus, Field Text, Arrow Send Button)
    col_plus, col_text, col_btn = st.columns([1, 8, 1])

    with col_plus:
        st.markdown('<div class="plus-btn">', unsafe_allowed_html=True)
        # Toggles layout visibility mapping switches
        toggle_drawer = st.button("＋", key="drawer_toggle_trigger")
        st.markdown('</div>', unsafe_allow_html=True)
        if toggle_drawer:
            st.session_state.show_plus_menu = not st.session_state.show_plus_menu
            st.rerun()

    with col_text:
        user_query = st.text_input(
            label="InputWorkspaceQueryField",
            placeholder="Ask your academic question here...",
            key="chat_message_field"
        )
        
    with col_btn:
        submit_btn = st.button("➔", key="send_arrow_btn")

    # Display Attachment options inside a structured card if drawer toggled active
    uploaded_files = None
    query_mode = "Solve Question"
    
    if st.session_state.show_plus_menu:
        st.markdown('<div class="drawer-container">', unsafe_allow_html=True)
        st.markdown("<p style='margin:0 0 5px 0; font-size:13px; color:#9aa0a6; font-weight:bold;'>ATTACHMENTS & UTILITIES</p>", unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            label="Upload Assignment Document Pages (Images/PDFs):",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="drawer_media_uploader"
        )
        
        query_mode = st.selectbox(
            label="Select Task Query Type Profile:",
            options=["Solve Question Step-by-Step", "Generate Quick Revision Summary Notes", "Extract Core Formula Breakdown Sheet"],
            key="drawer_mode_selector"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Processing Input Request Core
    if submit_btn:
        has_text = bool(user_query.strip())
        has_files = bool(uploaded_files) if uploaded_files else False

        if not client_ready:
            st.error("AI service engine core modules are offline.")
        elif not has_text and not has_files:
            st.warning("Please input text variables or attach a document panel asset.")
        else:
            contents_payload = []
            
            # Formulate behavioral instructions based on selected drawer category
            system_scaffolding = "You are an expert high school tutor assistant. "
            if query_mode == "Generate Quick Revision Summary Notes":
                system_scaffolding += "Provide a high-yield summary revision guide layout. Use clean bullet points, bold key definitions, and include a 'Key Takeaway' summary.\n"
            elif query_mode == "Extract Core Formula Breakdown Sheet":
                system_scaffolding += "Isolate and display all mathematical and physics formulas explicitly in a clean structural matrix layout.\n"
            else:
                system_scaffolding += "Answer the query with a comprehensive, verified step-by-step logical solution breakdown.\n"
                
            history_context = system_scaffolding + "Review the history context window if needed:\n"
            for past_msg in current_session["history"][-6:]:
                history_context += f"{past_msg['role']}: {past_msg['text']}\n"
            contents_payload.append(history_context)

            # Define localized presentation log markers
            mode_tag = f"<b>[{query_mode}]</b> "
            if has_text and has_files:
                display_log_text = f"{mode_tag}{user_query} <i>(+{len(uploaded_files)} files attached)</i>"
            elif has_files:
                display_log_text = f"{mode_tag}<i>[Attached {len(uploaded_files)} document assets for evaluation]</i>"
            else:
                display_log_text = f"{mode_tag}{user_query}"

            if has_files:
                for f in uploaded_files:
                    file_bytes = f.read()
                    mime_type = f.type
                    contents_payload.append(
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    )

            if has_text:
                contents_payload.append(user_query)
            else:
                contents_payload.append("Process and fulfill the selected action criteria details on the attached elements completely.")

            current_session["history"].append({"role": "user", "text": display_log_text})

            with st.spinner("Tutor AI processing calculations..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload
                    )
                    
                    current_session["history"].append({"role": "model", "text": response.text})
                    
                    if len(current_session["history"]) <= 2 and has_text:
                        current_session["title"] = user_query[:25]
                    
                    # Close drawer automatically after sending to clean the screen view layout
                    st.session_state.show_plus_menu = False
                    st.rerun()

                except Exception as api_err:
                    st.error("API response generation module hit a tracking error block.")
                    st.code(f"Diagnostic Logs Trace: {api_err}")

# ------------------------------------------
# TAB 2: FORMULA QUICK REFERENCE CHEAT SHEET
# ------------------------------------------
with tab2:
    st.header("Formula Matrix")
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
        """, unsafe_allow_html=True)
    elif subject_choice == "Mathematics Essentials":
        st.markdown("""
        <div class='feature-card'>
            <h4>📐 Calculus & Algebra Matrix</h4>
            <ul>
                <li><strong>Quadratic Formula Roots:</strong> <code>x = [-b ± √(b² - 4ac)] / 2a</code></li>
                <li><strong>Fundamental Derivative:</strong> <code>d/dx(x^n) = n * x^(n-1)</code></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: BRAIN BOOSTER FLASHCARDS
# ------------------------------------------
with tab3:
    st.header("Interactive Concept Flashcards")
    with st.expander("❓ Question 1: What does Lenz's Law determine in electromagnetic physics?"):
        st.markdown("🎯 **Answer:** It states that the direction of the induced current always opposes the change in magnetic flux that produced it. (Obeys the Conservation of Energy).")
    with st.expander("❓ Question 2: Why do real gases deviate from Ideal Gas behavior?"):
        st.markdown("🎯 **Answer:** Real gases have actual intermolecular attractive forces between molecules, and their individual gas molecules occupy a finite, non-zero volume space.")

# ==========================================
# 7. FOOTER ARCHITECTURE
# ==========================================
st.markdown("---")
st.caption("✨ Academic AI Assistant Engine Running Multi-Session Custom Chat Core.")
