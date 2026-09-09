
import streamlit as st
from ollama import Client
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
# OLLAMA CLOUD CONFIGURATION
# =========================================================

try:
    OLLAMA_API_KEY = st.secrets["OLLAMA_API_KEY"]

except KeyError:
    st.error(
        "OLLAMA_API_KEY is not configured.\n\n"
        "Please add OLLAMA_API_KEY to your Streamlit Secrets."
    )
    st.stop()


client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }
)


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODELS = {
    "GPT-OSS-120B": "gpt-oss:120b",
    "GPT-OSS-20B": "gpt-oss:20b",
    "Gemma 4": "gemma4"
}


# =========================================================
# MODEL COST CONFIGURATION
# =========================================================
#
# USD per 1M tokens.
#
# Replace these values with the actual Ollama Cloud
# pricing you want to use for your evaluation.
# =========================================================

MODEL_COSTS = {
    "GPT-OSS-120B": {
        "input": 0.00,
        "output": 0.00
    },

    "GPT-OSS-20B": {
        "input": 0.00,
        "output": 0.00
    },

    "Gemma 4": {
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
# COST CALCULATION
# =========================================================

def calculate_cost(
    model_name,
    input_tokens,
    output_tokens
):

    input_price = MODEL_COSTS[model_name]["input"]
    output_price = MODEL_COSTS[model_name]["output"]

    input_cost = (
        input_tokens / 1_000_000
    ) * input_price

    output_cost = (
        output_tokens / 1_000_000
    ) * output_price

    return input_cost + output_cost


# =========================================================
# MODEL CALL
# =========================================================

def run_model(model_name, prompt):

    model = MODELS[model_name]

    start_time = time.perf_counter()

    try:

        response = client.chat(
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

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        answer = response["message"]["content"]

        # -------------------------------------------------
        # TOKEN USAGE
        # -------------------------------------------------

        input_tokens = response.get(
            "prompt_eval_count",
            0
        )

        output_tokens = response.get(
            "eval_count",
            0
        )

        total_tokens = (
            input_tokens + output_tokens
        )

        # -------------------------------------------------
        # TOKENS / SECOND
        # -------------------------------------------------

        tokens_per_second = (
            output_tokens / latency
            if latency > 0
            else 0
        )

        # -------------------------------------------------
        # COST
        # -------------------------------------------------

        total_cost = calculate_cost(
            model_name,
            input_tokens,
            output_tokens
        )

        return {
            "model": model_name,
            "response": answer,
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "tokens_per_second": tokens_per_second,
            "cost": total_cost,
            "success": True,
            "error": None
        }

    except Exception as e:

        return {
            "model": model_name,
            "response": "",
            "latency": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "tokens_per_second": 0,
            "cost": 0,
            "success": False,
            "error": str(e)
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

    results = []

    with st.spinner(
        "Running GPT-OSS-120B, GPT-OSS-20B and Gemma 4 on Ollama Cloud..."
    ):

        for model_name in MODELS:

            result = run_model(
                model_name,
                prompt
            )

            # Add evaluation metadata
            result["timestamp"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            result["ingredients"] = ingredients
            result["cuisine"] = cuisine
            result["diet"] = diet
            result["time_limit"] = time_limit

            results.append(result)

    # Store all three results
    st.session_state.evaluation_results.extend(
        results
    )

    st.success("Model comparison completed!")


# =========================================================
# DISPLAY RESULTS
# =========================================================

if len(st.session_state.evaluation_results) >= 3:

    # -----------------------------------------------------
    # Get the latest result for each model
    # -----------------------------------------------------

    latest_results = {}

    for result in reversed(
        st.session_state.evaluation_results
    ):

        model_name = result["model"]

        if model_name not in latest_results:

            latest_results[model_name] = result

        if len(latest_results) == len(MODELS):

            break


    qwen = latest_results["GPT-OSS-120B"]
    gpt = latest_results["GPT-OSS-20B"]
    gemma4 = latest_results["Gemma 4"]


    # =====================================================
    # HANDLE MODEL ERRORS
    # =====================================================

    for result in [
        qwen,
        gpt,
        gemma4
    ]:

        if not result["success"]:

            st.error(
                f"{result['model']} failed:\n\n"
                f"{result['error']}"
            )


    # =====================================================
    # SIDE-BY-SIDE RESPONSES
    # =====================================================

    if (
        qwen["success"]
        and gpt["success"]
        and gemma4["success"]
    ):

        st.divider()

        st.subheader("🧠 Model Responses")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### GPT-OSS-120B")

            st.markdown(
                qwen["response"]
            )

        with col2:

            st.markdown("### GPT-OSS-20B")

            st.markdown(
                gpt["response"]
            )

        with col3:

            st.markdown("### Gemma 4")

            st.markdown(
                gemma4["response"]
            )


        # =================================================
        # PERFORMANCE METRICS
        # =================================================

        st.divider()

        st.subheader("📊 Performance Comparison")

        metrics_df = pd.DataFrame({

            "Metric": [
                "Latency (seconds)",
                "Input Tokens",
                "Output Tokens",
                "Total Tokens",
                "Tokens / Second",
                "Estimated Cost ($)"
            ],

            "GPT-OSS-120B": [
                round(qwen["latency"], 2),
                qwen["input_tokens"],
                qwen["output_tokens"],
                qwen["total_tokens"],
                round(qwen["tokens_per_second"], 2),
                round(qwen["cost"], 6)
            ],

            "GPT-OSS-20B": [
                round(gpt["latency"], 2),
                gpt["input_tokens"],
                gpt["output_tokens"],
                gpt["total_tokens"],
                round(gpt["tokens_per_second"], 2),
                round(gpt["cost"], 6)
            ],

            "Gemma 4": [
                round(gemma4["latency"], 2),
                gemma4["input_tokens"],
                gemma4["output_tokens"],
                gemma4["total_tokens"],
                round(gemma4["tokens_per_second"], 2),
                round(gemma4["cost"], 6)
            ]
        })

        st.dataframe(
            metrics_df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # HUMAN EVALUATION
        # =================================================

        st.divider()

        st.subheader("⭐ Human Evaluation")

        st.caption(
            "Rate each model from 1 (poor) to 5 (excellent)."
        )

        col1, col2, col3 = st.columns(3)


        # -------------------------------------------------
        # QWEN
        # -------------------------------------------------

        with col1:

            st.markdown("### GPT-OSS-120B")

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


        # -------------------------------------------------
        # GPT
        # -------------------------------------------------

        with col2:

            st.markdown("### GPT-OSS-20B")

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
        # GEMMA
        # -------------------------------------------------

        with col3:

            st.markdown("### Gemma 4")

            gemma_quality = st.slider(
                "Recipe quality",
                1,
                5,
                3,
                key="gemma_quality"
            )

            gemma_constraints = st.slider(
                "Constraint following",
                1,
                5,
                3,
                key="gemma_constraints"
            )

            gemma_cook = st.radio(
                "Would you actually cook this?",
                ["Yes", "No"],
                key="gemma_cook"
            )


        # =================================================
        # OVERALL QUALITY SCORE
        # =================================================

        # Quality score:
        #
        # 60% Recipe Quality
        # 40% Constraint Following
        #
        # Cost is evaluated separately because it is the
        # primary model-selection criterion.

        qwen_score = (
            qwen_quality * 0.60
            + qwen_constraints * 0.40
        )

        gpt_score = (
            gpt_quality * 0.60
            + gpt_constraints * 0.40
        )

        gemma_score = (
            gemma_quality * 0.60
            + gemma_constraints * 0.40
        )


        # =================================================
        # SCORE COMPARISON
        # =================================================

        st.divider()

        st.subheader("🏆 GeekCook Model Score")

        score_df = pd.DataFrame({

            "Metric": [
                "Recipe Quality",
                "Constraint Following",
                "Would Cook",
                "Overall Quality Score"
            ],

            "GPT-OSS-120B": [
                qwen_quality,
                qwen_constraints,
                1 if qwen_cook == "Yes" else 0,
                round(qwen_score, 2)
            ],

            "GPT-OSS-20B": [
                gpt_quality,
                gpt_constraints,
                1 if gpt_cook == "Yes" else 0,
                round(gpt_score, 2)
            ],

            "Gemma 4": [
                gemma_quality,
                gemma_constraints,
                1 if gemma_cook == "Yes" else 0,
                round(gemma_score, 2)
            ]
        })

        st.dataframe(
            score_df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # COST COMPARISON
        # =================================================

        st.subheader("💰 Cost Comparison")

        cost_col1, cost_col2, cost_col3 = st.columns(3)

        with cost_col1:

            st.metric(
                "GPT-OSS-120B",
                f"${qwen['cost']:.6f}"
            )

        with cost_col2:

            st.metric(
                "GPT-OSS-20B",
                f"${gpt['cost']:.6f}"
            )

        with cost_col3:

            st.metric(
                "Gemma 4",
                f"${gemma4['cost']:.6f}"
            )


        if (
            qwen["cost"] == 0
            and gpt["cost"] == 0
            and gemma4["cost"] == 0
        ):

            st.info(
                "Model pricing is currently set to $0.00. "
                "Update MODEL_COSTS with the actual Ollama "
                "Cloud input/output pricing to enable cost "
                "comparison."
            )


        # =================================================
        # QUALITY / DOLLAR
        # =================================================

        st.divider()

        st.subheader("🎯 GeekCook Decision")

        if (
            qwen["cost"] > 0
            and gpt["cost"] > 0
            and gemma4["cost"] > 0
        ):

            quality_per_dollar = {

                "GPT-OSS-120B":
                    qwen_score / qwen["cost"],

                "GPT-OSS-20B":
                    gpt_score / gpt["cost"],

                "Gemma 4":
                    gemma_score / gemma4["cost"]
            }


            qpd_df = pd.DataFrame({

                "Metric": [
                    "Quality Score",
                    "Cost ($)",
                    "Quality / Dollar"
                ],

                "GPT-OSS-120B": [
                    round(qwen_score, 2),
                    round(qwen["cost"], 6),
                    round(
                        quality_per_dollar["GPT-OSS-120B"],
                        2
                    )
                ],

                "GPT-OSS-20B": [
                    round(gpt_score, 2),
                    round(gpt["cost"], 6),
                    round(
                        quality_per_dollar["GPT-OSS-20B"],
                        2
                    )
                ],

                "Gemma 4": [
                    round(gemma_score, 2),
                    round(gemma4["cost"], 6),
                    round(
                        quality_per_dollar["Gemma 4"],
                        2
                    )
                ]
            })

            st.dataframe(
                qpd_df,
                use_container_width=True,
                hide_index=True
            )


            # Find best model
            best_model = max(
                quality_per_dollar,
                key=quality_per_dollar.get
            )

            st.success(
                f"🏆 {best_model} currently provides "
                f"the best quality-to-cost ratio."
            )

        else:

            st.warning(
                "Add actual model pricing to calculate "
                "quality-to-dollar efficiency."
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

    history_columns = [
        "timestamp",
        "model",
        "cuisine",
        "diet",
        "time_limit",
        "latency",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "tokens_per_second",
        "cost"
    ]

    history_df = history_df[
        [
            col
            for col in history_columns
            if col in history_df.columns
        ]
    ]

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # DOWNLOAD RESULTS
    # -----------------------------------------------------

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
        "Run a model comparison to start collecting "
        "evaluation results."
    )

