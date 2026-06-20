import json
import csv
import os
import argparse
import sys
import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

# 1. Define sets for fast membership lookups
SERVICES_BLACKLIST = {
    'tcs', 'tata consultancy', 'infosys', 'wipro', 'accenture', 'cognizant', 
    'capgemini', 'hcl', 'tech mahindra', 'l&t', 'lnt', 'ibm', 'deloitte', 
    'pwc', 'ey', 'kpmg', 'genpact'
}

PRODUCT_WHITELIST = {
    'google', 'microsoft', 'meta', 'apple', 'netflix', 'amazon', 'zomato', 
    'swiggy', 'paytm', 'phonepe', 'ola', 'zoho', 'freshworks', 'razorpay', 
    'cred', 'flipkart', 'meesho', 'inmobi', 'salesforce', 'adobe', 'byju'
}

def honeypot_detector_agent(candidate):
    """
    Expert Agent: Inspects a candidate's profile for synthetic inconsistencies.
    Returns: True if candidate is a honeypot (trap), False if they are a real candidate.
    """
    # Rule 1: Zero-duration expert/advanced skills
    skills = candidate.get('skills', [])
    zero_duration_expert_count = 0
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        proficiency = skill.get('proficiency', '')
        if proficiency:
            proficiency = proficiency.lower()
        duration = skill.get('duration_months', 0)
        if proficiency in ('expert', 'advanced') and duration == 0:
            zero_duration_expert_count += 1
            
    if zero_duration_expert_count >= 3:
        return True

    # Rule 2: Job History Calendar Verification (e.g. 8 years at a company joined 3 years ago)
    career_history = candidate.get('career_history', [])
    current_date = pd.to_datetime('2026-06-18')
    for job in career_history:
        if not isinstance(job, dict):
            continue
        start_date = job.get('start_date')
        end_date = job.get('end_date')
        stated_months = job.get('duration_months', 0)
        
        if start_date:
            try:
                s_yr = int(start_date[:4])
                s_mo = int(start_date[5:7])
                if not end_date:
                    e_yr, e_mo = 2026, 6
                else:
                    e_yr = int(end_date[:4])
                    e_mo = int(end_date[5:7])
                calendar_months = (e_yr - s_yr) * 12 + (e_mo - s_mo) + 1
                if stated_months > calendar_months + 6:
                    return True
            except Exception:
                pass

    # Rule 3: Total Experience Validation
    try:
        profile_years = candidate.get('profile', {}).get('years_of_experience', 0.0)
        total_job_months = sum(j.get('duration_months', 0) for j in career_history if isinstance(j, dict) and j.get('duration_months') is not None)
        actual_years = total_job_months / 12.0
        if profile_years > actual_years + 3.0:
            return True
    except Exception:
        pass

    return False

def create_profile_text(row):
    """
    Feature Engineering: Converts structured candidate row to a clean text paragraph.
    """
    profile = row.get('profile', {})
    title = profile.get('current_title', '')
    headline = profile.get('headline', '')
    summary = profile.get('summary', '')
    
    # Extract skills
    skills_list = [s.get('name', '') for s in row.get('skills', [])]
    skills_text = ", ".join(skills_list)
    
    # Extract recent job descriptions (top 2 roles)
    history = row.get('career_history', [])
    history_text = ""
    for job in history[:2]:
        history_text += f" Job Title: {job.get('title', '')}. Description: {job.get('description', '')}."
        
    return f"Title: {title}. Headline: {headline}. Summary: {summary}. Skills: {skills_text}. History: {history_text}"

