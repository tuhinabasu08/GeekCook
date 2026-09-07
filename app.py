import streamlit as st
pip install ollama
from ollama import chat
from ollama import Client

ollama signin
ollama run gpt-oss:120b-cloud

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="GeekCook | Recipe Recommendation System",
    page_icon="👨‍🍳",
    layout="centered"
)


# ---------------------------------------------------------
# App Header
# ---------------------------------------------------------

st.title("👨‍🍳 GeekCook")
st.subheader("Recipe Recommendation System")

st.write(
    "Tell GeekCook what ingredients you have, then keep chatting to "
    "tweak the recipe — swap ingredients, make it vegetarian, ask for "
    "a faster version, whatever you need."
)


# ---------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------

MODEL_NAME = "gpt-oss:120b"

SYSTEM_PROMPT = """You are GeekCook, a friendly recipe recommendation assistant.

When the user gives you ingredients or asks for a recipe, create an
easy-to-cook recipe using this exact format:

## 🍽️ Recipe Name

**Preparation Time:**
**Cooking Time:**
**Servings:**

### 🥕 Ingredients

- List the ingredients required
- Clearly identify any additional ingredients needed

### 👨‍🍳 Instructions

1. Give simple step-by-step cooking instructions.
2. Keep the instructions practical for a home cook.
3. Avoid complicated cooking techniques.

### 💡 Tips & Substitutions

- Suggest simple substitutions where appropriate.
- Mention useful cooking tips.

Important rules:

- Prioritize the ingredients the user has told you about.
- Keep recipes beginner-friendly and practical for a normal home kitchen.
- Do not assume the user has unusual ingredients.
- When the user asks you to change something about a recipe you already
  gave (swap an ingredient, make it vegetarian, cut the time, serve more
  people, etc.), give back the FULL recipe again in the same format above,
  updated accordingly — don't just describe the change in words.
- If the user asks a quick clarifying question that isn't about changing
  the recipe (e.g. "why did you use butter instead of oil?"), answer
  briefly in plain sentences instead of the full template.
"""


# ---------------------------------------------------------
# Chat Generation Function
# ---------------------------------------------------------

def generate_reply(messages):
    response = chat(
        model=MODEL_NAME,
        messages=messages,
        think=True
    )
    return response.message.content


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


# ---------------------------------------------------------
# Controls
# ---------------------------------------------------------

col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🔄 Start over", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()


# ---------------------------------------------------------
# Render Chat History
# ---------------------------------------------------------

has_started = len(st.session_state.messages) > 1

if not has_started:
    st.info(
        "👋 Start by telling GeekCook what ingredients you have — "
        "e.g. \"chicken, onion, tomato, garlic, rice, capsicum\"."
    )

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"], avatar="👨‍🍳" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])


# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------

placeholder = (
    "What ingredients do you have?"
    if not has_started
    else "Ask for a tweak — e.g. \"make it vegetarian\" or \"swap rice for pasta\""
)

user_input = st.chat_input(placeholder)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="👨‍🍳"):
        with st.spinner("👨‍🍳 GeekCook is thinking..."):
            try:
                reply = generate_reply(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as e:
                error_text = "❌ Something went wrong while generating a response."
                st.error(error_text)
                st.caption(f"Error details: {str(e)}")
                # Don't save a broken turn to history, so the user can just retry.
                st.session_state.messages.pop()


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "GeekCook 👨‍🍳 | Powered by Ollama + Qwen"
)
