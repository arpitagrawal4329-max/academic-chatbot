import streamlit as st
from google import genai
from google.genai import types
import os
import uuid
import re

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
        border-left: 3px solid #4b6cb7;
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
# 2. BACKEND AUTHENTICATION SETUP
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
# 3. GLOBAL & SESSION STATE INITIALIZER
# ==========================================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "extracted_formulas" not in st.session_state:
    st.session_state.extracted_formulas = []
if "extracted_flashcards" not in st.session_state:
    st.session_state.extracted_flashcards = []
if "extracted_practice" not in st.session_state:
    st.session_state.extracted_practice = []

if "active_chat_id" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.all_chats[first_id] = {
        "title": "New Problem Solving Session",
        "history": []
    }
    st.session_state.active_chat_id = first_id

if "show_plus_menu" not in st.session_state:
    st.session_state.show_plus_menu = False

current_session = st.session_state.all_chats.get(st.session_state.active_chat_id)

# ==========================================
# 4. CONDITIONAL INTRO BANNER ARCHITECTURE
# ==========================================
if current_session and len(current_session["history"]) == 0:
    st.markdown("""
        <div class="credit-box">
            <h2 style='margin-top:0; color:#4b6cb7; font-size:24px;'>🎓 Academic AI Assistant Workspace</h2>
            <p style='margin-bottom:5px; font-size:14px;'>Welcome to your study environment! Ask questions, break down formulas, and generate revision tools live.</p>
            <hr style='border-color: #3c4043; margin: 10px 0;'>
            <p style='margin-bottom:5px; font-size:13px;'><strong>Developed by:</strong> Harshit Agrawal & Umar Fahrukh</p>
            <p style='margin-bottom:5px; font-size:13px;'><strong>School:</strong> Acharya Tulsi Sarvodaya Bal Vidyalaya &nbsp;|&nbsp; <strong>Guided by:</strong> Gopal Meena Sir</p>
        </div>
    """, unsafe_allow_html=True)

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
        st.session_state.extracted_formulas = []
        st.session_state.extracted_flashcards = []
        st.session_state.extracted_practice = []
        fallback_id = str(uuid.uuid4())
        st.session_state.all_chats[fallback_id] = {
            "title": "New Problem Solving Session",
            "history": []
        }
        st.session_state.active_chat_id = fallback_id
        st.session_state.show_plus_menu = False
        st.rerun()

# ==========================================
# 6. APPLICATION MAIN INTERFACE TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Question Solver", 
    "📐 Formula Reference", 
    "🧠 Brain Booster Flashcards",
    "📝 Practice Bank"
])

