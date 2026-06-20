import os
import asyncio
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import google_search
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.genai import types

# Ensure GOOGLE_API_KEY is in os.environ for the ADK SDK
if "GOOGLE_API_KEY" not in os.environ:
    # If not loaded by dotenv, raise error
    raise ValueError("GOOGLE_API_KEY not found in environment. Please check your .env file.")

# Define HTTP retry options for API stability
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# -------------------------------------------------------------
# STAGE 2 TOOL: NumPy Eco-Remediation Ratios Calculator
# -------------------------------------------------------------
def compute_remediation_ratios(disease_class: str, severity: str) -> dict:
    """
    Computes chemical and fertilizer remediation ratios using matrix operations.
    
    Args:
        disease_class: The detected crop disease class (e.g. Tomato__Target_Spot).
        severity: The disease severity level ('Low', 'Medium', 'High').
        
    Returns:
        A dictionary containing fertilizer ratios, treatment products, and application schedules.
    """
    # 1. Base N-P-K adjustments (N, P, K in kg/hectare) for specific classes
    # Rows: 0 -> Tomato__Target_Spot, 1 -> Tomato__Late_Blight, 2 -> Potato__Early_Blight
    # Columns: [N adjustment, P adjustment, K adjustment]
    nutrient_matrix = np.array([
        [-15.0, 25.0, 30.0],  # Tomato Target Spot: Reduce nitrogen, increase phosphorus & potassium
        [-20.0, 15.0, 25.0],  # Tomato Late Blight: Significant nitrogen reduction, moderate P & K increase
        [-10.0, 20.0, 20.0]   # Potato Early Blight: Moderate adjustment
    ], dtype=np.float64)
    
    disease_map = {
        "Tomato__Target_Spot": 0,
        "Tomato__Late_Blight": 1,
        "Potato__Early_Blight": 2
    }
    
    disease_idx = disease_map.get(disease_class, 0)
    base_nutrients = nutrient_matrix[disease_idx]
    
    # 2. Severity multiplier scalar
    severity_factors = {
        "low": 0.5,
        "medium": 1.0,
        "high": 2.0
    }
    sev_factor = severity_factors.get(severity.lower(), 1.0)
    
    # NumPy operation: Scale baseline adjustments by severity factor
    final_npk = base_nutrients * sev_factor
    
    # 3. Chemical fungicide dosage matrix (ml per Liter of water)
    # Rows: Target Spot, Late Blight, Early Blight
    # Columns: Chlorothalonil, Copper_Hydroxide, Mancozeb
    chemical_matrix = np.array([
        [2.0, 1.5, 0.0],  # Target spot uses Chlorothalonil and Copper
        [0.0, 2.5, 2.0],  # Late blight uses Copper and Mancozeb
        [1.5, 0.0, 2.5]   # Early blight uses Chlorothalonil and Mancozeb
    ], dtype=np.float64)
    
    base_chemicals = chemical_matrix[disease_idx]
    final_chemicals = base_chemicals * sev_factor
    
    # 4. Compute total required volumes based on standard 500 L/hectare spray rate
    spray_rate_l_per_hectare = 500.0
    total_chemicals_ml = final_chemicals * spray_rate_l_per_hectare
    
    result = {
        "disease_class": disease_class,
        "severity": severity,
        "npk_adjustments_kg_per_hectare": {
            "Nitrogen (N)": float(final_npk[0]),
            "Phosphorus (P)": float(final_npk[1]),
            "Potassium (K)": float(final_npk[2])
        },
        "chemical_treatment_concentration_ml_per_L": {
            "Chlorothalonil": float(final_chemicals[0]),
            "Copper_Hydroxide": float(final_chemicals[1]),
            "Mancozeb": float(final_chemicals[2])
        },
        "total_spray_chemical_requirement_ml_per_hectare": {
            "Chlorothalonil": float(total_chemicals_ml[0]),
            "Copper_Hydroxide": float(total_chemicals_ml[1]),
            "Mancozeb": float(total_chemicals_ml[2])
        },
        "application_interval_days": 14 if severity.lower() == "low" else (10 if severity.lower() == "medium" else 7),
        "soil_moisture_limit_pct": 65.0,
        "calculation_engine": "NumPy Vector/Matrix Engine"
    }
    return result

# -------------------------------------------------------------
# STAGE 2 MULTI-AGENT DEFINITION
# -------------------------------------------------------------

