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

# Custom CSS styling to force a tight, single grey area container layout
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
    .sidebar-text {
        color: #9aa0a6;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 10px;
    }
    
    /* Strict global container capsule matching modern chat bar styles */
    .unified-grey-pod {
        background-color: #1e1e24 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 20px !important;
        padding: 12px 16px !important;
        margin-top: 10px;
    }
    
    /* Eliminate default spacing labels inside the compact layout elements */
    div[data-testid="stTextInput"] label, div[data-testid="stFileUploader"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"], div[data-testid="stFileUploader"] {
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Force horizontal flexing bar items inside the lower control row layout */
    .chat-controls-row {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 12px !important;
        width: 100% !important;
    }
    .flex-input-grow {
        flex-grow: 1 !important;
    }
    
    /* Input element color overrides */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        color: #e3e3e3 !important;
        padding: 0px !important;
        font-size: 15px !important;
        height: 36px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        box-shadow: none !important;
    }
    
    /* Action control icons button styling overrides */
    .stButton>button {
        background-color: transparent !important;
        color: #9aa0a6 !important;
        border: none !important;
        font-size: 20px !important;
        font-weight: bold !important;
        height: 36px !important;
        width: 36px !important;
        padding: 0px !important;
        margin: 0px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stButton>button:hover {
        color: #e3e3e3 !important;
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
    st.error("🔑 API Key Configuration Missing! Check your Streamlit Secrets drawer.")
else:
    try:
        client = genai.Client(api_key=api_key)
        client_ready = True
    except Exception as e:
        st.error(f"Engine Core Failure: {e}")

# ==========================================
# 4. SESSION STATE CONVERSATION CONFIG
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

if "show_plus_menu" not in st.session_state:
    st.session_state.show_plus_menu = False

# ==========================================
# 5. SIDEBAR NAVIGATION MENU (RECENTS BAR)
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
                    st.session_state.active_chat_id = remaining_ids[0] if remaining_ids else None
                st.rerun()
                
    st.markdown("---")
    if st.button("🗑️ Clear Entire History", key="clear_all_global_history_btn"):
        st.session_state.all_chats = {}
        st.session_state.active_chat_id = None
        st.session_state.show_plus_menu = False
        st.rerun()

if not st.session_state.active_chat_id or st.session_state.active_chat_id not in st.session_state.all_chats:
    fallback_id = str(uuid.uuid4())
    st.session_state.all_chats[fallback_id] = {"title": "New Problem Solving Session", "history": []}
    st.session_state.active_chat_id = fallback_id

current_session = st.session_state.all_chats[st.session_state.active_chat_id]

# ==========================================
# 6. APPLICATION MAIN INTERFACE TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔍 Question Solver", "📐 Formula Reference", "🧠 Brain Booster Flashcards"])

# ------------------------------------------
# TAB 1: UNIFIED INPUT SLAB SYSTEM
# ------------------------------------------
with tab1:
    st.subheader(f"Session Focus: {current_session['title']}")
    
    st.write("---")
    if not current_session["history"]:
        st.caption("No queries submitted yet. Use the integrated workspace bar below to begin.")
    else:
        for chat in current_session["history"]:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # ONE SINGLE GREY CONTAINER AREA FOR EVERYTHING
    st.markdown('<div class="unified-grey-pod">', unsafe_allow_html=True)
    
    uploaded_files = None
    
    # 1. Inline File Uploader Block (Renders ABOVE the text entry box inside the grey pod when active)
    if st.session_state.show_plus_menu:
        st.markdown("<p style='margin:0 0 6px 0; font-size:12px; color:#4b6cb7; font-weight:bold;'>ATTACH FILE ASSIGNMENTS (IMAGES/PDF)</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            label="inline_media_uploader", 
            type=["png", "jpg", "jpeg", "pdf"], 
            accept_multiple_files=True, 
            key="inline_media_field"
        )
        st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid #3c4043;'>", unsafe_allow_html=True)

    # 2. Base Horizontal Control Elements Row Layout
    st.markdown('<div class="chat-controls-row">', unsafe_allow_html=True)
    
    col_p, col_t, col_b = st.columns([1, 14, 1])
    
    with col_p:
        if st.button("＋", key="pod_drawer_toggle"):
            st.session_state.show_plus_menu = not st.session_state.show_plus_menu
            st.rerun()
            
    with col_t:
        user_query = st.text_input(
            label="query_txt",
            placeholder="Ask your academic question here...",
            key="chat_message_field"
        )
        
    with col_b:
        submit_btn = st.button("➔", key="pod_send_arrow")
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 7. BACKEND EXECUTION LOGIC PIPELINE
    # ------------------------------------------
    if submit_btn:
        has_text = bool(user_query.strip())
        has_files = bool(uploaded_files) if uploaded_files else False

        if not client_ready:
            st.error("AI core processing channel is offline.")
        elif not has_text and not has_files:
            st.warning("Please type a question or choose an assignment file first.")
        else:
            contents_payload = []
            
            # Provide high school tutoring prompt framework
            history_context = (
                "You are an expert high school tutor assistant. Provide comprehensive, "
                "verified step-by-step logical breakdown solutions. Review previous logs if needed:\n"
            )
            for past_msg in current_session["history"][-6:]:
                history_context += f"{past_msg['role']}: {past_msg['text']}\n"
            contents_payload.append(history_context)

            # Build readable chat tags
            if has_text and has_files:
                display_log_text = f"{user_query} <i>(+{len(uploaded_files)} files uploaded)</i>"
            elif has_files:
                display_log_text = f"<i>[Sent {len(uploaded_files)} assignment files for verification]</i>"
            else:
                display_log_text = user_query

            if has_files:
                for f in uploaded_files:
                    contents_payload.append(types.Part.from_bytes(data=f.read(), mime_type=f.type))

            if has_text:
                contents_payload.append(user_query)
            else:
                contents_payload.append("Completely solve and break down the homework problems present inside the attached files.")

            current_session["history"].append({"role": "user", "text": display_log_text})

            with st.spinner("Calculating solutions..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload
                    )
                    current_session["history"].append({"role": "model", "text": response.text})
                    if len(current_session["history"]) <= 2 and has_text:
                        current_session["title"] = user_query[:25]
                    
                    # Auto-close the plus selection layout panel after message transmission
                    st.session_state.show_plus_menu = False
                    st.rerun()
                except Exception as api_err:
                    st.error(f"Execution Error: {api_err}")

# ------------------------------------------
# STUDY REFERENCE MATRIX & FLASHCARDS
# ------------------------------------------
with tab2:
    st.header("Formula Matrix")
    subject_choice = st.selectbox("Choose target subject:", ["Physics", "Chemistry", "Mathematics"])
    if subject_choice == "Physics":
        st.markdown("⚡ `v = u + at` | Lens Maker Formula: `1/f = (μ - 1)*(1/R₁ - 1/R₂)`")
    elif subject_choice == "Chemistry":
        st.markdown("🧪 Ideal Gas Law: `P * V = n * R * T` | Gibbs: `ΔG = ΔH - TΔS`")
    elif subject_choice == "Mathematics":
        st.markdown("📐 Quadratic Equation: `x = [-b ± √(b² - 4ac)] / 2a` | Derivative: `d/dx(x^n) = n*x^(n-1)`")

with tab3:
    st.header("Interactive Concept Flashcards")
    with st.expander("❓ What does Lenz's Law state?"):
        st.markdown("🎯 Induced current direction always opposes the change in magnetic flux that produced it. (Obeys the Conservation of Energy).")
