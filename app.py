import streamlit as st
from ollama import Client


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="GeekCook | Recipe Recommendation System",
    page_icon="👨‍🍳",
    layout="centered"
)

st.sidebar.header("📊 Filter Options")

# Categorical Filter (Multiselect)
cuisine = ["North Indian", "Chinese", "Bengali", "Maharashtrian", "Goan", "South Indian", "Italian", "Continental", "Pan Asian"]
selected_categories = st.sidebar.multiselect(
    label="Select Cuisine",
    options=cuisine.unique(),
    default=cuisine.unique() # Defaults to selecting everything
)

# Vegetarian Toggle
veg_only = st.sidebar.checkbox("Vegetarian Only 🌿")

diet_restriction = "The recipe MUST be strictly vegetarian." if veg_only else "The recipe can include meat or be vegetarian."
    
# Numerical Filter (Slider)
min_val, max_val = int(1, 50)
selected_serve_range = st.sidebar.slider(
    label="Select Number of Servings",
    min_value=min_val,
    max_value=max_val,
    value=(min_val, max_val) # Defaults to full range
)

# ---------------------------------------------------------
# Ollama Cloud Configuration
# ---------------------------------------------------------

OLLAMA_API_KEY = st.secrets["OLLAMA_API_KEY"]

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }
)

MODEL_NAME = "gpt-oss:120b"


# ---------------------------------------------------------
# System Prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = f"""You are GeekCook, a friendly recipe recommendation assistant.

When the user gives you ingredients or asks for a recipe, create an
easy-to-cook recipe from the {selected_cuisine} cuisine using this exact format:

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

- Adjust ingredient quantity as per number of servings:{selected_serve_range}
- Follow the dietary restiction: {diet_restriction}
- Prioritize the ingredients the user has told you about.
- Keep recipes beginner-friendly and practical for a normal home kitchen.
- Do not assume the user has unusual ingredients.
- When the user asks to change something about a recipe you already
  gave (swap an ingredient, make it vegetarian, cut the time, serve
  more people, etc.), give back the FULL recipe again in the same
  format above, updated accordingly.
- If the user asks a quick clarifying question that isn"t about
  changing the recipe, answer briefly in plain sentences instead of
  the full template.
"""


# ---------------------------------------------------------
# Chat Generation Function
# ---------------------------------------------------------

def generate_reply(messages):

    response = client.chat(
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
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("👨‍🍳 GeekCook")
st.subheader("Recipe Recommendation System")

st.write(
    "Tell GeekCook what ingredients you have, then keep chatting "
    "to tweak the recipe — swap ingredients, make it vegetarian, "
    "ask for a faster version, whatever you need."
)


# ---------------------------------------------------------
# Controls
# ---------------------------------------------------------

col1, col2 = st.columns([5, 1])

with col2:

    if st.button("🔄 Start over", use_container_width=True):

        st.session_state.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        st.rerun()


# ---------------------------------------------------------
# Render Chat History
# ---------------------------------------------------------

has_started = len(st.session_state.messages) > 1


if not has_started:

    st.info(
        "👋 Start by telling GeekCook what ingredients you have — "
        "e.g. "chicken, onion, tomato, garlic, rice, capsicum"."
    )


for msg in st.session_state.messages:

    if msg["role"] == "system":
        continue

    with st.chat_message(
        msg["role"],
        avatar="👨‍🍳" if msg["role"] == "assistant" else None
    ):

        st.markdown(msg["content"])


# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------

placeholder = (
    "What ingredients do you have?"
    if not has_started
    else "Ask for a tweak — e.g. "
         ""make it vegetarian" or "swap rice for pasta""
)

user_input = st.chat_input(placeholder)


if user_input:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)


    # Generate response
    with st.chat_message("assistant", avatar="👨‍🍳"):

        with st.spinner("👨‍🍳 GeekCook is thinking..."):

            try:

                reply = generate_reply(
                    st.session_state.messages
                )

                st.markdown(reply)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )

            except Exception as e:

                error_text = (
                    "❌ Something went wrong while generating "
                    "a response."
                )

                st.error(error_text)
                st.caption(f"Error details: {str(e)}")

                # Remove user message so the user can retry
                st.session_state.messages.pop()


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "GeekCook 👨‍🍳 | Powered by Ollama Cloud + gpt-oss:120b"
)
