# import os
# import requests
# import pandas as pd
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from fastapi.responses import JSONResponse
# from fastapi.responses import HTMLResponse
# from fastapi import Form

# load_dotenv()
# API_KEY = os.getenv("DATA_GOV_API_KEY")

# app = FastAPI()

# # Allow CORS for frontend dev
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# RAIN_RESOURCE = "9cffe053-2a27-4543-8530-94409ccdd444"
# CROP_RESOURCE = "35be999b-0208-4354-b557-f6ca9a5355de"

# def get_datagov_data(resource_id, filters=None, limit=1000, offset=0):
#     # Increase limit to up to 1000 (API default max), and support pagination via offset
#     url = f"https://api.data.gov.in/resource/{resource_id}?api-key={API_KEY}&format=json&limit={limit}&offset={offset}"
#     if filters:
#         # Only some fields may be filterable via URL on data.gov.in—usually not recommended
#         for k, v in filters.items():
#             url += f"&{k}={v}"
#     r = requests.get(url)
#     r.raise_for_status()
#     records = r.json().get("records", [])
#     return pd.DataFrame(records)

# @app.post("/qa")
# async def answer_question(req: Request):
#     data = await req.json()
#     question = data.get('question', '')

#     # --- Simple "Intent Classification" ---
#     if "rainfall" in question and "crop" in question:
#         import re
#         m = re.findall(r'in (.+?) and (.+?) for the last (\d+) years', question)
#         if m:
#             state1, state2, years_count = m[0]
#             years_count = int(years_count)
#             # Dynamically determine last N years available, based on data!
#             try:
#                 # Fetch only a bit to find latest year
#                 sample_rain = get_datagov_data(RAIN_RESOURCE, limit=100)
#                 sample_rain['year'] = sample_rain['year'].astype(int)
#                 max_year = sample_rain['year'].max()
#                 years = [str(y) for y in range(max_year - years_count + 1, max_year + 1)]
#             except Exception:
#                 years = []

#             # Fetch larger slices
#             df_rain = get_datagov_data(RAIN_RESOURCE, limit=1000)
#             df_crop = get_datagov_data(CROP_RESOURCE, limit=1000)

#             res = {}
#             for state in [state1.strip(), state2.strip()]:
#                 # Filter for state and years
#                 rf = df_rain[
#                     (df_rain['state'].str.contains(state, case=False, na=False)) &
#                     (df_rain['year'].astype(str).isin(years))
#                 ]
#                 try:
#                     avg_rain = rf['rainfall'].astype(float).mean()
#                 except Exception:
#                     avg_rain = float('nan')

#                 prod = df_crop[
#                     (df_crop['state_name'].str.contains(state, case=False, na=False)) &
#                     (df_crop['crop_year'].astype(str).isin(years))
#                 ]
#                 if not prod.empty:
#                     # Convert to numeric
#                     prod['production_'] = pd.to_numeric(prod['production_'], errors='coerce')
#                     top_crops = (prod.groupby('crop')['production_'].sum().sort_values(ascending=False).head(3))
#                 else:
#                     top_crops = pd.Series([], dtype=float)
#                 res[state] = {
#                     "avg_rainfall": avg_rain,
#                     "top_crops": list(top_crops.index),
#                     "top_crops_qty": list(top_crops.values)
#                 }
#             answer = (
#                 f"- **Average annual rainfall**:\n"
#                 f"  - {state1}: {res[state1]['avg_rainfall']:.2f} mm ([SHB 2020](https://data.gov.in/resource/{RAIN_RESOURCE}))\n"
#                 f"  - {state2}: {res[state2]['avg_rainfall']:.2f} mm ([SHB 2020](https://data.gov.in/resource/{RAIN_RESOURCE}))\n"
#                 f"- **Top 3 most produced crops (by volume):**\n"
#                 f"  - {state1}: {', '.join(res[state1]['top_crops'])} ([Crop Production](https://data.gov.in/resource/{CROP_RESOURCE}))\n"
#                 f"  - {state2}: {', '.join(res[state2]['top_crops'])} ([Crop Production](https://data.gov.in/resource/{CROP_RESOURCE}))"
#             )
#             return {"answer": answer}
#         else:
#             return {"answer": "Sorry, couldn't parse your question. Please use format: Compare rainfall and top crops in <State1> and <State2> for the last <N> years."}
#     return {"answer": "Sorry, only 'compare rainfall and crops' is implemented in this demo prototype. Try: 'Compare rainfall and top crops in Maharashtra and Gujarat for the last 5 years.'"}

