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


# Create Ollama Cloud client
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
    "Qwen 2.5 3B": "qwen2.5:3b",
    "GPT-OSS-120B": "gpt-oss:120b", 
    "Gemma4":"gemma4"
}


# =========================================================
# MODEL COST CONFIGURATION
# =========================================================
#
# Cost should be USD per 1M tokens.
#
# IMPORTANT:
# Replace these values with the actual Ollama Cloud
# pricing you are using.
#
# Keeping them configurable makes it easy to update
# pricing without changing the evaluation logic.
# =========================================================

MODEL_COSTS = {
    "Qwen 2.5 3B": {
        "input": 0.00,
        "output": 0.00
    },

    "GPT-OSS-120B": {
        "input": 0.00,
        "output": 0.00
    },

    "Gemma4": {
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

    with st.spinner("Running both models on Ollama Cloud..."):

        qwen_result = run_model(
            "Qwen 2.5 3B",
            prompt
        )

        gpt_result = run_model(
            "GPT-OSS-120B",
            prompt
        )
        
        gemma_result = run_model(
            "Gemma4",
            prompt
        )

    results = [
        qwen_result,
        gpt_result,
        gemma_result
    ]

    # Add evaluation metadata
    for result in results:

        result["timestamp"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        result["ingredients"] = ingredients
        result["cuisine"] = cuisine
        result["diet"] = diet
        result["time_limit"] = time_limit

    st.session_state.evaluation_results.extend(
        results
    )

    st.success("Model comparison completed!")


# =========================================================
# DISPLAY RESULTS
# =========================================================

if len(st.session_state.evaluation_results) >= 2:

    latest_results = (
        st.session_state.evaluation_results[-2:]
    )

    qwen = latest_results[0]
    gpt = latest_results[1]
    gemma4 = latest_results[2]

    # -----------------------------------------------------
    # HANDLE MODEL ERRORS
    # -----------------------------------------------------

    if not qwen["success"]:

        st.error(
            f"Qwen 2.5 3B failed:\n\n{qwen['error']}"
        )

    if not gpt["success"]:

        st.error(
            f"GPT-OSS-120B failed:\n\n{gpt['error']}"
        )

    if not gemma4["success"]:

        st.error(
            f"Gemma4 failed:\n\n{gpt['error']}"
        )

    # -----------------------------------------------------
    # SIDE-BY-SIDE RESPONSES
    # -----------------------------------------------------

    if qwen["success"] and gpt["success"] and gemma["success"]:

        st.divider()

        st.subheader("🧠 Model Responses")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### Qwen 2.5 3B")

            st.markdown(
                qwen["response"]
            )

        with col2:

            st.markdown("### GPT-OSS-120B")

            st.markdown(
                gpt["response"]
            )
            
        with col3:

            st.markdown("### Gemma4")

            st.markdown(
                gemma["response"]
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
                "Tokens / Second",
                "Estimated Cost ($)"
            ],

            "Qwen 2.5 3B": [
                round(qwen["latency"], 2),
                qwen["input_tokens"],
                qwen["output_tokens"],
                qwen["total_tokens"],
                round(qwen["tokens_per_second"], 2),
                round(qwen["cost"], 6)
            ],

            "GPT-OSS-120B": [
                round(gpt["latency"], 2),
                gpt["input_tokens"],
                gpt["output_tokens"],
                gpt["total_tokens"],
                round(gpt["tokens_per_second"], 2),
                round(gpt["cost"], 6)
            ],

            "Gemma4": [
                round(gemma["latency"], 2),
                gemma["input_tokens"],
                gemma["output_tokens"],
                gemma["total_tokens"],
                round(gemma["tokens_per_second"], 2),
                round(gemma["cost"], 6)
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

        col1, col2, col3 = st.columns(3)

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
            
        with col3:

            st.markdown("### Gemma4")

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

        # -------------------------------------------------
        # OVERALL SCORE
        # -------------------------------------------------
        #
        # Cost is the primary model-selection criterion.
        #
        # Quality score itself is normalized to a 1-5 scale.
        #
        # 60% Recipe Quality
        # 40% Constraint Following
        #
        # Cost is evaluated separately below because it is
        # the primary business decision criterion.
        # -------------------------------------------------

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
        # -------------------------------------------------
        # SCORE COMPARISON
        # -------------------------------------------------

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
            ],

            "Gemma4": [
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

        # -------------------------------------------------
        # COST COMPARISON
        # -------------------------------------------------

        st.subheader("💰 Cost Comparison")

        cost_col1, cost_col2, cost_col3 = st.columns(3)

        with cost_col1:

            st.metric(
                "Qwen 2.5 3B",
                f"${qwen['cost']:.6f}"
            )

        with cost_col2:

            st.metric(
                "GPT-OSS-120B",
                f"${gpt['cost']:.6f}"
            )
            
        with cost_col3:

            st.metric(
                "Gemma4",
                f"${gemma['cost']:.6f}"
            )

        if qwen["cost"] == 0 and gpt["cost"] == 0 and gemma["cost"] == 0:

            st.info(
                "Model pricing is currently set to $0.00. "
                "Update MODEL_COSTS with the actual Ollama "
                "Cloud input/output pricing to enable cost "
                "comparison."
            )

        # -------------------------------------------------
        # MODEL RECOMMENDATION
        # -------------------------------------------------

        st.divider()

        st.subheader("🎯 GeekCook Decision")

        if qwen["cost"] > 0 and gpt["cost"] > 0 and gemma["cost"] > 0:

            qwen_quality_per_dollar = (
                qwen_score / qwen["cost"]
            )

            gpt_quality_per_dollar = (
                gpt_score / gpt["cost"]
            )

            gemma_quality_per_dollar = (
                gemma_score / gemma["cost"]
            )

            qpd_df = pd.DataFrame({

                "Metric": [
                    "Quality Score",
                    "Cost ($)",
                    "Quality / Dollar"
                ],

                "Qwen 2.5 3B": [
                    round(qwen_score, 2),
                    round(qwen["cost"], 6),
                    round(qwen_quality_per_dollar, 2)
                ],

                "GPT-OSS-120B": [
                    round(gpt_score, 2),
                    round(gpt["cost"], 6),
                    round(gpt_quality_per_dollar, 2)
                ],
    
                "Gemma4": [
                    round(gemma_score, 2),
                    round(gemma["cost"], 6),
                    round(gemma_quality_per_dollar, 2)
                ]
            })

            st.dataframe(
                qpd_df,
                use_container_width=True,
                hide_index=True
            )

            if qwen_quality_per_dollar > gpt_quality_per_dollar and qwen_quality_per_dollar > gemma_quality_per_dollar:

                st.success(
                    "🏆 Qwen 2.5 3B currently provides the "
                    "best quality-to-cost ratio."
                )

            elif gpt_quality_per_dollar > qwen_quality_per_dollar and gpt_quality_per_dollar > gemma_quality_per_dollar:

                st.success(
                    "🏆 GPT-OSS-120B currently provides the "
                    "best quality-to-cost ratio."
                )
                
            elif gemma_quality_per_dollar > gpt_quality_per_dollar and gemma_quality_per_dollar > qwen_quality_per_dollar:

                st.success(
                    "🏆 Gemma currently provides the "
                    "best quality-to-cost ratio."
                )

            else:

                st.info(
                    "Both models currently have the same "
                    "quality-to-cost ratio."
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

