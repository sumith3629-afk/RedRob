from dotenv import load_dotenv
load_dotenv()
import os

try:
    from kaggle_secrets import UserSecretsClient
    GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print("Gemini API key setup complete (via Kaggle Secrets).")
except ImportError:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        print("Gemini API key setup complete (via local .env).")
    else:
        print("Error: GOOGLE_API_KEY not found in local environment or .env file.")
except Exception as e:
    print(
        f"Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your Kaggle secrets. Details: {e}"
    )


from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

root_agent = Agent(
    name = "helpful_assistant",
    model = Gemini(
        model ="gemini-2.5-flash-lite",
        retry_options = retry_config
    ),
    description="A model that can answer simple general questions",
    instruction="You are a helpful AI assistant. Use Google search if you are unsure.",
    tools =[google_search],
)
