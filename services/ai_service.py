from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def get_insights(df, missing, duplicates):
    summary = f"""
    Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
    Columns: {list(df.columns)}
    Missing values: {missing}
    Duplicate rows: {duplicates}
    Numeric summary:
    {df.describe().to_string()}
    """

    prompt = f"""
    You are a professional data analyst. Analyze this dataset and give 5 clear business insights.
    Be specific, mention actual numbers from the data.
    Format each insight on a new line starting with a bullet point.
    {summary}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def answer_question(df, question):
    summary = f"""
    Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
    Columns: {list(df.columns)}
    Sample data:
    {df.head(10).to_string()}
    Numeric summary:
    {df.describe().to_string()}
    """

    prompt = f"""
    You are a data analyst assistant. Answer this question about the dataset clearly and concisely.
    Question: {question}
    Dataset info:
    {summary}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content