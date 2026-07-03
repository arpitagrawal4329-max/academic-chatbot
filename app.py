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

# Custom CSS to force the single grey area capsule layout and style icons
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
    
    /* Unified Gemini-style grey workspace pod */
    .gemini-input-pod {
        background-color: #1e1e24;
        border: 1px solid #3c4043;
        border-radius: 24px;
        padding: 12px 16px;
        margin-top: 10px;
    }
    
    /* Clean overrides to kill standard block spacing inside the grey container */
    div[data-testid="stTextInput"] label, div[data-testid="stFileUploader"] label, div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"], div[data-testid="stFileUploader"] {
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Flat transparent text input box within the capsule pod */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        color: #e3e3e3 !important;
        padding: 0px !important;
        font-size: 15px;
    }
    div[data-testid="stTextInput"] input:focus {
        box-shadow: none !important;
    }
    
    /* Icon Buttons configurations styling */
    .stButton>button {
        background-color: transparent !important;
        color: #9aa0a6 !important;
        border: none !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 36px !important;
        padding: 0px !important;
        margin: 0px !important;
        display: flex;
        align-items: center;
        justify-content: center;
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
    st.error("🔑 API Key Configuration Missing! Go to Secrets drawer.")
else:
    try:
        client = genai.Client(api_key=api_key)
        client_ready = True
    except Exception as e:
        st.error(f"Initialization failure: {e}")

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
                    st.session_state.active_chat_id = remaining_ids[0] if remaining_ids else None
                st.rerun()
                
    st.markdown("---")
    if st.button("🗑️ Clear Entire History", key="clear_all_global_history_btn"):
        st.session_state.all_chats = {}
        st.session_state.active_chat_id = None
        st.session_state.show_plus_menu = False
        st.rerun()

# Fallback check if everything cleared out
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
# TAB 1: QUESTION SOLVER (UNIFIED CAPSULE ENGINE)
# ------------------------------------------
with tab1:
    st.subheader(f"Session Focus: {current_session['title']}")
    
    st.write("---")
    if not current_session["history"]:
        st.caption("No queries submitted yet. Use the chat bar below to get started.")
    else:
        for chat in current_session["history"]:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # The Unified Grey Area Workspace Pod Container
    st.markdown('<div class="gemini-input-pod">', unsafe_allow_html=True)
    
    uploaded_files = None
    query_mode = "Solve Question Step-by-Step"
    
    # 1. Dynamic Inline Drawer Section (Appears cleanly right *above* text box when active)
    if st.session_state.show_plus_menu:
        st.markdown("<p style='margin:0 0 4px 0; font-size:12px; color:#4b6cb7; font-weight:bold;'>Upload Files Below:</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            label="inline_uploader",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="pod_media_uploader"
        )
        st.markdown("<p style='margin:8px 0 4px 0; font-size:12px; color:#4b6cb7; font-weight:bold;'>Select Task Mode:</p>", unsafe_allow_html=True)
        query_mode = st.selectbox(
            label="inline_mode",
            options=["Solve Question Step-by-Step", "Generate Quick Revision Summary Notes", "Extract Core Formula Breakdown Sheet"],
            key="pod_mode_selector"
        )
        st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid #3c4043;'>", unsafe_allow_html=True)

    # 2. Main Horizontal Interactive Controls Row
    col_plus, col_text, col_btn = st.columns([1, 10, 1])
    
    with col_plus:
        toggle_drawer = st.button("＋", key="pod_drawer_toggle")
        if toggle_drawer:
            st.session_state.show_plus_menu = not st.session_state.show_plus_menu
            st.rerun()
            
    with col_text:
        user_query = st.text_input(
            label="pod_text_input",
            placeholder="Ask your academic question here...",
            key="chat_message_field"
        )
        
    with col_btn:
        submit_btn = st.button("➔", key="pod_send_arrow")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Execution Processing Engine Pipeline
    if submit_btn:
        has_text = bool(user_query.strip())
        has_files = bool(uploaded_files) if uploaded_files else False

        if not client_ready:
            st.error("AI service offline.")
        elif not has_text and not has_files:
            st.warning("Please provide input text or data objects.")
        else:
            contents_payload = []
            
            # Base Prompts Modification Scaffolding Mapping
            system_scaffolding = "You are an expert high school tutor assistant. "
            if query_mode == "Generate Quick Revision Summary Notes":
                system_scaffolding += "Provide a high-yield summary revision guide layout. Use clean bullet points and bold key terms.\n"
            elif query_mode == "Extract Core Formula Breakdown Sheet":
                system_scaffolding += "Isolate and display equations inside structured blocks.\n"
            else:
                system_scaffolding += "Provide a complete step-by-step breakdown calculation solution.\n"
                
            history_context = system_scaffolding + "Review context window logs:\n"
            for past_msg in current_session["history"][-6:]:
                history_context += f"{past_msg['role']}: {past_msg['text']}\n"
            contents_payload.append(history_context)

            # Generate local dynamic visual message tags
            mode_tag = f"<b>[{query_mode}]</b> " if st.session_state.show_plus_menu else ""
            if has_text and has_files:
                display_log_text = f"{mode_tag}{user_query} <i>(+{len(uploaded_files)} documents)</i>"
            elif has_files:
                display_log_text = f"{mode_tag}<i>[Sent {len(uploaded_files)} documents for evaluation]</i>"
            else:
                display_log_text = f"{mode_tag}{user_query}"

            if has_files:
                for f in uploaded_files:
                    contents_payload.append(types.Part.from_bytes(data=f.read(), mime_type=f.type))

            if has_text:
                contents_payload.append(user_query)
            else:
                contents_payload.append("Process the action requirements on the attached elements completely.")

            current_session["history"].append({"role": "user", "text": display_log_text})

            with st.spinner("Tutor AI processing execution..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload
                    )
                    current_session["history"].append({"role": "model", "text": response.text})
                    if len(current_session["history"]) <= 2 and has_text:
                        current_session["title"] = user_query[:25]
                    
                    # Hide layout drawers automatically to revert interface window cleanly
                    st.session_state.show_plus_menu = False
                    st.rerun()
                except Exception as api_err:
                    st.error(f"Execution Error: {api_err}")

# ------------------------------------------
# SUBJECTS QUICK REFERENCE REFERENCE DATA
# ------------------------------------------
with tab2:
    st.header("Formula Matrix")
    subject_choice = st.selectbox("Choose target subject:", ["Physics", "Chemistry", "Mathematics"])
    if subject_choice == "Physics":
        st.markdown("⚡ `v = u + at` | Lens Maker: `1/f = (μ - 1)*(1/R₁ - 1/R₂)`")
    elif subject_choice == "Chemistry":
        st.markdown("🧪 Ideal Gas Law: `P * V = n * R * T` | `ΔG = ΔH - TΔS`")
    elif subject_choice == "Mathematics":
        st.markdown("📐 Roots: `x = [-b ± √(b² - 4ac)] / 2a` | Power Rule: `d/dx(x^n) = n*x^(n-1)`")

with tab3:
    st.header("Interactive Concept Flashcards")
    with st.expander("❓ What does Lenz's Law state?"):
        st.markdown("🎯 Induced current direction always opposes the change in magnetic flux that produced it.")
