import json

notebook_path = r"c:\Users\karakavalasa sumith\Desktop\agent\.venv\Scripts\redrob\redrob.ipynb"

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

honeypot_code = [
    "# --- HONEYPOT DETECTOR AGENT ---\n",
    "import pandas as pd\n",
    "import json\n",
    "\n",
    "def honeypot_detector_agent(candidate):\n",
    "    \"\"\"\n",
    "    Expert Agent: Inspects a candidate's profile for synthetic inconsistencies.\n",
    "    Returns: True if candidate is a honeypot (trap), False if they are a real candidate.\n",
    "    \"\"\"\n",
    "    # 1. Zero-duration expert/advanced skills\n",
    "    skills = candidate.get('skills', [])\n",
    "    zero_duration_expert_count = 0\n",
    "    for skill in skills:\n",
    "        proficiency = skill.get('proficiency', '').lower()\n",
    "        duration = skill.get('duration_months', 0)\n",
    "        if proficiency in ['expert', 'advanced'] and duration == 0:\n",
    "            zero_duration_expert_count += 1\n",
    "            \n",
    "    if zero_duration_expert_count >= 3:\n",
    "        return True\n",
    "\n",
    "    # 2. Job History Calendar Verification (e.g. 8 years at a company joined 3 years ago)\n",
    "    current_date = pd.to_datetime('2026-06-18')\n",
    "    career_history = candidate.get('career_history', [])\n",
    "    for job in career_history:\n",
    "        try:\n",
    "            start_date = pd.to_datetime(job.get('start_date'))\n",
    "            end_date = pd.to_datetime(job.get('end_date'))\n",
    "            if pd.isnull(end_date):\n",
    "                end_date = current_date\n",
    "            stated_months = job.get('duration_months', 0)\n",
    "            calendar_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1\n",
    "            if stated_months > calendar_months + 6:\n",
    "                return True\n",
    "        except Exception:\n",
    "            pass\n",
    "\n",
    "    # 3. Total Experience Validation\n",
    "    try:\n",
    "        profile_years = candidate.get('profile', {}).get('years_of_experience', 0.0)\n",
    "        total_job_months = sum(j.get('duration_months', 0) for j in career_history)\n",
    "        actual_years = total_job_months / 12.0\n",
    "        if profile_years > actual_years + 3.0:\n",
    "            return True\n",
    "    except Exception:\n",
    "        pass\n",
    "\n",
    "    return False\n",
    "\n",
    "# Load the raw candidates list to test our agent\n",
    "path = r\"C:\\Users\\karakavalasa sumith\\Downloads\\[PUB] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\candidates.jsonl\"\n",
    "print(\"Loading candidates pool...\")\n",
    "all_candidates = []\n",
    "with open(path, 'r', encoding='utf-8') as f:\n",
    "    for i, line in enumerate(f):\n",
    "        if line.strip():\n",
    "            all_candidates.append(json.loads(line))\n",
    "        if i >= 10000:  # Test on a sample of 10,000 candidates first\n",
    "            break\n",
    "\n",
    "print(f\"Testing Honeypot Agent on a sample of {len(all_candidates)} candidates...\")\n",
    "valid_candidates = [c for c in all_candidates if not honeypot_detector_agent(c)]\n",
    "honeypots_count = len(all_candidates) - len(valid_candidates)\n",
    "\n",
    "print(f\"✅ Honeypots identified and removed: {honeypots_count}\")\n",
    "print(f\"✅ Clean candidates remaining: {len(valid_candidates)}\")\n"
]

if len(notebook.get("cells", [])) > 3:
    notebook["cells"][3]["source"] = honeypot_code
    notebook["cells"][3]["outputs"] = []
    notebook["cells"][3]["execution_count"] = None

with open(notebook_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print("Notebook cell 4 updated successfully!")