# @app.get("/test/rainfall")
# def test_rainfall(state: str = None, limit: int = 10, offset: int = 0):
#     try:
#         df_rain = get_datagov_data(RAIN_RESOURCE, limit=limit, offset=offset)
#         if state:
#             df_rain = df_rain[df_rain['state'].str.contains(state, case=False, na=False)]
#         # Limit to avoid massive responses
#         return JSONResponse(content=df_rain.head(20).to_dict(orient="records"))
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/test/crop")
# def test_crop(state: str = None, limit: int = 10, offset: int = 0):
#     try:
#         df_crop = get_datagov_data(CROP_RESOURCE, limit=limit, offset=offset)
#         if state:
#             df_crop = df_crop[df_crop['state_name'].str.contains(state, case=False, na=False)]
#         # Limit to avoid massive responses
#         return JSONResponse(content=df_crop.head(20).to_dict(orient="records"))
#     except Exception as e:
#         return {"error": str(e)}


# # ... your existing endpoints ...

# def get_answer_from_question(question: str):
#     import re

#     # "Rainfall in <region>"
#     m = re.match(r'rainfall in ([\w\s]+)', question.lower())
#     if m:
#         region = m.group(1).strip()
#         df_rain = get_datagov_data(RAIN_RESOURCE, limit=1000)
#         # Try both district and state columns for matching
#         df = df_rain[
#             df_rain['district'].str.contains(region, case=False, na=False) |
#             df_rain['state'].str.contains(region, case=False, na=False)
#         ]
#         if not df.empty:
#             try:
#                 df['rainfall'] = pd.to_numeric(df['rainfall'], errors='coerce')
#             except Exception:
#                 pass
#             avg_rain = df['rainfall'].mean()
#             latest_year = df['year'].max()
#             answer = (f"Average rainfall in {region.title()} (latest year {latest_year}): "
#                       f"{avg_rain:.2f} mm ([Source](https://data.gov.in/resource/{RAIN_RESOURCE}))")
#         else:
#             answer = f"No rainfall data found for {region.title()}."
#         return answer

#     # --- Compare rainfall and crops logic ---
#     if "rainfall" in question and "crop" in question:
#         m = re.findall(r'in (.+?) and (.+?) for the last (\d+) years', question)
#         if m:
#             state1, state2, years_count = m[0]
#             years_count = int(years_count)
#             try:
#                 sample_rain = get_datagov_data(RAIN_RESOURCE, limit=100)
#                 sample_rain['year'] = sample_rain['year'].astype(int)
#                 max_year = sample_rain['year'].max()
#                 years = [str(y) for y in range(max_year - years_count + 1, max_year + 1)]
#             except Exception:
#                 years = []

#             df_rain = get_datagov_data(RAIN_RESOURCE, limit=1000)
#             df_crop = get_datagov_data(CROP_RESOURCE, limit=1000)

#             res = {}
#             for state in [state1.strip(), state2.strip()]:
#                 rf = df_rain[
#                     (df_rain['state'].str.contains(state, case=False, na=False)) &
#                     (df_rain['year'].astype(str).isin(years))
#                 ]
#                 try:
#                     avg_rain = rf['rainfall'].astype(float).mean()
#                 except Exception:
#                     avg_rain = float('nan')