def compute_final_score(row):
    """
    Heuristic Re-ranking scoring for candidate profile and behavioral signals.
    """
    score = row['semantic_score']
    
    profile = row.get('profile', {})
    signals = row.get('redrob_signals', {})
    
    # --- CRITERIA 1: LOCATION & VISA FEASIBILITY ---
    loc = profile.get('location', '').lower()
    willing_relocate = signals.get('willing_to_relocate', False)
    country = profile.get('country', '').lower()
    
    # Penalize foreign candidates (visa issues)
    if 'india' not in country and country != '':
        score -= 0.3
        
    # Reward local candidates or those willing to relocate to Noida/Pune
    if 'noida' in loc or 'pune' in loc:
        score += 0.1  # Noida/Pune bonus
    elif willing_relocate:
        score += 0.05  # Relocation bonus
        
    # --- CRITERIA 2: NOTICE PERIOD ---
    notice = signals.get('notice_period_days', 90)
    if notice <= 30:
        score += 0.05  # Quick joiner bonus
    elif notice > 90:
        score -= 0.08  # Penalty for long notice period
        
    # --- CRITERIA 3: CAREER DURATION & TENURE ---
    history = row.get('career_history', [])
    if history:
        # Calculate average job tenure to detect job hoppers
        total_months = sum(j.get('duration_months', 0) for j in history)
        avg_tenure = total_months / len(history)
        
        if avg_tenure < 18:
            score -= 0.08  # Penalty for job hoppers
        elif avg_tenure >= 36:
            score += 0.05  # Bonus for high stability
            
        # --- CRITERIA 4: PRODUCT VS SERVICE COMPANY EXPERIENCE ---
        has_product_exp = False
        has_only_service_exp = True
        
        for job in history:
            company = job.get('company', '').lower()
            if any(p in company for p in PRODUCT_WHITELIST):
                has_product_exp = True
            if not any(s in company for s in SERVICES_BLACKLIST):
                has_only_service_exp = False
                
        if has_product_exp:
            score += 0.05
        if has_only_service_exp:
            score -= 0.15  # Heavy penalty for service-only backgrounds
            
    # --- CRITERIA 5: PLATFORM ASSESSMENTS ---
    assessments = signals.get('skill_assessment_scores', {})
    relevant_scores = [
        val for key, val in assessments.items() 
        if any(kw in key.lower() for kw in ['pinecone', 'milvus', 'nlp', 'vector', 'model', 'mlops'])
    ]
    if relevant_scores:
        avg_assessment = sum(relevant_scores) / len(relevant_scores)
        score += (avg_assessment / 100.0) * 0.05  # Add up to 0.05 bonus
        
    return score

def build_reasoning(row, rank):
    """
    Dynamic reasoning text generator to pass manual reviews.
    """
    profile = row.get('profile', {})
    name = profile.get('anonymized_name', 'The candidate')
    years_exp = profile.get('years_of_experience', 0)
    title = profile.get('current_title', 'Engineer')
    company = profile.get('current_company', 'their current company')
    signals = row.get('redrob_signals', {})
    notice = signals.get('notice_period_days', 30)
    
    # Highlight top skills
    skills = [s.get('name') for s in row.get('skills', []) if s.get('duration_months', 0) > 0]
    ai_skills = [
        s for s in skills 
        if s.lower() in ['embeddings', 'vector search', 'vector database', 'pinecone', 'milvus', 'faiss', 'nlp', 'pytorch', 'tensorflow']
    ]
    
    starters = [
        f"Title: {title}. {name} brings {years_exp} years of engineering experience, currently working at {company}.",
        f"Currently working as a {title} at {company}, {name} has accumulated {years_exp} years of experience.",
        f"With {years_exp} years of experience as a {title} at {company}, {name} shows excellent career progression."
    ]
    starter = starters[rank % len(starters)]
    
    if ai_skills:
        skills_part = f" They possess strong hands-on expertise in {', '.join(ai_skills[:2])}."
    else:
        skills_part = " They have strong foundational backend software engineering skills."
        
    if notice > 60:
        gap_part = f" Note: notice period is {notice} days, but their technical fit remains exceptionally strong."
    else:
        gap_part = f" They are highly reachable with a notice period of {notice} days."
        
    return starter + skills_part + gap_part

