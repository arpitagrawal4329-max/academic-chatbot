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

# Custom CSS to lock everything into a single horizontal slab line and fix mobile layouts
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
    
    /* Strict force rules to keep columns horizontally aligned on mobile phones */
    div[data-testid="stHorizontalBlock"] {
        background-color: #1e1e24 !important;
        border: 1px solid #3c4043 !important;
        border-radius: 24px !important;
        padding: 8px 14px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px !important;
    }
    
    /* Remove default element spaces */
    div[data-testid="stHorizontalBlock"] > div {
        width: auto !important;
        flex-grow: 0 !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Let the central text box fill up the remaining space dynamically */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        flex-grow: 1 !important;
    }
    
    /* Remove labels and background boxes from the inputs */
    div[data-testid="stTextInput"] label, div[data-testid="stFileUploader"] label, div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    
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
    
    /* Transparent action icons buttons setup */
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
    }
    .stButton>button:hover {
        color: #e3e3e3 !important;
    }
    
    /* Styling for the drop-down attachment window drawer inside the chat layout */
    .drawer-inline-box {
        background-color: #232329;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #3c4043;
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
# 3. BACKEND AUTHENTICATION SETUP
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
client_ready = False

if not api_key:
    st.error("🔑 API Key Configuration Missing! Add your key to Streamlit settings.")
else:
    try:
        client = genai.Client(api_key=api_key)
        client_ready = True
    except Exception as e:
        st.error(f"Engine failure: {e}")

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
# TAB 1: UIFIED COMPACT SLAB INTERFACE
# ------------------------------------------
with tab1:
    st.subheader(f"Session Focus: {current_session['title']}")
    
    st.write("---")
    if not current_session["history"]:
        st.caption("No queries submitted yet. Use the integrated input bar below.")
    else:
        for chat in current_session["history"]:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # Dynamic Inline Drawer Layout (Appears cleanly right ABOVE the unified single-line row only when needed)
    uploaded_files = None
    query_mode = "Solve Question Step-by-Step"
    
    if st.session_state.show_plus_menu:
        st.markdown('<div class="drawer-inline-box">', unsafe_allow_html=True)
        st.markdown("<p style='margin:0 0 5px 0; font-size:12px; color:#4b6cb7; font-weight:bold;'>ATTACH FILE ASSIGNMENTS</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(label="file_up", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True, key="inline_media_field")
        
        st.markdown("<p style='margin:10px 0 5px 0; font-size:12px; color:#4b6cb7; font-weight:bold;'>SELECT QUERY STYLE</p>", unsafe_allow_html=True)
        query_mode = st.selectbox(label="mode_sel", options=["Solve Question Step-by-Step", "Generate Quick Revision Summary Notes", "Extract Core Formula Breakdown Sheet"], key="inline_mode_field")
        st.markdown('</div>', unsafe_allow_html=True)

    # UNIFIED SINGLE SLAB ROW: Plus button, text box, and send arrow aligned strictly in one straight line
    col_plus, col_text, col_btn = st.columns([1, 10, 1])
    
    with col_plus:
        if st.button("＋", key="pod_drawer_toggle"):
            st.session_state.show_plus_menu = not st.session_state.show_plus_menu
            st.rerun()
            
    with col_text:
        user_query = st.text_input(
            label="query_txt",
            placeholder="Ask your academic question here...",
            key="chat_message_field"
        )
        
    with col_btn:
        submit_btn = st.button("➔", key="pod_send_arrow")

    # ------------------------------------------
    # 7. LOGIC PIPELINE BACKEND PROCESSING CORE
    # ------------------------------------------
    if submit_btn:
        has_text = bool(user_query.strip())
        has_files = bool(uploaded_files) if uploaded_files else False

        if not client_ready:
            st.error("AI client backend core is offline.")
        elif not has_text and not has_files:
            st.warning("Please type a question or select a file asset first.")
        else:
            contents_payload = []
            
            # Scaffolding logic customization
            system_scaffolding = "You are an expert high school tutor assistant. "
            if query_mode == "Generate Quick Revision Summary Notes":
                system_scaffolding += "Provide a high-yield summary revision guide layout with bullet points.\n"
            elif query_mode == "Extract Core Formula Breakdown Sheet":
                system_scaffolding += "Isolate and organize mathematical equations clearly.\n"
            else:
                system_scaffolding += "Provide a comprehensive step-by-step breakdown solution.\n"
                
            history_context = system_scaffolding + "Review past conversation window context logs if relevant:\n"
            for past_msg in current_session["history"][-6:]:
                history_context += f"{past_msg['role']}: {past_msg['text']}\n"
            contents_payload.append(history_context)

            # Format visual log title text
            mode_tag = f"<b>[{query_mode}]</b> " if st.session_state.show_plus_menu else ""
            if has_text and has_files:
                display_log_text = f"{mode_tag}{user_query} <i>(+{len(uploaded_files)} files)</i>"
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
                contents_payload.append("Process the action requirements on the attached document elements completely.")

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
                    
                    # Reset dynamic pop-up view state back to standard clean workspace profile automatically
                    st.session_state.show_plus_menu = False
                    st.rerun()
                except Exception as api_err:
                    st.error(f"Execution Error: {api_err}")

# ------------------------------------------
# HIGH SCHOOL PRE-BOARD STUDY REFERENCE TABS
# ------------------------------------------
with tab2:
    st.header("Formula Matrix")
    subject_choice = st.selectbox("Choose target subject:", ["Physics", "Chemistry", "Mathematics"])
    if subject_choice == "Physics":
        st.markdown("⚡ `v = u + at` | Lens Maker Formula: `1/f = (μ - 1)*(1/R₁ - 1/R₂)`")
    elif subject_choice == "Chemistry":
        st.markdown("🧪 Ideal Gas Law: `P * V = n * R * T` | Gibbs Criterion: `ΔG = ΔH - TΔS`")
    elif subject_choice == "Mathematics":
        st.markdown("📐 Roots Matrix: `x = [-b ± √(b² - 4ac)] / 2a` | Derivative Rule: `d/dx(x^n) = n*x^(n-1)`")

with tab3:
    st.header("Interactive Concept Flashcards")
    with st.expander("❓ What does Lenz's Law state?"):
        st.markdown("🎯 Induced current direction always opposes the change in magnetic flux that produced it. (Conserves energy).")
