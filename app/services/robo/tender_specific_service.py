import requests
import time
from app.config import LLM_API_KEY,LLM_API_URL
from bson import ObjectId
from fastapi import Request

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
                time.sleep(delay * attempt)  # Exponential backoff
            else:
                raise RuntimeError(f"❌ DeepSeek failed after {retries} attempts.") from e


def get_relevant_field_from_question(question: str) -> str:
    schema_fields = [
        "organization", "emd", "clean_bio",
        "submission_date", "metadata.length", "metadata.type", "metadata.roadLocation"
        "metadata.currentSite", "metadata.drainage", "metadata.structures",
        "metadata.protection", "metadata.geometricDesigns", "metadata.paymentWeightage",
        "metadata.intersections", "metadata.facilities", "metadata.utilities", "metadata.costGST",
        "metadata.timePeriod"
    ]

    prompt = f"""
              You are an assistant helping to identify which MongoDB field best answers a user's question.

              Here are the schema fields:
              {chr(10).join(f"- {f}" for f in schema_fields)}

              Now apply these rules before choosing the field:

              Rules:
              - If question is about TCS, pavement design, road crust, cross sections → choose "metadata.roadComposition"
              - If question is about culverts, bridges, minor or major structures → choose "metadata.structures"
              - If question is about grade separators, intersections, cut sections → choose "metadata.gradeSeperators"
              - If question is about traffic signs, roadside furniture, safety devices, lighting → choose "metadata.facilities"
              - If question is about gabion, toe wall, breast wall, retaining wall → choose "metadata.protection"
              - If question is about utilities or miscellaneous works → choose "metadata.otherWorks"
              - If question asks about current site status like chainage, lanes, width → choose "metadata.currentSite"
              - If question refers to payment percentages or cost breakups → choose "metadata.paymentWeightage"
              - If the question asks something like 'Does the tender contain any protection work etc.', then → choose "metadata.paymentWeightage"

              Now answer only with the most relevant field (just the field name, no explanation) for this question:
              \"{question}\"
              """
    return query_deepseek(prompt).replace('"', '').strip()


def extract_field_value(tender: dict, field_path: str):
    keys = field_path.split(".")
    value = tender
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
        if value is None:
            return None
    return value


def ask_deepseek_with_field_content(question: str, field_value):
    prompt = f"""
              You are TenderRobo, the official assistant of TenderBharat — a platform that helps users explore and understand government road construction tenders using AI.

              You are answering the user's question by referring to internal data from a specific tender.

              ---

              📥 Question:
              "{question}"

              📄 Relevant Tender Data:
              \"\"\"{field_value}\"\"\"

              ---

              ✅ Your Answer:
              Please provide a helpful, easy-to-understand answer to the user, speaking on behalf of TenderBharat.
              """
    return query_deepseek(prompt)


async def answer_tender_field_question(question: str, tender_id: str, request: Request):
    tenders_collection = request.app.mongodb["Test"]
    try:
        tender = await tenders_collection.find_one({"_id": ObjectId(tender_id)})
    except Exception as e:
        return f"❌ Could not fetch tender: {e}"

    if not tender:
        return f"❌ No tender found with ID: {tender_id}"

    field = get_relevant_field_from_question(question)
    if not field:
        return "❌ Sorry, I couldn't find relevant information in the tender for your question."

    value = extract_field_value(tender, field)
    if not value:
        return f"⚠️ The tender does not contain data for the field `{field}`."

    return ask_deepseek_with_field_content(question, value)