#                 prod = df_crop[
#                     (df_crop['state_name'].str.contains(state, case=False, na=False)) &
#                     (df_crop['crop_year'].astype(str).isin(years))
#                 ]
#                 if not prod.empty:
#                     prod['production_'] = pd.to_numeric(prod['production_'], errors='coerce')
#                     top_crops = (prod.groupby('crop')['production_'].sum().sort_values(ascending=False).head(3))
#                 else:
#                     top_crops = pd.Series([], dtype=float)
#                 res[state] = {
#                     "avg_rainfall": avg_rain,
#                     "top_crops": list(top_crops.index),
#                     "top_crops_qty": list(top_crops.values)
#                 }
#             answer = (
#                 f"- **Average annual rainfall**:\n"
#                 f"  - {state1}: {res[state1]['avg_rainfall']:.2f} mm ([SHB 2020](https://data.gov.in/resource/{RAIN_RESOURCE}))\n"
#                 f"  - {state2}: {res[state2]['avg_rainfall']:.2f} mm ([SHB 2020](https://data.gov.in/resource/{RAIN_RESOURCE}))\n"
#                 f"- **Top 3 most produced crops (by volume):**\n"
#                 f"  - {state1}: {', '.join(res[state1]['top_crops'])} ([Crop Production](https://data.gov.in/resource/{CROP_RESOURCE}))\n"
#                 f"  - {state2}: {', '.join(res[state2]['top_crops'])} ([Crop Production](https://data.gov.in/resource/{CROP_RESOURCE}))"
#             )
#             return answer
#         else:
#             return "Sorry, couldn't parse your question. Please use format: Compare rainfall and top crops in <State1> and <State2> for the last <N> years."
#     return "Sorry, question pattern not yet supported. Example: rainfall in Chennai"

# # Now update your /qa endpoint to call this:
# @app.post("/qa")
# async def answer_question(req: Request):
#     data = await req.json()
#     question = data.get('question', '')
#     answer = get_answer_from_question(question)
#     return {"answer": answer}

# # Update /qa_html to NOT use await:
# @app.get("/", response_class=HTMLResponse)
# def home():
#     return """
#     <html>
#     <head><title>Project Samarth Q&A Demo</title></head>
#     <body>
#       <h2>Project Samarth Q&A Demo</h2>
#       <form action="/qa_html" method="post">
#         <input name="question" style="width:350px" placeholder="Ask your question about rainfall/crops...">
#         <button type="submit">Ask</button>
#       </form>
#       <br>
#       <b>Example questions:</b>
#       <ul>
#         <li>rainfall in Chennai</li>
#         <li>Compare rainfall and top crops in Maharashtra and Gujarat for the last 5 years</li>
#         <li>Compare rainfall and top crops in Kerala and Tamil Nadu for the last 3 years</li>
#       </ul>
#     </body>
#     </html>
#     """

# @app.post("/qa_html", response_class=HTMLResponse)
# def qa_html(question: str = Form(...)):
#     answer = get_answer_from_question(question)
#     return f"""
#     <html>
#     <head><title>Project Samarth Q&A Demo</title></head>
#     <body>
#       <h2>Project Samarth Q&A Demo</h2>
#       <form action="/qa_html" method="post">
#         <input name="question" value="{question}" style="width:350px">
#         <button type="submit">Ask</button>
#       </form>
#       <br>
#       <b>Example questions:</b>
#       <ul>
#         <li>rainfall in Chennai</li>
#         <li>Compare rainfall and top crops in Maharashtra and Gujarat for the last 5 years</li>
#         <li>Compare rainfall and top crops in Kerala and Tamil Nadu for the last 3 years</li>
#       </ul>
#       <hr>
#       <b>Answer:</b><br>
#       <div style="white-space: pre-wrap;">{answer}</div>
#     </body></html>
#     """

import os
import requests
import pandas as pd
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

load_dotenv()
API_KEY = os.getenv("DATA_GOV_API_KEY", "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b")

app = FastAPI(title="Project Samarth Q&A")

# Allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resources
RAIN_RESOURCE = "9cffe053-2a27-4543-8530-94409ccdd444"
CROP_RESOURCE = "35be999b-0208-4354-b557-f6ca9a5355de"


# -------------------------------------------------------------------
# Helper: Fetch data.gov.in data
# -------------------------------------------------------------------
def get_datagov_data(resource_id, filters=None, limit=1000, offset=0):
    """Fetch and return as DataFrame."""
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={API_KEY}&format=json&limit={limit}&offset={offset}"
    if filters:
        for k, v in filters.items():
            url += f"&{k}={v}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        records = data.get("records", [])
        return pd.DataFrame(records)
    except Exception as e:
        print(f"⚠️ Error fetching {resource_id}: {e}")
        return pd.DataFrame()


