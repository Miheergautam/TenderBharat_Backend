import os
import json
import requests
import certifi
import time
from app.config import LLM_API_KEY, LLM_API_URL

def query_deepseek(prompt, api_key=LLM_API_KEY, retries=3, delay=2):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(LLM_API_URL, headers=headers, json=payload)
            response_data = response.json()

            if "choices" in response_data:
                return response_data["choices"][0]["message"]["content"]
            elif "error" in response_data:
                raise RuntimeError(f"❌ API Error: {response_data['error']['message']}")
            else:
                raise RuntimeError(f"❌ Unexpected response structure: {response_data}")

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed for DeepSeek: {e}")
            if attempt < retries:
                time.sleep(delay * attempt)
            else:
                raise RuntimeError(f"❌ DeepSeek failed after {retries} attempts.") from e


def classify_query_with_deepseek(user_query: str) -> str:
    prompt = f"""
              You are an AI assistant trained to classify user queries made on a tender platform called TenderBharat, which deals with government tenders in road construction.

              Classify the following user query into one of the following categories:

              1. "tender_fetching" – if the query is about fetching tenders and maps to known tender schema fields (e.g., terrain, cost, state, type, roadwork, etc.).
              2. "tender_specific" – if the query is asking for information about a specific tender (e.g., "What is the bridge span in this tender?").
              3. "gk_question" – if the user is asking for general knowledge (e.g., "What is an EPC contract?", "What is NHAI?").
              4. "nonsense" – if the query is irrelevant, random, or does not make sense.

              User Query: "{user_query}"

              Respond with only one of the four category labels: "tender_fetching", "tender_specific", "gk_question", or "nonsense".
              """
    return query_deepseek(prompt)


def handle_tender_specific():
    return "To explore details about this tender, please go to the tender page on TenderBharat and click on ‘Analysis’. You'll find a complete breakdown there."


def handle_gk_question(user_query: str):
    prompt = f"""
              You are TenderRobo, the official assistant of TenderBharat — a platform that helps users discover the most relevant government road construction tenders using AI.

              A user has asked a general knowledge question related to government tenders or infrastructure. Please respond in a clear, helpful tone as if you're replying on behalf of TenderBharat.

              User question: "{user_query}"

              Your answer:
              """
    return query_deepseek(prompt)


def handle_nonsense(user_query: str):
    prompt = f"""
              You are TenderRobo, the assistant of TenderBharat — a platform that deals with Indian government road construction tenders. A user has entered a message that seems unclear or unrelated.

              Respond kindly and clarify or guide the user as needed, as if you're responding on behalf of TenderBharat.

              User message: "{user_query}"

              Your response:
              """
    return query_deepseek(prompt)


def handle_tender_fetching(user_query: str):
    prompt = f"""
You are TenderRobo, the assistant of TenderBharat — a platform specializing in Indian government road construction tenders.

Below is the MongoDB schema for tenders, stored in the `TenderBharat` database, `Tenders` collection, inside a dictionary called `query`.

---

## 📦 SCHEMA FIELDS AND EXPECTED INPUTS

Each field is part of a MongoDB document and should be used to construct filters **only if** the user query maps directly to the schema.

{{
    "weightage_roadwork": float (percentage),
    "weightage_structures": float (percentage),
    "weightage_utilities": float (percentage),
    "weightage_other_works": float (percentage),
    "weightage_culverts": float (percentage),
    "weightage_structures_including_culverts": float (percentage),
    "weightage_earthwork_subgrade_subbase": float (percentage),

    "type_pavement": string — only one of ["Flexible", "Rigid", "Both"],
    "carriageway_width": float (in meters),

    "type_roadwork": string — only one of ["Greenfield", "Upgradation"],

    "road_lanes": string — only one of ["Two Lane", "Four Lane", "Six Lane", "Intermediate Lane"],

    "number_major_bridges": integer,
    "number_minor_bridges": integer,
    "maximum_span_bridge": float (in meters),
    "number_culverts": integer,
    "maximum_span_ROB_RUB": float (in meters),

    "completion_time": integer (in months),
    "length": float (in kilometers),
    "cost": float (in crores),
    "emd": float (in crores),
    "cost_per_length": float (in crores/km),

    "organisation": string — e.g., "NHAI", "MORTH", "PWD",
    "organisation_type": string — only one of ["Central", "State"],

    "submission_date": string — in "DD/MM/YYYY" format,

    "terrain": array of strings — valid values: ["Border", "Hilly"],

    "extreme_conditions": array of strings — valid values: ["Extreme Heat", "Extreme Cold", "Extreme Monsoon", "Cyclone", "Dense Fog"],

    "city": array of strings — valid values: array of any Indian city  e.g.,["Jaipur", "Jodhpur"],
    "state": string — any Indian state,

    "coordinates": array of two floats — [longitude, latitude],

    "type": string — only one of ["EPC", "HAM", "ITEM-RATE", "BOT", "Others"]
}}

---

🧠 Your Task:
Given a user query, decompose it into a valid MongoDB filter over the `query` field.

Only use schema fields and only use values that are allowed as per the field descriptions.

📥 User Query:
"{user_query}"

---

✅ Your Output:
Respond only with the MongoDB filter as a JSON dictionary.

Each key must start with "query." (e.g., "query.state", "query.type", etc.).

If the query does not map to this schema (e.g., completely irrelevant, nonsense, or vague), return:
null

If numbers are mentioned (e.g., "more than 10 crore cost"), convert to comparison filter like:
{{ "query.cost": {{ "$gt": 10 }} }}

🗓️ If the query mentions a date **without a year**, assume the year is 2025 and convert the value to "DD/MM/2025" format.

## For queries about combined quantities (e.g., "total bridges"):

1. Automatically sum all relevant schema fields that match the category
2. Use $expr with $add for the sum operation
3. Apply the requested comparison ($gte, $lte, etc.)

Example transformations:
"minimum 2 bridges" → Sum of major + minor bridges

Do not explain anything. Just return the MongoDB filter or null. NO JSON Braces
"""
    return query_deepseek(prompt)


def process_user_query(user_query: str):
    category = classify_query_with_deepseek(user_query).strip().lower()

    if category == "tender_fetching":
        response = handle_tender_fetching(user_query)
        if response.strip() == "null":
            return "Sorry, we couldn't find tenders based on your query."
        else:
            return response

    elif category == "tender_specific":
        return handle_tender_specific()

    elif category == "gk_question":
        return handle_gk_question(user_query)

    elif category == "nonsense":
        return handle_nonsense(user_query)

    else:
        return "Sorry, we couldn’t understand your request. Please try rephrasing."
