from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def get_insights(df, missing, duplicates):
    try:
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

    except Exception as e:
        return f"• AI insights temporarily unavailable. Please try again.\n• Error: {str(e)}"


def answer_question(df, question, history=[]):
    try:
        summary = f"""
        Dataset has {df.shape[0]} rows and {df.shape[1]} columns.
        Columns: {list(df.columns)}
        Sample data:
        {df.head(10).to_string()}
        Numeric summary:
        {df.describe().to_string()}
        """

        messages = [
            {"role": "system", "content": f"You are a data analyst assistant. Here is the dataset info:\n{summary}"}
        ]

        # Add conversation history
        for msg in history:
            messages.append(msg)

        # Add current question
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Sorry, I couldn't process your question. Error: {str(e)}"