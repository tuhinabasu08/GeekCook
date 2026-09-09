import streamlit as st
import ollama
import time
import pandas as pd
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GeekCook | Model Evaluation",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 GeekCook Model Evaluation")
st.caption("Compare LLM performance for recipe recommendations")

# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODELS = {
    "Qwen 2.5 3B": "qwen2.5:3b",
    "GPT-OSS-120B": "gpt-oss:120b"
}

# IMPORTANT:
# Replace these with the actual costs you are using.
# Cost should be expressed as USD per 1M tokens.

MODEL_COSTS = {
    "Qwen 2.5 3B": {
        "input": 0.00,
        "output": 0.00
    },
    "GPT-OSS-120B": {
        "input": 0.00,
        "output": 0.00
    }
}

# =========================================================
# SESSION STATE
# =========================================================

if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = []

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("🍳 Recipe Requirements")

ingredients = st.sidebar.text_area(
    "Ingredients available",
    "chicken, onion, tomato, garlic, rice"
)

cuisine = st.sidebar.selectbox(
    "Cuisine",
    [
        "Indian",
        "North Indian",
        "South Indian",
        "Bengali",
        "Chinese",
        "Italian",
        "Mexican"
    ]
)

diet = st.sidebar.selectbox(
    "Diet",
    [
        "No specific restriction",
        "Vegetarian",
        "High Protein",
        "Low Carb"
    ]
)

time_limit = st.sidebar.slider(
    "Maximum cooking time (minutes)",
    10,
    90,
    30
)

# =========================================================
# PROMPT BUILDER
# =========================================================

def create_prompt(
    ingredients,
    cuisine,
    diet,
    time_limit
):

    return f"""
You are an expert recipe recommendation assistant.

Create ONE practical recipe using the ingredients available below.

Ingredients available:
{ingredients}

Cuisine preference:
{cuisine}

Dietary requirement:
{diet}

Maximum cooking time:
{time_limit} minutes

Requirements:
- Primarily use the available ingredients.
- Do not invent unavailable major ingredients.
- Respect the dietary requirement.
- Keep the recipe realistic and practical.
- Provide quantities for each ingredient.
- Provide step-by-step cooking instructions.
- Mention approximate cooking time.
- Explain briefly why the ingredients work well together.

Return the answer in this format:

Recipe Name:
Why this recipe:
Ingredients:
Instructions:
Cooking Time:
"""

# =========================================================
# MODEL CALL
# =========================================================

def run_model(model_name, prompt):

    model = MODELS[model_name]

    start_time = time.perf_counter()

    try:

        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        end_time = time.perf_counter()

        latency = end_time - start_time

        answer = response["message"]["content"]

        # Ollama generally returns token counts
        input_tokens = response.get(
            "prompt_eval_count",
            0
        )

        output_tokens = response.get(
            "eval_count",
            0
        )

        # -------------------------------------------------
        # COST CALCULATION
        # -------------------------------------------------

        input_cost = (
            input_tokens / 1_000_000
        ) * MODEL_COSTS[model_name]["input"]

        output_cost = (
            output_tokens / 1_000_000
        ) * MODEL_COSTS[model_name]["output"]

        total_cost = input_cost + output_cost

        return {
            "model": model_name,
            "response": answer,
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": (
                input_tokens + output_tokens
            ),
            "cost": total_cost,
            "success": True
        }

    except Exception as e:

        return {
            "model": model_name,
            "response": f"Error: {str(e)}",
            "latency": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost": 0,
            "success": False
        }


# =========================================================
# RUN EVALUATION
# =========================================================

prompt = create_prompt(
    ingredients,
    cuisine,
    diet,
    time_limit
)

st.subheader("📝 Evaluation Prompt")

with st.expander("View prompt"):
    st.code(prompt)

if st.button(
    "🚀 Compare Models",
    type="primary",
    use_container_width=True
):

    with st.spinner("Running both models..."):

        qwen_result = run_model(
            "Qwen 2.5 3B",
            prompt
        )

        gpt_result = run_model(
            "GPT-OSS-120B",
            prompt
        )

    results = [
        qwen_result,
        gpt_result
    ]

    # Store results
    st.session_state.evaluation_results.extend(
        results
    )

    st.success("Model comparison completed!")

# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state.evaluation_results:

    latest_results = (
        st.session_state.evaluation_results[-2:]
    )

    if len(latest_results) == 2:

        qwen = latest_results[0]
        gpt = latest_results[1]

        # -------------------------------------------------
        # SIDE-BY-SIDE RESPONSES
        # -------------------------------------------------

        st.divider()

        st.subheader("🧠 Model Responses")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                "### Qwen 2.5 3B"
            )

            st.markdown(
                qwen["response"]
            )

        with col2:

            st.markdown(
                "### GPT-OSS-120B"
            )

            st.markdown(
                gpt["response"]
            )

        # -------------------------------------------------
        # PERFORMANCE METRICS
        # -------------------------------------------------

        st.divider()

        st.subheader("📊 Performance Comparison")

        metrics_df = pd.DataFrame({

            "Metric": [
                "Latency (seconds)",
                "Input Tokens",
                "Output Tokens",
                "Total Tokens",
                "Estimated Cost ($)"
            ],

            "Qwen 2.5 3B": [
                round(qwen["latency"], 2),
                qwen["input_tokens"],
                qwen["output_tokens"],
                qwen["total_tokens"],
                round(qwen["cost"], 6)
            ],

            "GPT-OSS-120B": [
                round(gpt["latency"], 2),
                gpt["input_tokens"],
                gpt["output_tokens"],
                gpt["total_tokens"],
                round(gpt["cost"], 6)
            ]
        })

        st.dataframe(
            metrics_df,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # HUMAN EVALUATION
        # -------------------------------------------------

        st.divider()

        st.subheader("⭐ Human Evaluation")

        st.caption(
            "Rate each model from 1 (poor) to 5 (excellent)."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### Qwen 2.5 3B")

            qwen_quality = st.slider(
                "Recipe quality",
                1,
                5,
                3,
                key="qwen_quality"
            )

            qwen_constraints = st.slider(
                "Constraint following",
                1,
                5,
                3,
                key="qwen_constraints"
            )

            qwen_cook = st.radio(
                "Would you actually cook this?",
                ["Yes", "No"],
                key="qwen_cook"
            )

        with col2:

            st.markdown("### GPT-OSS-120B")

            gpt_quality = st.slider(
                "Recipe quality",
                1,
                5,
                3,
                key="gpt_quality"
            )

            gpt_constraints = st.slider(
                "Constraint following",
                1,
                5,
                3,
                key="gpt_constraints"
            )

            gpt_cook = st.radio(
                "Would you actually cook this?",
                ["Yes", "No"],
                key="gpt_cook"
            )

        # -------------------------------------------------
        # OVERALL SCORE
        # -------------------------------------------------

        # Cost is intentionally weighted heavily because
        # cost is the primary decision criterion.

        qwen_score = (
            qwen_quality * 0.30
            + qwen_constraints * 0.20
        )

        gpt_score = (
            gpt_quality * 0.30
            + gpt_constraints * 0.20
        )

        st.divider()

        st.subheader("🏆 GeekCook Model Score")

        score_df = pd.DataFrame({

            "Metric": [
                "Recipe Quality",
                "Constraint Following",
                "Would Cook",
                "Overall Quality Score"
            ],

            "Qwen 2.5 3B": [
                qwen_quality,
                qwen_constraints,
                1 if qwen_cook == "Yes" else 0,
                round(qwen_score, 2)
            ],

            "GPT-OSS-120B": [
                gpt_quality,
                gpt_constraints,
                1 if gpt_cook == "Yes" else 0,
                round(gpt_score, 2)
            ]
        })

        st.dataframe(
            score_df,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # QUALITY PER DOLLAR
        # -------------------------------------------------

        st.subheader("💰 Quality per Dollar")

        if qwen["cost"] > 0:

            qwen_qpd = (
                qwen_score / qwen["cost"]
            )

        else:
            qwen_qpd = float("inf")

        if gpt["cost"] > 0:

            gpt_qpd = (
                gpt_score / gpt["cost"]
            )

        else:
            gpt_qpd = float("inf")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Qwen 2.5 3B",
                (
                    "∞"
                    if qwen_qpd == float("inf")
                    else f"{qwen_qpd:.2f}"
                )
            )

        with col2:

            st.metric(
                "GPT-OSS-120B",
                (
                    "∞"
                    if gpt_qpd == float("inf")
                    else f"{gpt_qpd:.2f}"
                )
            )

# =========================================================
# EVALUATION HISTORY
# =========================================================

st.divider()

st.subheader("📈 Evaluation History")

if st.session_state.evaluation_results:

    history_df = pd.DataFrame(
        st.session_state.evaluation_results
    )

    history_df = history_df[
        [
            "model",
            "latency",
            "input_tokens",
            "output_tokens",
            "cost"
        ]
    ]

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

    csv = history_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Evaluation Results",
        csv,
        "geekcook_model_evaluation.csv",
        "text/csv"
    )

else:

    st.info(
        "Run a model comparison to start collecting evaluation results."
    )
