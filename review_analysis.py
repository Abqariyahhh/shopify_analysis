import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv

# ====== LOAD .ENV FILE ======
load_dotenv()

# ====== CONFIG ======
RAW_FILE = "raw_reviews.csv"
CLEAN_FILE = "cleaned_reviews.csv"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"  # You can change this if needed


# ====== CLEAN DATA ======
def clean_data():
    print("Cleaning data...")
    try:
        df = pd.read_csv(RAW_FILE)
    except FileNotFoundError:
        raise FileNotFoundError(f"{RAW_FILE} not found. Place raw_reviews.csv in the same folder.")

    # Convert timestamps to uniform datetime format
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Normalize product/category names
    df["Product Category"] = df["Product Category"].fillna("Unknown").str.title().str.strip()
    df["Product Name"] = df["Product Name"].fillna("Unknown").str.title().str.strip()

    # Remove blank or too-short reviews
    df = df[df["Review Content"].notna() & (df["Review Content"].str.len() > 3)]

    # Fix ratings (fill missing with median)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    median_rating = df["Rating"].median()
    df["Rating"] = df["Rating"].fillna(median_rating)

    # Save cleaned data
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Cleaned data saved to {CLEAN_FILE}")
    return df


# ====== OPENROUTER CALL ======
def call_openrouter(prompt):
    if not OPENROUTER_API_KEY:
        return "❌ OpenRouter API key not set. Add it to .env as OPENROUTER_API_KEY."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI summary failed: {e}"


# ====== STAKEHOLDER QUESTIONS ======
def stakeholder_insights(df):
    # Q1: Categories with most 1-star reviews in Canada
    canada_1_star = df[(df["Rating"] == 1) & (df["Shipping Country"].str.lower() == "canada")]
    q1 = canada_1_star["Product Category"].value_counts()

    # Q2: Correlation between order value & rating
    df["Order Value"] = pd.to_numeric(df["Order Value"], errors="coerce")
    correlation = df["Order Value"].corr(df["Rating"])

    # Q3: Top complaints & compliments (AI summary)
    sample_reviews = "\n".join(df["Review Content"].sample(min(50, len(df))).tolist())
    prompt = f"""
Given these reviews, summarize:
1. Top 5 complaints
2. Top 5 compliments
Reviews:\n{sample_reviews}
"""
    summary = call_openrouter(prompt)

    # Q4: Fulfillment statuses most associated with negative feedback
    neg_status = df[df["Rating"] <= 2]["Fulfillment Status"].value_counts()

    return q1, correlation, summary, neg_status


# ====== MAIN SCRIPT ======
if __name__ == "__main__":
    df = clean_data()
    q1, correlation, summary, neg_status = stakeholder_insights(df)

    print("\n=== Categories with most 1-star reviews in Canada ===")
    print(q1)
    print("\n=== Correlation between Order Value & Rating ===")
    print(correlation)
    print("\n=== Top Complaints & Compliments ===")
    print(summary)
    print("\n=== Fulfillment statuses linked to negative feedback ===")
    print(neg_status)
