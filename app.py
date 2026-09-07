import streamlit as st
from ollama import chat


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
    "Have some ingredients but don't know what to cook? "
    "Enter what you have and GeekCook will suggest an "
    "easy-to-cook recipe."
)


# ---------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------

MODEL_NAME = "qwen2.5:3b"


# ---------------------------------------------------------
# Recipe Generation Function
# ---------------------------------------------------------

def generate_recipe(ingredients):

    prompt = f"""
You are GeekCook, a friendly recipe recommendation assistant.

The user has the following ingredients:

{ingredients}

Create an easy-to-cook recipe using these ingredients.

Please provide the answer in exactly this format:

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

- Prioritize the ingredients provided by the user.
- Keep the recipe beginner-friendly.
- Do not assume the user has unusual ingredients.
- Keep the recipe practical for a normal home kitchen.
"""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content


# ---------------------------------------------------------
# User Input
# ---------------------------------------------------------

with st.form("recipe_form"):

    st.markdown("### 🥕 What ingredients do you have?")

    user_input = st.text_area(
        "Enter ingredients separated by commas",
        placeholder=(
            "Example: chicken, onion, tomato, "
            "garlic, rice, capsicum"
        ),
        height=120
    )

    submitted = st.form_submit_button(
        "🍳 Get Recipe Recommendations",
        use_container_width=True
    )


# ---------------------------------------------------------
# Generate Recipe
# ---------------------------------------------------------

if submitted:

    if not user_input.strip():

        st.warning(
            "⚠️ Please enter at least one ingredient."
        )

    else:

        with st.spinner(
            "👨‍🍳 GeekCook is preparing your recipe..."
        ):

            try:

                recipe = generate_recipe(user_input)

                st.markdown("---")

                st.markdown(recipe)

            except Exception as e:

                st.error(
                    "❌ Something went wrong while "
                    "generating your recipe."
                )

                st.caption(
                    f"Error details: {str(e)}"
                )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("---")

st.caption(
    "GeekCook 👨‍🍳 | Powered by Ollama + Qwen"
)

