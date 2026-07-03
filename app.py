import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import pypdf

# ==========================================
# 1. PAGE CONFIGURATION & THEME LAYOUT
# ==========================================
st.set_page_config(
    page_title="Academic AI Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling injected to create a clean ChatGPT/Gemini interface
st.markdown("""
    <style>
    /* Global Background and Text Color Themes */
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    
    /* Dedicated Project Introduction Header Card */
    .intro-banner {
        background: linear-gradient(135deg, #1e1e24, #2a2b36);
        border: 1px solid #3c4043;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .intro-banner h2 {
        color: #8ab4f8;
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
    }
    .intro-banner p {
        color: #c4c7c5;
        font-size: 0.95rem;
        margin: 0.2rem 0;
    }
    .credit-highlight {
        color: #ecb22e;
        font-weight: 600;
    }
    
    /* Chat Conversation Styling Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding-bottom: 9rem;
    }
    .chat-row {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .user-avatar { background-color: #5f6368; color: white; }
    .bot-avatar { background: linear-gradient(135deg, #1a73e8, #8ab4f8); color: white; }
    
    .message-content {
        max-width: 85%;
        line-height: 1.6;
        font-size: 1.05rem;
    }
    
    /* Structured Styling for the 3-Part Answer Layout */
    .section-box {
        background-color: #1e1f20;
        border-left: 4px solid #4285F4;
        padding: 0.8rem;
        margin-top: 0.5rem;
        border-radius: 0 8px 8px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FIXED SCHOOL PROJECT CREDITS BANNER
# ==========================================
# Change X, Y, and Z School below to match your actual details
st.markdown("""
    <div class='intro-banner'>
        <h2>📚 Smart Academic AI Assistant</h2>
        <p>Developed by: <span class='credit-highlight'>harshit</span> and <span class='credit-highlight'>umarfahrukh</span></p>
        <p>Under the Project of: <span class='credit-highlight'>atsbv School</span></p>
        <p style='font-size: 0.85rem; color: #9aa0a6; margin-top: 0.5rem;'>
            Strictly authorized to process and break down school curriculum questions only.
        </p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. INITIALIZE SECURE API CLIENT & MEMORY
# ==========================================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state["api_key"]
else:
    api_key = None

if not api_key:
    with st.sidebar:
        st.subheader("🔑 API Setup")
        user_key = st.text_input("Enter Gemini API Key:", type="password")
        if user_key:
            st.session_state["api_key"] = user_key
            st.rerun()
    st.info("💡 Please look at the sidebar drawer and insert your Gemini API Key to initialize the engine.")
    st.stop()

client = genai.Client(api_key=api_key)

# The core Chat History Engine (Maintains memory context across the webpage timeline)
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 4. RENDER PREVIOUS DISCUSSIONS (MEMORY VIEW)
# ==========================================
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
            <div class='chat-row'>
                <div class='avatar user-avatar'>🧑</div>
                <div class='message-content'><b>You:</b><br>{msg['text']}</div>
            </div>
        """, unsafe_allow_html=True)
        if "image" in msg and msg["image"] is not None:
            st.image(msg["image"], width=250)
    else:
        st.markdown(f"""
            <div class='chat-row'>
                <div class='avatar bot-avatar'>✨</div>
                <div class='message-content'><b>Tutor Engine:</b><br>{msg['text']}</div>
            </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 5. DOCK STYLE INPUT & MEDIA FILE SLOTS
# ==========================================
input_container = st.container()
with input_container:
    col_attach, col_text = st.columns([1, 6])
    
    with col_attach:
        uploaded_file = st.file_uploader(
            "➕", 
            type=["png", "jpg", "jpeg", "pdf"], 
            help="Upload assignment sheets, text diagrams or textbook PDFs",
            label_visibility="visible"
        )
        
    with col_text:
        with st.form(key="chat_form", clear_on_submit=True):
            user_text = st.text_input(
                "",
                placeholder="Type your homework query...",
                label_visibility="collapsed"
            )
            submit_button = st.form_submit_button(label="⬆️ Submit")

# ==========================================
# 6. ENFORCING COMPLEX STRUCTURAL RULES
# ==========================================
if submit_button and user_text:
    api_contents = []
    processed_img = None
    extracted_pdf_text = ""
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()
        if file_type in ["png", "jpg", "jpeg"]:
            processed_img = Image.open(uploaded_file)
            api_contents.append(processed_img)
        elif file_type == "pdf":
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted_pdf_text += page.extract_text() + "\n"
            user_text = f"[Document Scan Context:\n{extracted_pdf_text}]\n\nUser Query: {user_text}"

    # Log user's viewable bubble into memory arrays
    st.session_state.messages.append({
        "role": "user", 
        "text": user_text.split("]\n\nUser Query: ")[-1], 
        "image": processed_img
    })

    # Compiling historical context so the model remembers past questions inside the chat loop
    # We append the active conversation history directly into the API request content payload
    for past_msg in st.session_state.messages[:-1]:
        api_contents.append(f"{past_msg['role'].replace('model', 'assistant')}: {past_msg['text']}")
    
    # Active latest message prompt append
    api_contents.append(f"user: {user_text}")
    
    # Strictly structured system rules enforcing your constraints
    academic_guardrail = (
        "CRITICAL ROLE RULE: You are a specialized AI Academic Tutor. You are ONLY allowed to assist with school subjects "
        "(Physics, Chemistry, Math, Biology, History, Computer Science, Economics, etc.). "
        "If a user asks a casual, recreational, or non-academic question (e.g., daily chat, writing songs, movie summaries, "
        "video game scripts, tech buying advice), you must strictly refuse to answer. Reply exactly with: "
        "'I am sorry, but I am programmed to only answer academic and school-related questions.'\n\n"
        
        "RESPONSE LAYOUT RULE: If the question is validly academic, you must format your response into exactly three sequential parts:\n"
        "1. **Direct Answer:** Give the short, clear, absolute answer directly in a brief sentence or expression.\n"
        "2. **Expanded Solution:** Provide a deep, step-by-step breakdown or calculation explaining how that answer is derived.\n"
        "3. **Concept Applied:** State the scientific/academic formula, law, theorem, or core logic used, along with a short explanation of that concept.\n\n"
        
        "Ensure you use Google Search grounding tools to confirm that information, formulas, and historical data are highly accurate."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=api_contents,
            config=types.GenerateContentConfig(
                system_instruction=academic_guardrail,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        # Save structural output into session memory state
        st.session_state.messages.append({"role": "model", "text": response.text})
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to fetch response from backend processing core: {e}")
              
