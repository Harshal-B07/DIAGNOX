import streamlit as st
import time
from datetime import datetime
from reasoning.orchestrator import Orchestrator
from utils.logger import get_logger
from utils.report_generator import create_pdf_report
from utils.audio_generator import generate_audio_summary
from agents.dr_ai_agent import DrDiagnaAgent

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DIAGNOX | AI Diagnostic Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLING (FIXED SELECTORS) ---
st.markdown("""
    <style>
    /* Global Settings */
    .main { background-color: #f8f9fa; }
    
    /* Standard Button Styles */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: 600; 
        padding: 12px; 
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    /* Status Badges */
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
    .status-NORMAL { background-color: #e6fcf5; color: #0ca678; border: 1px solid #c3fae8; }
    .status-HIGH { background-color: #fff5f5; color: #fa5252; border: 1px solid #ffc9c9; }
    .status-LOW { background-color: #e7f5ff; color: #228be6; border: 1px solid #d0ebff; }

    /* --- 🚀 DR. DIAGNA FLOATING TAB 🚀 --- */
    
    /* 1. FLOAT THE CONTAINER (The specific fix for position) */
    /* We target the container ID directly to rip it out of the layout flow */
    [data-testid="stPopover"] {
        position: fixed !important;
        bottom: 20px !important;
        right: 30px !important;
        z-index: 999999 !important;
        width: auto !important; /* Let it wrap the button */
    }

    /* 2. STYLE THE BUTTON (Use descendant selector ' ' instead of child '>') */
    [data-testid="stPopover"] button {
        width: 280px !important;
        height: 75px !important;
        border-radius: 20px 20px 0 20px !important; /* Rounded Tab Shape */
        background: linear-gradient(135deg, #20c997 0%, #0ca678 100%) !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(32, 201, 151, 0.4) !important;
        color: transparent !important; /* Hide default text */
        overflow: visible !important; /* Allow Avatar pop-out */
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: flex !important;
        align-items: center !important;
    }

    /* 3. HIDE DEFAULT CONTENT (Icons/Text inside the button) */
    [data-testid="stPopover"] button > * {
        display: none !important;
    }

    /* 4. ADD CUSTOM TEXT (::before) */
    [data-testid="stPopover"] button::before {
        content: "Ask Dr. Diagna";
        position: absolute;
        left: 25px;
        top: 50%;
        transform: translateY(-50%);
        color: white !important;
        font-size: 19px !important;
        font-weight: 800 !important;
        font-family: sans-serif !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 5. ADD AVATAR IMAGE (::after) */
    [data-testid="stPopover"] button::after {
        content: "";
        position: absolute;
        right: 5px; 
        bottom: 0px;
        width: 85px; 
        height: 100px;
        background-image: url('https://cdn-icons-png.flaticon.com/512/3304/3304567.png');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: bottom center;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.25));
    }

    /* 6. HOVER INTERACTION */
    [data-testid="stPopover"] button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        background: linear-gradient(135deg, #25d4a0 0%, #0eb885 100%) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

logger = get_logger("StreamlitUI")

# --- 3. SESSION STATE ---
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator()
if "dr_ai_agent" not in st.session_state:
    st.session_state.dr_ai_agent = DrDiagnaAgent()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Text Streaming Helper
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

def navigate_to(page):
    st.session_state.current_page = page

# --- 4. SIDEBAR ---
with st.sidebar:
    # 1. LOGO SECTION (Place it here)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://img.icons8.com/color/96/heart-with-pulse.png" width="80"> 
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.title("DIAGNOX")
    st.caption("Multimodal Clinical Intelligence")
    
    
    if st.button("🏠 Home", use_container_width=True):
        navigate_to("Home")
    
    if st.session_state.analysis_result:
        if st.button("📊 Executive Dashboard", use_container_width=True):
            navigate_to("Dashboard")
        if st.button("🔬 Deep Dive Analysis", use_container_width=True):
            navigate_to("Deep Dive")
            
    
    st.info("**Privacy Ensured!**\n\nNo patient data is stored.")
    st.markdown("BY Harshal Bhosale")

# --- 5. PAGE LOGIC ---

# === PAGE 1: HOME ===
if st.session_state.current_page == "Home":
    st.markdown("""
        <div style="text-align: center; padding-top: 40px; padding-bottom: 20px;">
            <h1 style="font-size: 3.5rem; margin-bottom: 10px; color: #20c997; text-shadow: 2px 2px 0px #e6fcf5;">DIAGNOX</h1>
            <p style="font-size: 1.2rem; color: #6c757d;">Advanced AI Diagnostic Assistant for Clinical Intelligence</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("### 📂 Select Document Type")
    
    if "doc_type" not in st.session_state:
        st.session_state.doc_type = "LAB_REPORT"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🧪 Lab Report", use_container_width=True, type="primary" if st.session_state.doc_type == "LAB_REPORT" else "secondary"):
            st.session_state.doc_type = "LAB_REPORT"
            st.rerun()
    with c2:
        if st.button("🦴 Radiology", use_container_width=True, type="primary" if st.session_state.doc_type == "RADIOLOGY" else "secondary"):
            st.session_state.doc_type = "RADIOLOGY"
            st.rerun()
    with c3:
        if st.button("📝 Clinical Note", use_container_width=True, type="primary" if st.session_state.doc_type == "CLINICAL_NOTE" else "secondary"):
            st.session_state.doc_type = "CLINICAL_NOTE"
            st.rerun()
    with c4:
        if st.button("💊 Prescription", use_container_width=True, type="primary" if st.session_state.doc_type == "PRESCRIPTION" else "secondary"):
            st.session_state.doc_type = "PRESCRIPTION"
            st.rerun()

    st.markdown("---")

    current_type_name = st.session_state.doc_type.replace("_", " ").title()
    st.write(f"### 📤 Upload {current_type_name}")
    
    uploaded_file = st.file_uploader(
        label=f"Upload your {current_type_name} (PDF, PNG, JPG)", 
        type=["pdf", "png", "jpg", "jpeg"], 
        label_visibility="visible"
    )
    
    if uploaded_file:
        st.markdown("<br>", unsafe_allow_html=True)
        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("📤 Uploading and encrypting document...")
                progress_bar.progress(20)
                time.sleep(0.5)
                status_text.text("🧬 Extracting clinical biomarkers...")
                progress_bar.progress(40)
                time.sleep(0.5)
                status_text.text("🧠 Running clinical reasoning models...")
                progress_bar.progress(60)
                
                file_bytes = uploaded_file.getvalue()
                result = st.session_state.orchestrator.run_pipeline(file_bytes, st.session_state.doc_type)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis Complete!")
                time.sleep(0.5)
                
                if "error" in result:
                    if "429" in str(result.get("details", "")) or "quota" in str(result.get("details", "")).lower():
                        st.warning("📉 **Server Busy:** The AI is experiencing heavy traffic. Please wait 30 seconds and try again.")
                    else:
                        st.error(f"⚠️ **System Alert:** {result.get('error')}")
                        st.code(result.get('details'), language="text")
                else:
                    st.session_state.analysis_result = result
                    st.session_state.chat_history = [{"role": "assistant", "content": f"Hello! I am Dr. Diagna. I've analyzed the {current_type_name}. I see some findings that might need attention. How can I help you?"}]
                    navigate_to("Dashboard")
                    st.rerun()

# === PAGE 2: DASHBOARD ===
elif st.session_state.current_page == "Dashboard":
    if not st.session_state.analysis_result:
        navigate_to("Home")
        st.rerun()
    
    result = st.session_state.analysis_result
    
    # KPI Row
    critical_count = len(result.get("critical_findings", []))
    warning_count = len(result.get("warnings", []))
    
    if critical_count > 0:
        risk_color = "#ff6b6b"
        risk_label = "HIGH RISK"
        risk_icon = "🔴"
        risk_bg = "#fff5f5"
    elif warning_count > 0:
        risk_color = "#fcc419"
        risk_label = "MODERATE RISK"
        risk_icon = "🟡"
        risk_bg = "#fff9db"
    else:
        risk_color = "#20c997"
        risk_label = "HEALTHY"
        risk_icon = "🟢"
        risk_bg = "#e6fcf5"

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid {risk_color};">
            <h4 style="margin:0; color: #868e96; font-size: 0.8rem; font-weight: 600;">OVERALL STATUS</h4>
            <h2 style="margin:0; font-size: 1.6rem; color: {risk_color}; font-weight: 700;">{risk_icon} {risk_label}</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #ff6b6b;">
            <h4 style="margin:0; color: #868e96; font-size: 0.8rem; font-weight: 600;">CRITICAL ALERTS</h4>
            <h2 style="margin:0; font-size: 1.6rem; color: #ff6b6b; font-weight: 700;">{critical_count} <span style="font-size: 1rem; color: #adb5bd; font-weight: 400;">Issues</span></h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #339af0;">
            <h4 style="margin:0; color: #868e96; font-size: 0.8rem; font-weight: 600;">DOCUMENT DATE</h4>
            <h2 style="margin:0; font-size: 1.6rem; color: #339af0; font-weight: 700;">{datetime.now().strftime('%d %b')} <span style="font-size: 1rem; color: #adb5bd; font-weight: 400;">{datetime.now().strftime('%Y')}</span></h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Main Grid
    row2_col1, row2_col2 = st.columns([2, 1])
    with row2_col1:
        st.subheader("📋 Clinical Summary")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 25px; border-radius: 12px; border: 1px solid #e9ecef;">
            <p style="font-size: 1.1rem; line-height: 1.6; color: #343a40;">{result.get("patient_summary", "Analysis pending...")}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔊 Listen to Audio Briefing", use_container_width=True):
             with st.spinner("Generating audio analysis..."):
                diagnosis_list = result.get("diagnosis_section", [])
                if diagnosis_list:
                    top_condition = diagnosis_list[0].get("condition", "Unknown Condition")
                    explanation = diagnosis_list[0].get("explanation", "")
                    audio_script = f"Attention. Based on the analysis, the potential diagnosis is {top_condition}. {explanation}. "
                else:
                    audio_script = "No clear diagnosis was found. "
                if critical_count > 0:
                    audio_script += f"I have detected {critical_count} critical alerts. "
                    for alert in result.get("critical_findings", []):
                        audio_script += f"{alert}. "
                
                audio_bytes = generate_audio_summary(audio_script)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")

    with row2_col2:
        st.subheader("📥 Actions")
        pdf_bytes = create_pdf_report(result)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"Diagnox_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"**Patient:** {result.get('metadata', {}).get('patient_name', 'Unknown')}")

    st.markdown("---")

    if result.get("critical_findings"):
        st.subheader(f"🚨 Critical Findings ({critical_count})")
        for finding in result["critical_findings"]:
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 8px; background-color: #fff5f5; border-left: 4px solid #ff6b6b; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <span style="color: #fa5252; font-weight: bold; font-size: 1.1rem;">⚠️ ALERT:</span> <span style="color: #495057;">{finding}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.subheader("💡 Recommended Next Steps")
    recs = result.get("recommendations", {})
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("**🩺 Medical Actions**")
        if recs.get("medical_next_steps"):
            for step in recs.get("medical_next_steps", []):
                st.markdown(f"✅ {step}")
        else:
            st.markdown("No immediate medical actions needed.")
    with r2:
        st.markdown("**🥗 Lifestyle Adjustments**")
        if recs.get("lifestyle_actions"):
            for step in recs.get("lifestyle_actions", []):
                st.markdown(f"🌿 {step}")
        else:
            st.markdown("Maintain current healthy lifestyle.")

# === PAGE 3: DEEP DIVE ===
elif st.session_state.current_page == "Deep Dive":
    if not st.session_state.analysis_result:
        navigate_to("Home")
        st.rerun()
        
    result = st.session_state.analysis_result
    st.title("🔬 Deep Dive Analysis")
    st.markdown("Detailed biomarkers and clinical indicators.")
    
    diagnosis_data = result.get("diagnosis_section", [])
    if diagnosis_data:
        with st.expander("💡 Clinical Reasoning", expanded=True):
            st.info("This section explains *why* the AI flagged certain risks.")
            for diagnosis in diagnosis_data:
                st.markdown(f"**{diagnosis.get('condition')}** ({diagnosis.get('likelihood')})")
                st.caption(diagnosis.get('explanation'))
                st.markdown("---")

    st.subheader("📌 Biomarkers by System")
    grouped_data = result.get("grouped_findings", {})
    if grouped_data:
        for category, findings in grouped_data.items():
            with st.expander(f"{category} ({len(findings)} markers)", expanded=False):
                for item in findings:
                    c1, c2, c3 = st.columns([3, 2, 5])
                    with c1:
                        st.markdown(f"**{item.get('name')}**")
                        ref_range = item.get('reference_range', 'N/A')
                        st.caption(f"Value: {item.get('value')} | **Standard: {ref_range}**")
                    with c2:
                        status = item.get('status', 'NORMAL')
                        color_class = f"status-{status}"
                        st.markdown(f"<span class='status-badge {color_class}'>{status}</span>", unsafe_allow_html=True)
                    with c3:
                        score = item.get('severity_score', 0)
                        bar_color = "#20c997"
                        if score > 20: bar_color = "#fcc419"
                        if score > 60: bar_color = "#ff6b6b"
                        
                        st.markdown(f"""
                            <div style="background-color: #e9ecef; border-radius: 5px; height: 10px; width: 100%;">
                                <div style="background-color: {bar_color}; width: {score}%; height: 100%; border-radius: 5px;"></div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---")
    else:
        if "lab_results" in result:
             for item in result["lab_results"]:
                st.write(f"**{item.get('parameter')}**: {item.get('value')} ({item.get('status')})")
        else:
             st.info("No detailed biomarkers detected.")

# ==========================================
# 💬 PHASE 3: DR. DIAGNA INTELLIGENT CHAT
# ==========================================

# 1. THE FLOATING POPOVER (This creates the button)
# The CSS above targets [data-testid="stPopover"] to make it fixed and styled.
# We pass an empty label " " so the button is created, but we fill it with CSS.
with st.popover(" ", help="Ask Dr. Diagna"):
    
    # --- HEADER ---
    h1, h2 = st.columns([3, 2])
    with h1:
        st.markdown("### 👩‍⚕️ Dr. Diagna")
        st.caption("AI Medical Assistant")
    with h2:
        selected_language = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], label_visibility="collapsed")
    
    st.markdown("---")

    # --- CHAT HISTORY ---
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.chat_history:
            if st.session_state.analysis_result:
                st.info("👋 Hi! I'm ready to answer questions about your report.")
            else:
                st.info("👋 Hi! Please upload a medical report so I can analyze it for you.")
        
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

    # --- QUICK CHIPS (UPDATED LOGIC) ---
    final_prompt = None
    
    # CASE 1: Document Uploaded (Context-Aware Chips)
    if st.session_state.analysis_result:
        st.markdown("**Quick Actions:**")
        chip_cols = st.columns(3)
        user_choice = None
        
        if chip_cols[0].button("🧬 Explain Diagnosis", key="chip_1"):
            user_choice = "Explain the diagnosis in simple terms."
        if chip_cols[1].button("🥗 Diet Plan", key="chip_2"):
            user_choice = "What should I eat based on these results?"
        if chip_cols[2].button("⚠️ Precautions", key="chip_3"):
            user_choice = "What precautions should I take?"
        
        if user_choice:
            final_prompt = user_choice

    # CASE 2: No Document Yet (General Chips)
    else:
        st.markdown("**Common Questions:**")
        chip_cols = st.columns(3)
        user_choice = None
        
        if chip_cols[0].button("📋 What can you analyze?", key="chip_gen_1"):
            user_choice = "What kind of medical reports can you analyze?"
        if chip_cols[1].button("🔒 Is my data safe?", key="chip_gen_2"):
            user_choice = "How do you ensure patient privacy?"
        if chip_cols[2].button("🧪 Sample Analysis", key="chip_gen_3"):
            user_choice = "Tell me about a hypothetical high glucose case."
            
        if user_choice:
            final_prompt = user_choice

    # --- INPUT AREA ---
    prompt = st.chat_input("Ask Dr. Diagna...")
    
    if prompt and not final_prompt:
        final_prompt = prompt

    if final_prompt:
        st.session_state.chat_history.append({"role": "user", "content": final_prompt})
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.write(final_prompt)
        
        if st.session_state.analysis_result:
            context = str(st.session_state.analysis_result)
        else:
            context = "User has NOT uploaded a file yet. Kindly ask them to upload a PDF lab report."

        with st.chat_message("assistant", avatar="🤖"):
             with st.spinner("Thinking..."):
                try:
                    full_response = st.session_state.dr_ai_agent.ask(
                        final_prompt, 
                        context, 
                        st.session_state.chat_history, 
                        language=selected_language
                    )
                    st.write_stream(stream_data(full_response))
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")