from services.analyzer import CorrelationResult
from config.settings import DEFAULT_MODEL
from models.schemas import Insight
from services.llm.prompt import _format_correlations_for_prompt
from services.llm.schema import SYSTEM_PROMPT, INSIGHT_TOOL_SCHEMA

from google import genai
import json
import os

from services.llm.prompt import _format_correlations_for_prompt

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def _call_gemini(correlations, n_days, user_goals, model = "gemini-2.5-flash"):
    prompt = _format_correlations_for_prompt(correlations, n_days, user_goals)

    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

    response = client.models.generate_content(
        model=model,
        contents=full_prompt
    )

    text = response.text.strip()

    if text.startswith("```"):text = text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(text)
    except:
        raise RuntimeError(f"Output Gemini bukan JSON valid:\n{text}")


    return parsed.get("insights", [])

   



# def _call_lovable_ai(
#     correlations: list[CorrelationResult],
#     n_days: int,
#     user_goals: list[str],
#     api_key: str,
#     model: str = DEFAULT_MODEL,
# ) -> list[Insight]:
#     """Kirim korelasi ke LLM, parse hasil tool call jadi list[Insight]."""
#     user_message = _format_correlations_for_prompt(
#         correlations, n_days, user_goals,
#     )

#     payload = {
#         "model": model,
#         "messages": [
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": user_message},
#         ],
#         "tools": [INSIGHT_TOOL_SCHEMA],
#         "tool_choice": {
#             "type": "function",
#             "function": {"name": "emit_insights"},
#         },
#     }

#     resp = requests.post(
#         LOVABLE_AI_URL,
#         headers={
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#         },
#         json=payload,
#         timeout=60,
#     )

#     # Surface rate-limit & payment errors agar bisa ditangani caller
#     if resp.status_code == 429:
#         raise RuntimeError("Rate limit Lovable AI tercapai. Coba lagi sebentar.")
#     if resp.status_code == 402:
#         raise RuntimeError(
#             "Kredit Lovable AI habis. Top-up di Settings > Workspace > Usage."
#         )
#     if not resp.ok:
#         raise RuntimeError(f"Lovable AI error {resp.status_code}: {resp.text[:300]}")

#     data = resp.json()
#     try:
#         tool_calls = data["choices"][0]["message"]["tool_calls"]
#         args_str = tool_calls[0]["function"]["arguments"]
#         parsed = json.loads(args_str)
#     except (KeyError, IndexError, json.JSONDecodeError) as e:
#         raise RuntimeError(
#             f"Gagal parse tool-call dari LLM: {e}. Raw: {json.dumps(data)[:500]}"
#         )

#     insights = [Insight(**item) for item in parsed.get("insights", [])]
#     return insights
