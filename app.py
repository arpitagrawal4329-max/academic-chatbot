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
# 4. APPLICATION LAYOUT
# ==========================================
tab1, tab2 = st.tabs(["💬 WhatsApp Tutor Chat & Uploads", "📐 Instant Formula Reference"])

# ------------------------------------------
# TAB 1: PERSISTENT CHAT & MULTI-MODAL UPLOADER
# ------------------------------------------
with tab1:
    st.header("Interactive Study Session")
    st.write("Upload a photo or a PDF document of your textbook/homework questions, or just type a query.")

    # File Attachment Inputs
    uploaded_files = st.file_uploader(
        label="Attach relevant Images or PDF homework pages:",
        type=["png", "jpg", "jpeg", "pdf"],
        accept_multiple_files=True,
        key="academic_media_uploader"
    )

    # Chat Log View Engine (Displays previous exchanges dynamically)
    st.write("---")
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai"><b>Tutor AI:</b><br>{chat["text"]}</div>', unsafe_allow_html=True)
    st.write("---")

    # Fixed User Input Controls
    with st.form(key="chat_input_form", clear_on_submit=True):
        user_query = st.text_input(
            label="Type your message here:",
            placeholder="Ask a question or explain the uploaded document...",
            key="chat_message_field"
        )
        submit_btn = st.form_submit_row = st.form_submit_button(label="Send Message")

    # Execution Block on Submission
    if submit_btn:
        if not client_ready:
            st.error("AI engine configuration is offline.")
        elif not user_query.strip() and not uploaded_files:
            st.warning("Please type a message or upload a file document.")
        else:
            contents_payload = []
            display_text = user_query if user_query.strip() else "[Sent Attachment Document]"

            # Process any attached file inputs into modern genai types
            if uploaded_files:
                for f in uploaded_files:
                    file_bytes = f.read()
                    mime_type = f.type
                    contents_payload.append(
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    )
                display_text += f" (+{len(uploaded_files)} attached file files)"

            # Append user entry into persistent session logs
            st.session_state.chat_history.append({"role": "user", "text": display_text})

            # Append the text message to the array payload passed to the model
            if user_query.strip():
                contents_payload.append(user_query)

            # Request generation processing
            with st.spinner("AI Tutor is analyzing entire history and payload..."):
                try:
                    # Provide system instructions via chat framework contextual continuity 
                    history_context = "You are a supportive high school homework assistant. Review previous query logs if relevant.\n"
                    for past_msg in st.session_state.chat_history[-6:]:  # include context window limit
                        history_context += f"{past_msg['role']}: {past_msg['text']}\n"
                    
                    contents_payload.insert(0, history_context)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents_payload
                    )
                    
                    # Store response to dynamic logs
                    st.session_state.chat_history.append({"role": "model", "text": response.text})
                    
                    # Refresh app layout state forcefully to show updated bubble sequences
                    st.rerun()

                except Exception as api_err:
                    st.error("The backend process could not compile this data payload successfully.")
                    st.code(f"Diagnostic Report: {api_err}")

    # Reset Option Button
    if st.button("Clear Conversation History", key="clear_session_trigger"):
        st.session_state.chat_history = []
        st.rerun()

# ------------------------------------------
# TAB 2: QUICK STUDY REFERENCE MATRICES
# ------------------------------------------
with tab2:
    st.header("Quick Subject Formula Sheet")
    subject_choice = st.selectbox(
        label="Select a course stream:",
        options=["Physics Formulas", "Chemistry Equations", "Mathematics Essentials"],
        key="ref_tab_selector"
    )
    
    if subject_choice == "Physics Formulas":
        st.code("Equations of Motion:\n v = u + at\n s = ut + 0.5*a*t^2\n v^2 = u^2 + 2as")
        st.code("Electrostatics Force:\n F = k * (q1 * q2) / r^2")
    elif subject_choice == "Chemistry Equations":
        st.code("Ideal Gas Equation:\n P * V = n * R * T")
        st.code("Gibbs Free Energy:\n ΔG = ΔH - T*ΔS")
    elif subject_choice == "Mathematics Essentials":
        st.code("Quadratic Roots Solution:\n x = (-b ± √(b^2 - 4ac)) / (2a)")
        st.code("Derivative Power Rule:\n d/dx(x^n) = n * x^(n-1)")

# ==========================================
# 5. FOOTER ARCHITECTURE
# ==========================================
st.markdown("---")
st.caption("✨ Academic AI Assistant Engine Running Multi-Modal Persistent Architecture.")
