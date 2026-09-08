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


# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------

st.sidebar.header("📊 Filter Options")

# Categorical Filter
cuisine = [
    "North Indian",
    "Chinese",
    "Bengali",
    "Maharashtrian",
    "Goan",
    "South Indian",
    "Italian",
    "Continental",
    "Pan Asian"
]

selected_cuisine = st.sidebar.multiselect(
    label="Select Cuisine",
    options=cuisine,
    default=cuisine
)

# Handle no cuisine selection
if selected_cuisine:
    cuisine_text = ", ".join(selected_cuisine)
else:
    cuisine_text = "any cuisine"


# Vegetarian Toggle
veg_only = st.sidebar.checkbox("Vegetarian Only 🌿")

diet_restriction = (
    "The recipe MUST be strictly vegetarian."
    if veg_only
    else "The recipe can include meat or be vegetarian."
)


# ---------------------------------------------------------
# Ollama Cloud Configuration
# ---------------------------------------------------------

try:
    OLLAMA_API_KEY = st.secrets["OLLAMA_API_KEY"]
except KeyError:
    st.error(
        "OLLAMA_API_KEY is not configured. "
        "Please add it to Streamlit Secrets."
    )
    st.stop()


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

SYSTEM_PROMPT = f"""
You are GeekCook, a friendly recipe recommendation assistant.

When the user gives you ingredients or asks for a recipe, create an
easy-to-cook recipe using one of these cuisines:

{cuisine_text}

Use this exact format:

## 🍽️ Recipe Name

**Preparation Time:**
**Cooking Time:**
**Servings:**

### 🥕 Ingredients

- List the ingredients required.
- Clearly identify any additional ingredients needed.

### 👨‍🍳 Instructions

1. Give simple step-by-step cooking instructions.
2. Keep the instructions practical for a home cook.
3. Avoid complicated cooking techniques.

### 💡 Tips & Substitutions

- Suggest simple substitutions where appropriate.
- Mention useful cooking tips.

Important rules:

- Before generating, prompt user to provide number of servings and adjust ingredient quantities according to the requested serving size.
- Follow the dietary restriction:
  {diet_restriction}
- Prioritize the ingredients the user has provided.
- Keep recipes beginner-friendly and practical for a normal home kitchen.
- Do not assume the user has unusual ingredients.
- If the user asks to change something about a recipe you already gave
  (swap an ingredient, make it vegetarian, reduce the cooking time,
  serve more people, etc.), return the FULL recipe again in the same
  format, updated accordingly.
- If the user asks a quick clarifying question that isn't about
  changing the recipe, answer briefly in plain sentences instead of
  using the full recipe template.
"""


# ---------------------------------------------------------
# Chat Generation Function
# ---------------------------------------------------------

def generate_reply(messages):

    response = client.chat(
        model=MODEL_NAME,
        messages=messages
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
        '👋 Start by telling GeekCook what ingredients you have — '
        'e.g. "chicken, onion, tomato, garlic, rice, capsicum".'
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

if not has_started:

    placeholder = "What ingredients do you have?"

else:

    placeholder = (
        'Ask for a tweak — e.g. '
        '"make it vegetarian" or "swap rice for pasta"'
    )


user_input = st.chat_input(placeholder)


# ---------------------------------------------------------
# Process User Message
# ---------------------------------------------------------

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
    "The app is still in testing phase, so few errors can occur - please verify before following recipe."
)