# Sub-Agent 1: Eco-Remediation Specialist
eco_remediation_specialist = Agent(
    name="EcoRemediationSpecialist",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="Calculates specific chemical and fertilizer remediation ratios based on disease classification.",
    instruction=(
        "You are the EcoRemediationSpecialist. Your job is to compute precise remediation ratios "
        "and fertilizer N-P-K adjustments for the crop disease. You MUST call the "
        "`compute_remediation_ratios` tool. Explain the output of the tool mathematically, highlighting the "
        "implications of the N-P-K ratios and chemical applications for the farmer."
    ),
    tools=[FunctionTool(compute_remediation_ratios)]
)

# Sub-Agent 2: Market Supply Broker
market_supply_broker = Agent(
    name="MarketSupplyBroker",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="Scrapes regional crop shortages and price fluctuations.",
    instruction=(
        "You are the MarketSupplyBroker. Use the `google_search` tool to live-scrape regional crop shortages, "
        "price dynamics, and mandi price fluctuations for the requested crop type (e.g. 'Tomato'). "
        "Provide a summary of the economic risks, current market prices, and potential supply-chain issues."
    ),
    tools=[google_search]
)

# Master Agent: Research Coordinator
research_coordinator = Agent(
    name="ResearchCoordinator",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="Coordinates diagnostic intelligence and acts as the orchestrator.",
    instruction=(
        "You are the ResearchCoordinator, the master orchestrator of TerraPulse. "
        "You receive raw crop leaf classification data from Stage 1: detected crop disease class, crop type, confidence score, and severity. "
        "You MUST orchestrate the following workflow: "
        "1. Consult the `EcoRemediationSpecialist` sub-agent tool to obtain precise chemical/fertilizer remediation ratios. "
        "2. Consult the `MarketSupplyBroker` sub-agent tool to assess the economic impact and regional market trends for this crop. "
        "3. Synthesize the findings into a comprehensive, elite, multi-modal 'Agro-Ecological Climate Resilience Dossier' written in Markdown. "
        "Format the Dossier with professional headings, tables, bullet points, and highlight critical insights. "
        "Do NOT attempt to compute ratios or perform searches yourself; rely entirely on your specialized sub-agent tools."
    ),
    tools=[
        AgentTool(eco_remediation_specialist),
        AgentTool(market_supply_broker)
    ]
)

# Initialize the ADK Application
terrapulse_app = App(
    name="TerraPulseAgentNetwork",
    root_agent=research_coordinator
)

# -------------------------------------------------------------
# EVENT FORMATTER & RUNNER GENERATOR
# -------------------------------------------------------------
def format_agent_event(event) -> str:
    """
    Parses an ADK Event object and outputs a formatted string representation of
    the agent's thoughts, tool calls, or final outputs.
    """
    if not event.content or not event.content.parts:
        return ""
    
    author = event.author
    logs = []
    
    for part in event.content.parts:
        # Check for model thoughts (internal monologue)
        if hasattr(part, "thought") and part.thought and part.text:
            logs.append(f"🧠 [{author} - Internal Monologue]\n{part.text.strip()}")
        # Check for normal text response
        elif part.text:
            logs.append(f"💬 [{author}]\n{part.text.strip()}")
        # Check for tool/function calls
        elif part.function_call:
            call = part.function_call
            logs.append(f"🛠️ [{author} -> Calling Tool: {call.name}]\nArguments: {call.args}")
        # Check for tool/function responses
        elif part.function_response:
            resp = part.function_response
            logs.append(f"📥 [Tool Response from: {resp.name}]\nResult: {resp.response}")
            
    return "\n".join(logs)

async def run_agent_pipeline(payload: dict):
    """
    Runs the ADK agent pipeline and yields formatted log messages as they are emitted by the runner.
    """
    runner = InMemoryRunner(app=terrapulse_app)
    runner.auto_create_session = True
    
    prompt = (
        f"Ingest the following crop disease telemetry and coordinate the full agro-ecological review: "
        f"Detected Class: {payload.get('detected_class')}, Crop Type: {payload.get('crop_type')}, "
        f"Severity: {payload.get('severity')}, Confidence Score: {payload.get('confidence_score')}, "
        f"Status: {payload.get('status')}."
    )
    
    try:
        # Run standard run_async to capture the full stream of events
        async for event in runner.run_async(
            user_id="nextgen_user",
            session_id="terrapulse_session",
            new_message=types.UserContent(parts=[types.Part(text=prompt)])
        ):
            log_str = format_agent_event(event)
            if log_str:
                yield log_str
    except Exception as e:
        yield f"❌ [Runner Error] An exception occurred during execution: {e}"
    finally:
        await runner.close()