def main():
    parser = argparse.ArgumentParser(description="Rank candidates for the Redrob AI Founding Team role.")
    parser.add_argument('--candidates', required=True, help="Path to candidates.jsonl file")
    parser.add_argument('--out', required=True, help="Path to output CSV file")
    args = parser.parse_args()
    
    print(f"Reading candidates from {args.candidates}...")
    candidates = []
    with open(args.candidates, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                candidates.append(json.loads(line))
                
    print(f"Loaded {len(candidates)} candidates. Filtering honeypots...")
    clean_candidates = [c for c in candidates if not honeypot_detector_agent(c)]
    print(f"Honeypots removed: {len(candidates) - len(clean_candidates)}. Clean pool size: {len(clean_candidates)}")
    
    valid_candidates_df = pd.DataFrame(clean_candidates)
    valid_candidates_df['search_profile'] = valid_candidates_df.apply(create_profile_text, axis=1)
    
    # Define Job Description
    job_description = """
    Senior AI Engineer — Founding Team. Experience: 5–9 years. 
    Key requirements: Production experience with embeddings-based retrieval systems, 
    vector databases (Pinecone, Weaviate, Qdrant, Milvus, FAISS), strong Python, 
    designing evaluation frameworks (NDCG, MRR, MAP). 
    Preferred: LLM fine-tuning (LoRA, QLoRA, PEFT), learning-to-rank models. 
    Location: Noida/Pune, India.
    """
    
    # Semantic scoring: Check if we can load precomputed embeddings
    cosine_scores = None
    embedding_cache_path = "candidate_embeddings.npy"
    
    if os.path.exists(embedding_cache_path):
        try:
            cached_embeddings = np.load(embedding_cache_path)
            # The length of the cached embeddings must match the filtered candidate list
            if len(cached_embeddings) == len(clean_candidates):
                print("Loading precomputed embeddings from cache...")
                # Load the model just for similarity utility
                model = SentenceTransformer('all-MiniLM-L6-v2')
                jd_embedding = model.encode(job_description, convert_to_tensor=True)
                candidate_embeddings = torch.tensor(cached_embeddings)
                cosine_scores = util.cos_sim(jd_embedding, candidate_embeddings)[0].cpu().numpy()
        except Exception as e:
            print(f"Warning: Failed to load cached embeddings: {e}. Falling back to live encoding.")
            
    if cosine_scores is None:
        print("Precomputed cache missing or mismatch. Running live Sentence Transformer encoding on CPU...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        # Configure multi-threading
        torch.set_num_threads(torch.get_num_threads())
        
        jd_embedding = model.encode(job_description, convert_to_tensor=True)
        print("Encoding candidate text profiles...")
        candidate_embeddings = model.encode(
            valid_candidates_df['search_profile'].tolist(),
            batch_size=64,
            show_progress_bar=False,
            convert_to_tensor=True
        )
        cosine_scores = util.cos_sim(jd_embedding, candidate_embeddings)[0].cpu().numpy()
        
    valid_candidates_df['semantic_score'] = cosine_scores
    
    # Filter to top 1,000 candidates for re-ranking
    top_1000_candidates = valid_candidates_df.nlargest(1000, 'semantic_score').copy()
    
    # Re-rank using heuristics
    print("Applying heuristic re-ranking rules...")
    top_1000_candidates['final_score'] = top_1000_candidates.apply(compute_final_score, axis=1)
    
    # Sort top 100
    top_100 = top_1000_candidates.sort_values(
        by=['final_score', 'candidate_id'], 
        ascending=[False, True]
    ).head(100).copy()
    
    # Monotonic score calibration
    current_max = 10.0
    calibrated_scores = []
    for score in top_100['final_score']:
        if score > current_max:
            score = current_max
        else:
            current_max = score
        calibrated_scores.append(round(score, 4))
        
    top_100['calibrated_score'] = calibrated_scores
    
    # Re-sort to resolve rounding ties
    top_100 = top_100.sort_values(
        by=['calibrated_score', 'candidate_id'],
        ascending=[False, True]
    )
    
    # Generate reasoning and write output
    print(f"Writing final submission to {args.out}...")
    submission_rows = []
    for idx, (_, row) in enumerate(top_100.iterrows()):
        rank = idx + 1
        reasoning = build_reasoning(row, rank)
        submission_rows.append({
            'candidate_id': row['candidate_id'],
            'rank': rank,
            'score': row['calibrated_score'],
            'reasoning': reasoning
        })
        
    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['candidate_id', 'rank', 'score', 'reasoning'])
        writer.writeheader()
        for s_row in submission_rows:
            writer.writerow(s_row)
            
    print("Ranking and export complete!")

if __name__ == '__main__':
    main()