# ------------------------------------------
# TAB 1: QUESTION SOLVER
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
                clean_render = re.sub(r'\[FORMULA\].*?\[/FORMULA\]|\[FLASHCARD\].*?\[/FLASHCARD\]|\[PRACTICE\].*?\[/PRACTICE\]', '', chat["text"], flags=re.DOTALL)
                st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{clean_render.strip()}</div>', unsafe_allow_html=True)
    st.write("---")

    # Placed prominent profile selector straight in the tab workspace view as per image 1000055783.jpg
    query_mode = st.selectbox(
        label="Select Task Query Type Profile:",
        options=["Solve Question Step-by-Step", "Generate Quick Revision Summary Notes", "Extract Core Formula Breakdown Sheet"],
        key="main_mode_selector"
    )

    # Dynamic File Drawer Elements Container (Exclusively holds attachment utilities now)
    uploaded_files = None
    if st.session_state.show_plus_menu:
        st.markdown('<div class="drawer-container">', unsafe_allow_html=True)
        st.markdown("<p style='margin:0 0 5px 0; font-size:13px; color:#9aa0a6; font-weight:bold;'>ATTACHMENTS & MEDIA</p>", unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            label="Upload Assignment Document Pages (Images/PDFs):",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="drawer_media_uploader"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Ultra-Compact Input Layout Line
    col_plus, col_text, col_btn = st.columns([1, 8, 1])

    with col_plus:
        st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
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

    if submit_btn:
        has_text = bool(user_query.strip())
        has_files = bool(uploaded_files) if uploaded_files else False

        if not client_ready:
            st.error("AI service engine core modules are offline.")
        elif not has_text and not has_files:
            st.warning("Please input text variables or attach a document panel asset.")
        else:
            contents_payload = []
            
            system_scaffolding = (
                "You are an expert high school tutor assistant. Respond to the user's primary request comprehensively. "
                "CRITICAL INSTRUCTION: In addition to your main explanation, you MUST append structural tags at the very bottom of your response to update the student's learning workspace dashboards if any are relevant to the query topic:\n"
                "1. If any mathematical or scientific formulas were used or are relevant, list them at the bottom exactly inside tags like this: [FORMULA]Name | Standard text or LaTeX string[/FORMULA]\n"
                "2. Generate 1 relevant flashcard question/answer set based on the query concept: [FLASHCARD]Question text | Answer text[/FLASHCARD]\n"
                "3. Generate 1-2 challenging practice follow-up questions for the student to attempt later: [PRACTICE]Topic Header | Question description content[/PRACTICE]\n\n"
            )
            
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
                    contents_payload.append(types.Part.from_bytes(data=file_bytes, mime_type=mime_type))

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
                    
                    raw_text = response.text
                    current_session["history"].append({"role": "model", "text": raw_text})
                    
                    # Background Parsing Engine
                    formulas_found = re.findall(r'\[FORMULA\](.*?)\[/FORMULA\]', raw_text, flags=re.DOTALL)
                    for item in formulas_found:
                        if '|' in item:
                            name, val = item.split('|', 1)
                            st.session_state.extracted_formulas.append({"name": name.strip(), "val": val.strip()})
                            
                    flashcards_found = re.findall(r'\[FLASHCARD\](.*?)\[/FLASHCARD\]', raw_text, flags=re.DOTALL)
                    for item in flashcards_found:
                        if '|' in item:
                            q, a = item.split('|', 1)
                            st.session_state.extracted_flashcards.append({"q": q.strip(), "a": a.strip()})
                            
                    practice_found = re.findall(r'\[PRACTICE\](.*?)\[/PRACTICE\]', raw_text, flags=re.DOTALL)
                    for item in practice_found:
                        if '|' in item:
                            topic, task = item.split('|', 1)
                            st.session_state.extracted_practice.append({"topic": topic.strip(), "task": task.strip()})

                    if len(current_session["history"]) <= 2 and has_text:
                        current_session["title"] = user_query[:25]
                    
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
    st.markdown("### 📌 Standard Reference Guide")
    col_sel_subject = st.selectbox("Filter reference blueprints:", ["Physics Basics", "Chemistry Foundations"])
    if col_sel_subject == "Physics Basics":
        st.markdown("<div class='feature-card'><b>Kinematics Base:</b></div>", unsafe_allow_html=True)
        st.latex(r"v = u + at \quad | \quad s = ut + \frac{1}{2}at^2")
    else:
        st.markdown("<div class='feature-card'><b>Ideal Gas Law:</b></div>", unsafe_allow_html=True)
        st.latex(r"P \cdot V = n \cdot R \cdot T")
        
    st.write("---")
    st.markdown("### ⚡ Live Extracted Formulas")
    
    if not st.session_state.extracted_formulas:
        st.caption("No dynamic formulas captured yet. Ask questions containing mathematical problem vectors in the solver tab.")
    else:
        for f in st.session_state.extracted_formulas:
            with st.container():
                st.markdown(f"<div class='feature-card'><b>{f['name']}</b></div>", unsafe_allow_html=True)
                if any(char in f['val'] for char in ['\\', '^', '_', '/', 'frac']):
                    st.latex(f['val'])
                else:
                    st.info(f['val'])

# ------------------------------------------
# TAB 3: BRAIN BOOSTER FLASHCARDS
# ------------------------------------------
with tab3:
    st.header("Interactive Concept Flashcards")
    st.markdown("### 📌 Core Flashcard Sets")
    with st.expander("❓ Question: What does Lenz's Law determine?"):
        st.markdown("🎯 **Answer:** Induced current always opposes the exact change in magnetic flux that produced it.")
        
    st.write("---")
    st.markdown("### 🧠 Live Generated Study Decks")
    
    if not st.session_state.extracted_flashcards:
        st.caption("AI-generated memory cards appear here automatically based on active workspace conversations.")
    else:
        for idx, card in enumerate(st.session_state.extracted_flashcards):
            with st.expander(f"❓ Card {idx+1}: {card['q']}"):
                st.markdown(f"🎯 **Answer Recall Guide:**\n{card['a']}")

# ------------------------------------------
# TAB 4: PRACTICE BANK
# ------------------------------------------
with tab4:
    st.header("🎯 Target Practice Workspace")
    st.markdown("Review custom exercise tasks automatically curated by the tutor based on topics you previously struggled with or asked about.")
    st.write("---")
    
    if not st.session_state.extracted_practice:
        st.info("Excellent! Your Practice Bank is empty. Ask complex academic questions in the Question Solver to receive target exercise variants.")
    else:
        for idx, task in enumerate(st.session_state.extracted_practice):
            st.markdown(f"""
            <div class="feature-card">
                <span style="background-color:#4b6cb7; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;">TASK {idx+1}</span>
                <h4 style='margin: 5px 0;'>📚 {task['topic']}</h4>
                <p style='margin:0; color:#b3b3b3;'>{task['task']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 7. FOOTER ARCHITECTURE
# ==========================================
st.markdown("---")
st.caption("✨ Academic AI Assistant Engine Running Multi-Session Custom Chat Core.")