# -------------------------------------------------------------------
# Main logic: Parse question and compute answer
# -------------------------------------------------------------------
def get_answer_from_question(question: str):
    import re

    q = question.lower().strip()

    # --- Case 1: "Rainfall in <region>" ---
    if q.startswith("rainfall in "):
        region = q.replace("rainfall in ", "").strip()
        df = get_datagov_data(RAIN_RESOURCE, limit=1000)
        if df.empty:
            return "⚠️ No rainfall data available from the API right now."

        # Find matching columns
        possible_cols = [c.lower() for c in df.columns]
        region_cols = [c for c in possible_cols if "district" in c or "state" in c]
        rain_col = next((c for c in possible_cols if "rain" in c), None)

        if not region_cols or not rain_col:
            return f"⚠️ Dataset missing expected columns. Columns: {list(df.columns)}"

        region_col = region_cols[0]
        df.columns = possible_cols
        df_match = df[df[region_col].str.contains(region, case=False, na=False)]

        if df_match.empty:
            return f"❌ No rainfall data found for {region.title()}."

        try:
            df_match[rain_col] = pd.to_numeric(df_match[rain_col], errors="coerce")
        except Exception:
            pass
        avg_rain = df_match[rain_col].mean()
        year_col = next((c for c in df.columns if "year" in c), None)
        latest_year = df_match[year_col].max() if year_col else "N/A"

        return (
            f"🌧️ Average rainfall in {region.title()} ({latest_year}): "
            f"{avg_rain:.2f} mm ([Source](https://data.gov.in/resource/{RAIN_RESOURCE}))"
        )

    # --- Case 2: Compare rainfall and crops ---
    if "rainfall" in q and "crop" in q:
        m = re.findall(r"in (.+?) and (.+?) for the last (\d+) years", q)
        if not m:
            return "❌ Please use format: Compare rainfall and top crops in <State1> and <State2> for the last <N> years."

        state1, state2, years_count = m[0]
        years_count = int(years_count)
        df_rain = get_datagov_data(RAIN_RESOURCE, limit=1000)
        df_crop = get_datagov_data(CROP_RESOURCE, limit=1000)

        if df_rain.empty or df_crop.empty:
            return "⚠️ Could not load required data. Try again later."

        try:
            df_rain["year"] = pd.to_numeric(df_rain["year"], errors="coerce")
            max_year = int(df_rain["year"].max())
            years = [str(y) for y in range(max_year - years_count + 1, max_year + 1)]
        except Exception:
            years = []

        result = {}
        for state in [state1.strip(), state2.strip()]:
            rf = df_rain[
                (df_rain["state"].str.contains(state, case=False, na=False))
                & (df_rain["year"].astype(str).isin(years))
            ]
            avg_rain = pd.to_numeric(rf["rainfall"], errors="coerce").mean()

            prod = df_crop[
                (df_crop["state_name"].str.contains(state, case=False, na=False))
                & (df_crop["crop_year"].astype(str).isin(years))
            ]
            prod["production_"] = pd.to_numeric(prod["production_"], errors="coerce")
            top_crops = (
                prod.groupby("crop")["production_"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
            )
            result[state] = {
                "avg_rain": avg_rain,
                "top_crops": list(top_crops.index),
                "top_vals": list(top_crops.values),
            }

        return (
            f"🌧️ **Average annual rainfall:**\n"
            f"• {state1.title()}: {result[state1]['avg_rain']:.2f} mm\n"
            f"• {state2.title()}: {result[state2]['avg_rain']:.2f} mm\n\n"
            f"🌾 **Top crops:**\n"
            f"• {state1.title()}: {', '.join(result[state1]['top_crops'])}\n"
            f"• {state2.title()}: {', '.join(result[state2]['top_crops'])}"
        )

    # --- Default response ---
    return (
        "🤖 Sorry, I only understand questions like:\n"
        "- rainfall in Chennai\n"
        "- compare rainfall and top crops in Maharashtra and Gujarat for the last 5 years"
    )


# -------------------------------------------------------------------
# API Routes
# -------------------------------------------------------------------

@app.post("/qa")
async def qa_json(req: Request):
    data = await req.json()
    question = data.get("question", "")
    answer = get_answer_from_question(question)
    return {"answer": answer}


# -------------------------------------------------------------------
# HTML Routes (Fixed)
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>🌿 Project Samarth – Data Q&A</title>
    <style>
      body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        margin: 0;
        padding: 20px;
      }

      .container {
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        padding: 40px;
        max-width: 600px;
        width: 100%;
        text-align: center;
      }

      h2 {
        color: #2e7d32;
        font-weight: 600;
        font-size: 28px;
        margin-bottom: 24px;
      }

      form {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin-bottom: 20px;
      }

      input[name="question"] {
        flex: 1;
        padding: 12px 14px;
        font-size: 16px;
        border: 2px solid #c8e6c9;
        border-radius: 10px;
        outline: none;
        transition: 0.3s;
      }

      input[name="question"]:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
      }

      button {
        background: linear-gradient(135deg, #66bb6a, #43a047);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
      }

      button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(76, 175, 80, 0.4);
      }

      ul {
        text-align: left;
        display: inline-block;
        margin-top: 16px;
        line-height: 1.6;
      }

      li {
        margin-bottom: 6px;
      }

      .note {
        margin-top: 16px;
        font-size: 14px;
        color: #666;
      }

      @media (max-width: 600px) {
        .container {
          padding: 28px 24px;
        }

        form {
          flex-direction: column;
        }

        button {
          width: 100%;
        }
      }
    </style>
  </head>

  <body>
    <div class="container">
      <h2>🌿 Project Samarth – Data Q&A</h2>
      <form action="/qa_html" method="post">
        <input
          type="text"
          name="question"
          placeholder="Ask about rainfall or crops..."
          required
        />
        <button type="submit">Ask</button>
      </form>

      <b>Examples:</b>
      <ul>
        <li>rainfall in Chennai</li>
        <li>crops in Uttar Pradesh</li>
        <li>compare rainfall and top crops in Maharashtra and Gujarat for the last 5 years</li>
      </ul>

      <div class="note">Powered by Open Data • data.gov.in API</div>
    </div>
  </body>
