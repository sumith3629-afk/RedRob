import os
import io
import asyncio
import numpy as np
import streamlit as st
from PIL import Image

# Import stage 1 and stage 2 modules
from crop_detector import MobileNetV2Classifier
from orchestrator import terrapulse_app, format_agent_event

# Import ADK elements
from google.adk.runners import InMemoryRunner
from google.genai import types

# Page Config
st.set_page_config(
    page_title="TerraPulse | Agro-Ecological Climate Resilience Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for Premium Dark UI
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap');

    /* Font Setup */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3, .title-text {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Core Page Styling */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0e1626 0%, #060a12 100%);
        color: #e2e8f0;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(16, 26, 48, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    
    /* Glow Headers */
    .glow-header {
        background: linear-gradient(135deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }

    /* Custom Terminal styling */
    .terminal-console {
        background-color: #0b0f19 !important;
        border: 1px solid #1f293d !important;
        border-radius: 10px !important;
        padding: 15px !important;
        color: #60EFFF !important;
        font-family: 'Space Grotesk', monospace !important;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Metrics panel styling */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00FF87;
        font-family: 'Space Grotesk', sans-serif;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar styling */
    div[data-testid="stSidebar"] {
        background-color: #080c16 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Branding
with st.sidebar:
    st.markdown("<h2 class='glow-header' style='font-size: 2.2rem; margin-bottom: 5px;'>TerraPulse</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top:0;'>Agro-Ecological Climate Resilience</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 🖥️ Edge Classifier Telemetry")
    st.info("MobileNetV2 Backbone active: Input Tensor (1, 224, 224, 3) normalized to range [-1, 1].")
    
    st.markdown("### 🤖 Multi-Agent Orchestrator")
    st.success("ResearchCoordinator (gemini-2.5-pro)\n\nEcoRemediationSpecialist (gemini-2.5-flash)\n\nMarketSupplyBroker (gemini-2.5-flash)")
    st.divider()
    
    st.caption("Developed for NextGenHacks. Submission ready.")

# Header Section
st.markdown("<h1 class='glow-header' style='font-size: 3.5rem; margin-bottom: 5px;'>TerraPulse Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.2rem; margin-top: 0;'>Multi-Modal Deep-Learning Agro-Ecological Climate Resilience Platform</p>", unsafe_allow_html=True)

# Main Grid Layout
col1, col2 = st.columns([1, 1], gap="large")

# State Management for Classifier Output and Dossier
if "classifier_output" not in st.session_state:
    st.session_state.classifier_output = None
if "resilience_dossier" not in st.session_state:
    st.session_state.resilience_dossier = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📸 Leaf Imagery Input")
    
    uploaded_file = st.file_uploader(
        "Upload crop leaf photograph (PNG, JPG, JPEG)", 
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    
    use_demo = st.button("🌱 Load Demo Crop Leaf Image")
    
    image_to_process = None
    
    if uploaded_file is not None:
        image_to_process = Image.open(uploaded_file)
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image_to_process.save(img_byte_arr, format='PNG')
        st.session_state.image_bytes = img_byte_arr.getvalue()
    elif use_demo:
        demo_path = "tiny_image.png"
        if os.path.exists(demo_path):
            image_to_process = Image.open(demo_path)
            with open(demo_path, "rb") as f:
                st.session_state.image_bytes = f.read()
        else:
            st.error("Demo image tiny_image.png not found in directory.")

    if image_to_process:
        st.image(image_to_process, caption="Uploaded Leaf Photograph", use_container_width=True)
        
        # Ingest and classify
        if st.button("🔥 Run TensorFlow MobileNetV2 Classifier", use_container_width=True):
            with st.spinner("Executing edge model forward pass..."):
                classifier = MobileNetV2Classifier()
                result = classifier.predict(st.session_state.image_bytes)
                st.session_state.classifier_output = result
    else:
        st.write("Please upload a file or click the demo button to initialize.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Edge TensorFlow Telemetry")
    
    if st.session_state.classifier_output:
        out = st.session_state.classifier_output
        
        # Display key metrics
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"<span class='metric-label'>Detected Class</span><br><span class='metric-value'>{out.get('detected_class')}</span>", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"<span class='metric-label'>Confidence</span><br><span class='metric-value'>{out.get('confidence_score')*100:.2f}%</span>", unsafe_allow_html=True)
            
        st.write("")
        m_col3, m_col4 = st.columns(2)
        with m_col3:
            st.markdown(f"<span class='metric-label'>Crop Type</span><br><span class='metric-value'>{out.get('crop_type')}</span>", unsafe_allow_html=True)
        with m_col4:
            st.markdown(f"<span class='metric-label'>Severity</span><br><span class='metric-value' style='color:#F87171;'>{out.get('severity')}</span>", unsafe_allow_html=True)
        
        st.divider()
        
        # Compute real NumPy channel histograms for the preprocessed input
        if st.session_state.image_bytes:
            img = Image.open(io.BytesIO(st.session_state.image_bytes)).resize((224, 224))
            arr = np.array(img, dtype=np.float32)
            
            # Make sure it's 3 channels
            if len(arr.shape) == 3 and arr.shape[2] >= 3:
                r_mean = float(np.mean(arr[:, :, 0]))
                g_mean = float(np.mean(arr[:, :, 1]))
                b_mean = float(np.mean(arr[:, :, 2]))
                
                st.markdown("**Preprocessed Color Channel Means (MobileNetV2 scale: [-1, 1]):**")
                norm_means = {
                    "Red Channel": (r_mean / 127.5) - 1.0,
                    "Green Channel": (g_mean / 127.5) - 1.0,
                    "Blue Channel": (b_mean / 127.5) - 1.0
                }
                
                st.bar_chart(norm_means)
            else:
                st.info("Color channel visualization skipped for single-channel/grayscale image.")
    else:
        st.warning("Awaiting MobileNetV2 classification output.")
    st.markdown("</div>", unsafe_allow_html=True)

# Agent Network section
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 🧠 ADK Hierarchical Agent Orchestrator Pipeline")

if st.session_state.classifier_output:
    if st.button("🚀 Trigger Orchestrator Agent Network", use_container_width=True):
        st.markdown("**Real-Time ADK Monologue & Execution Trace:**")
        log_placeholder = st.empty()
        
        async def run_gui_agent_pipeline():
            runner = InMemoryRunner(app=terrapulse_app)
            runner.auto_create_session = True
            payload = st.session_state.classifier_output
            
            prompt = (
                f"Ingest the following crop disease telemetry and coordinate the full agro-ecological review: "
                f"Detected Class: {payload.get('detected_class')}, Crop Type: {payload.get('crop_type')}, "
                f"Severity: {payload.get('severity')}, Confidence Score: {payload.get('confidence_score')}, "
                f"Status: {payload.get('status')}."
            )
            
            log_text = "🟢 [ADK-ORCHESTRATOR] Connecting to Master ResearchCoordinator...\n\n"
            log_placeholder.code(log_text, language="markdown")
            
            dossier_content = ""
            
            try:
                # Async generator over ADK events
                async for event in runner.run_async(
                    user_id="streamlit_runner",
                    session_id="streamlit_session_active",
                    new_message=types.UserContent(parts=[types.Part(text=prompt)])
                ):
                    event_log = format_agent_event(event)
                    if event_log:
                        log_text += f"{event_log}\n\n"
                        # Stream directly into the log container
                        log_placeholder.code(log_text, language="markdown")
                        
                    # Extract the final response text from ResearchCoordinator
                    if event.author == "ResearchCoordinator" and event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text and not getattr(part, "thought", False):
                                dossier_content = part.text
                                
            except Exception as e:
                error_msg = f"❌ [Runner Exception] {e}"
                log_placeholder.code(log_text + f"\n{error_msg}", language="markdown")
            finally:
                await runner.close()
                
            return dossier_content

        # Run async routine inside the Streamlit synchronous execution cycle
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            final_dossier = loop.run_until_complete(run_gui_agent_pipeline())
            st.session_state.resilience_dossier = final_dossier
        finally:
            loop.close()
            
else:
    st.info("Run the MobileNetV2 edge classifier first to generate the necessary payload context.")
st.markdown("</div>", unsafe_allow_html=True)

# Final Dossier Section
if st.session_state.resilience_dossier:
    st.markdown("<div class='glass-card' style='border: 1px solid rgba(0, 255, 135, 0.3);'>", unsafe_allow_html=True)
    st.markdown("### 📋 Final Agro-Ecological Climate Resilience Dossier")
    st.markdown(st.session_state.resilience_dossier)
    
    st.download_button(
        "📥 Download Resilience Dossier (MD)",
        data=st.session_state.resilience_dossier,
        file_name="terrapulse_resilience_dossier.md",
        mime="text/markdown",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
