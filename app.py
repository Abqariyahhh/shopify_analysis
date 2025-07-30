import streamlit as st
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv
from transformers import pipeline
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
from wordcloud import STOPWORDS
import streamlit as st

# ====== ENVIRONMENT VARIABLES ======
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"

# ====== LOAD DATA ======
#@st.cache_data
def load_clean_data():
    return pd.read_csv("cleaned_reviews.csv", parse_dates=["Timestamp"])

df = load_clean_data()

# ====== STREAMLIT TITLE ======
st.title("Shopify Review Insights")
st.markdown("<p style='font-size:18px; color:gray; margin-top:-10px;'>AI-powered analytics for customer feedback</p>", unsafe_allow_html=True)

# ====== FILTERS ======
country = st.selectbox("Country", ["All"] + sorted(df["Shipping Country"].dropna().unique()))
category = st.multiselect("Product Category", sorted(df["Product Category"].unique()))
status = st.multiselect("Fulfillment Status", sorted(df["Fulfillment Status"].unique()))
date_range = st.date_input("Date Range", [df["Timestamp"].min(), df["Timestamp"].max()])
rating_range = st.slider("Rating Range", 1, 5, (1, 5))
question = st.text_input("Ask a custom AI question about this data")

# ====== FILTER DATA ======
subset = df.copy()
if country != "All":
    subset = subset[subset["Shipping Country"] == country]
if category:
    subset = subset[subset["Product Category"].isin(category)]
if status:
    subset = subset[subset["Fulfillment Status"].isin(status)]
subset = subset[
    (subset["Rating"].between(*rating_range)) &
    (subset["Timestamp"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# Only show filtered data if user actually changed something from default
filters_applied = (
    (country != "All") or category or status or
    (rating_range != (1, 5)) or
    (date_range[0] != df["Timestamp"].min().date() or date_range[1] != df["Timestamp"].max().date())
)

if filters_applied and not subset.empty:
    st.subheader("Filtered Data")
    st.write(subset)
elif filters_applied and subset.empty:
    st.warning("No data matches your filters.")
else:
    st.info("Adjust filters to see data.")
# ====== BASIC INSIGHTS ======

if not subset.empty:
    avg_rating = subset["Rating"].mean()
    top_bad = subset.groupby("Product Name")["Rating"].mean().sort_values().head(5)
    st.metric("Average Rating", f"{avg_rating:.2f}")
    st.write("### Top 5 Lowest Rated Products", top_bad)

    # Ratings Distribution
    fig = px.histogram(subset, x="Rating", nbins=5, title="Ratings Distribution")
    st.plotly_chart(fig)

    # Download CSV
    csv = subset.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_reviews.csv", "text/csv")

# ====== AI CALL (OpenRouter) ======
def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Shopify Review Insights",
        "Content-Type": "application/json"
    }
    data = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 401:
            return "❌ Unauthorized. Check your API key."
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

if st.button("Get AI Summary"):
    sample_reviews = "\n".join(subset["Review Content"].sample(min(30, len(subset))).tolist())
    prompt = f"""
    Based on these Shopify reviews:
    {sample_reviews}
    1. Give sentiment breakdown (positive vs negative %)
    2. Top 5 complaints
    3. Top 5 compliments
    """
    summary = call_openrouter(prompt)
    st.subheader("AI Summary")
    st.write(summary)



ask_ai = st.button("Ask AI")
if ask_ai:
    if not question.strip():
        st.warning("Please enter a question before clicking Ask AI.")
    else:
        # Simple keyword-based domain check
        keywords = ["product", "review", "rating", "customer", "order", "purchase", "category", "shipping"]
        if not any(word in question.lower() for word in keywords):
            st.subheader("AI Answer")
            st.write("❌ Sorry, I can only answer questions related to Shopify reviews, ratings, products, and sales.")
        else:
            product_counts = subset["Product Name"].value_counts().index.tolist()
            prompt = f"""
You are an expert Shopify data analyst.

Rules:
1. Do NOT mention any numbers, quantities, percentages, or counts.
2. Focus only on relative popularity, trends, or customer sentiment.
3. If multiple products appear equally often, mention them as equally popular.
4. If the dataset is too small to determine a clear trend, say so.

Products in dataset: {', '.join(product_counts)}

Full Dataset:
{subset.to_string(index=False)}

Question: {question}
"""
            answer = call_openrouter(prompt)
            st.subheader("AI Answer")
            st.write(answer)



# ====== SENTIMENT ANALYSIS (HUGGINGFACE) ======
@st.cache_resource
def get_sentiment_pipeline():
    return pipeline("sentiment-analysis")

if st.button("Run Sentiment Analysis"):
    sentiment_pipe = get_sentiment_pipeline()
    subset["Sentiment"] = subset["Review Content"].apply(lambda x: sentiment_pipe(x[:512])[0]['label'])
    st.write(subset[["Review Content", "Sentiment"]])

    fig = px.pie(subset, names="Sentiment", title="Sentiment Distribution")
    st.plotly_chart(fig)

# ====== WORD CLOUD ======
if st.button("Generate Word Cloud"):
    # Separate positive vs negative reviews based on selected filter
    positive_text = " ".join(subset[subset["Rating"] >= 4]["Review Content"].dropna())
    negative_text = " ".join(subset[subset["Rating"] <= 2]["Review Content"].dropna())

    stop_words = set(STOPWORDS)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Handle positive reviews
    if positive_text.strip():
        wc_pos = WordCloud(width=400, height=300, background_color="white",
                           stopwords=stop_words, colormap="Greens").generate(positive_text)
        ax1.imshow(wc_pos, interpolation="bilinear")
        ax1.set_title("Positive Reviews")
    else:
        ax1.text(0.5, 0.5, "No Positive Reviews", ha='center', va='center', fontsize=14)
    ax1.axis("off")

    # Handle negative reviews
    if negative_text.strip():
        wc_neg = WordCloud(width=400, height=300, background_color="white",
                           stopwords=stop_words, colormap="Reds").generate(negative_text)
        ax2.imshow(wc_neg, interpolation="bilinear")
        ax2.set_title("Negative Reviews")
    else:
        ax2.text(0.5, 0.5, "No Negative Reviews", ha='center', va='center', fontsize=14)
    ax2.axis("off")

    st.pyplot(fig)


# ====== FOOTER ======
st.caption("Built with ❤️ using Streamlit, HuggingFace Transformers, and OpenRouter AI")