</html>

    """

@app.post("/qa_html", response_class=HTMLResponse)
def qa_html(question: str = Form(...)):
    try:
        answer = get_answer_from_question(question)
    except Exception as e:
        answer = f"⚠️ Error: {e}"

    return f"""
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>🌿 Project Samarth – Data Q&A</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}

            .container {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                padding: 40px;
                max-width: 700px;
                width: 100%;
            }}

            h2 {{
                color: #2e7d32;
                font-weight: 600;
                font-size: 28px;
                margin-bottom: 24px;
                text-align: center;
            }}

            form {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-bottom: 20px;
            }}

            input[name="question"] {{
                flex: 1;
                padding: 12px 14px;
                font-size: 16px;
                border: 2px solid #c8e6c9;
                border-radius: 10px;
                outline: none;
                transition: 0.3s;
            }}

            input[name="question"]:focus {{
                border-color: #4caf50;
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
            }}

            button {{
                background: linear-gradient(135deg, #66bb6a, #43a047);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            }}

            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 18px rgba(76, 175, 80, 0.4);
            }}

            .answer-section {{
                margin-top: 30px;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 12px;
                border-left: 5px solid #4caf50;
            }}

            .answer-label {{
                color: #4caf50;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
                text-transform: uppercase;
            }}

            .answer-content {{
                white-space: pre-wrap;
                color: #333;
                font-size: 15px;
                line-height: 1.6;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                color: #2e7d32;
                text-decoration: none;
                font-weight: 500;
            }}

            a:hover {{
                text-decoration: underline;
            }}

            @media (max-width: 600px) {{
                .container {{
                    padding: 28px 24px;
                }}
                form {{
                    flex-direction: column;
                }}
                button {{
                    width: 100%;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h2>🌿 Project Samarth – Data Q&A</h2>
            <form action="/qa_html" method="post">
                <input type="text" name="question" value="{question}" placeholder="Ask about rainfall or crops..." required />
                <button type="submit">Ask</button>
            </form>

            <div class="answer-section">
                <div class="answer-label">Answer</div>
                <div class="answer-content">{answer}</div>
            </div>

            <a href="/">← Ask another question</a>
        </div>
    </body>
    </html>
    """


# -------------------------------------------------------------------
# Test Endpoints
# -------------------------------------------------------------------

@app.get("/test/rainfall")
def test_rainfall():
    df = get_datagov_data(RAIN_RESOURCE, limit=10)
    return JSONResponse(content=df.head(5).to_dict(orient="records"))


@app.get("/test/crop")
def test_crop():
    df = get_datagov_data(CROP_RESOURCE, limit=10)
    return JSONResponse(content=df.head(5).to_dict(orient="records"))
