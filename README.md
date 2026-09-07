# GeekCook

## Local AI-Powered Recipe Recommendation System

**Technology Stack:** Python, Streamlit, Ollama, Qwen2.5 3B
**Application Type:** AI-powered web application
**Deployment Model:** Local machine
**AI Model:** `qwen2.5:3b`

---

## 1. Project Overview

GeekCook is an AI-powered Recipe Recommendation System that generates easy-to-cook recipes based on ingredients provided by the user.

The application provides a simple web interface where users enter the ingredients available to them. The application sends these ingredients to a locally hosted Large Language Model (LLM) through Ollama. The generated recipe is then displayed in the Streamlit interface.

The current implementation uses the following architecture:

**User → Streamlit → Ollama Python Library → Qwen2.5 3B → Recipe Response → Streamlit**

Unlike cloud-based LLM applications that require an external API key, GeekCook runs the language model locally through Ollama. This eliminates the requirement for OpenAI or Hugging Face API credentials.

---

# 2. Objectives

The primary objectives of GeekCook are:

1. Build a simple AI-powered recommendation application.
2. Allow users to provide ingredients available at home.
3. Generate practical recipes using those ingredients.
4. Provide beginner-friendly cooking instructions.
5. Use a locally hosted open-source LLM.
6. Avoid dependency on paid cloud-based AI APIs.
7. Provide a simple and responsive user interface.
8. Demonstrate integration between a Python application, Streamlit and an LLM.

---

# 3. Functional Requirements

The system should allow the user to:

* Enter multiple ingredients.
* Submit the ingredients for processing.
* Receive an automatically generated recipe.
* View preparation time.
* View cooking time.
* View serving information.
* View required ingredients.
* View cooking instructions.
* View tips and substitutions.

The application should also:

* Validate that the user has entered ingredients.
* Display a loading indicator while the model generates the response.
* Handle errors gracefully.
* Display the generated recipe in a readable format.

---

# 4. Non-Functional Requirements

### Performance

The application should provide the generated recipe as soon as the locally hosted model completes inference.

Performance depends primarily on:

* Computer hardware.
* Available RAM.
* CPU/GPU capabilities.
* Size of the selected LLM.
* Complexity of the prompt.

### Usability

The application should provide a simple interface requiring minimal user interaction.

The current application uses a text area and a single submit button.

### Security

No external API credentials are required.

Since the model runs locally, the user's ingredient input is sent to the local Ollama service rather than to a third-party hosted LLM API.

### Maintainability

The application separates:

* UI configuration
* Model configuration
* Recipe generation
* User input
* Response handling

This makes it relatively easy to replace the model or extend the application.

---

# 5. Technology Stack

## 5.1 Python

Python is used as the primary programming language.

Python handles:

* Application logic
* User input processing
* Prompt construction
* Communication with Ollama
* Error handling

---

## 5.2 Streamlit

Streamlit is used to build the web interface.

The current application configures:

* Page title
* Page icon
* Page layout
* Application title
* User input area
* Submit button
* Loading indicator
* Error messages
* Generated recipe output

Streamlit's `st.form` is used to group the input field and submit button so that the values are submitted together rather than triggering application execution for every interaction.

The application uses `st.text_area` for multi-line ingredient input.

---

## 5.3 Ollama

Ollama provides the local LLM runtime.

Instead of sending requests to a cloud-based AI service, Ollama runs the selected model locally on the user's computer.

The Python application communicates with Ollama through its Python library.

---

## 5.4 Qwen2.5 3B

GeekCook currently uses:

```text
qwen2.5:3b
```

The model name is stored in a dedicated configuration variable:

```python
MODEL_NAME = "qwen2.5:3b"
```

This makes model replacement straightforward.

For example, a future version could replace the model with another Ollama-supported model without changing the overall application architecture.

---

# 6. System Architecture

The application follows a simple request-response architecture.

```text
┌─────────────────────────────┐
│          User               │
│                             │
│ chicken, onion, tomato      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        Streamlit UI         │
│                             │
│  Ingredient Text Area       │
│  Submit Button              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     generate_recipe()       │
│                             │
│  Builds structured prompt   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Ollama Python API      │
│                             │
│       chat()                │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Ollama Runtime        │
│                             │
│     qwen2.5:3b              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Generated Recipe       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Streamlit UI          │
│                             │
│   Recipe displayed to user  │
└─────────────────────────────┘
```

---

# 7. Project Structure

The current project consists of two primary files:

```text
Recipe_Recommender/
│
├── app.py
│
└── requirements.txt
```

The application does not require:

```text
.streamlit/secrets.toml
```

because no external API key is used.

---

# 8. Dependencies

The current `requirements.txt` contains:

```text
streamlit
ollama
```

These two packages provide the primary application functionality.

### Streamlit

Used for building the web application interface.

### Ollama

Used by Python to communicate with the locally running Ollama model.

---

# 9. Application Implementation

## 9.1 Imports

The application begins with:

```python
import streamlit as st
from ollama import chat
```

Streamlit provides the user interface functionality, while `chat` is imported from the Ollama Python library to communicate with the model.

---

# 10. Page Configuration

The application configures the Streamlit page using:

```python
st.set_page_config(
    page_title="GeekCook | Recipe Recommendation System",
    page_icon="👨‍🍳",
    layout="centered"
)
```

This establishes:

* Browser page title
* Chef emoji as the application icon
* Centered page layout

The configuration is intended to give the application a dedicated product-like identity.

---

# 11. User Interface

The application displays the title:

```text
👨‍🍳 GeekCook
Recipe Recommendation System
```

It also provides an explanation of the application's purpose:

```text
Have some ingredients but don't know what to cook?
Enter what you have and GeekCook will suggest an
easy-to-cook recipe.
```

These elements are implemented using Streamlit's title, subheader and text functions.

---

# 12. Model Configuration

The model is configured using a single variable:

```python
MODEL_NAME = "qwen2.5:3b"
```

This is an important design decision because it prevents the model name from being duplicated throughout the application.

If the model needs to be changed in the future, only the configuration value needs to be updated.

---

# 13. Recipe Generation Function

The core AI functionality is implemented inside:

```python
def generate_recipe(ingredients):
```

The function accepts the ingredients entered by the user.

The ingredients are then inserted into a structured prompt.

The current implementation explicitly tells the model to behave as:

```text
GeekCook, a friendly recipe recommendation assistant.
```

It then provides the user's ingredients to the model and asks it to create an easy-to-cook recipe.

---

# 14. Prompt Engineering

Prompt engineering is an important component of GeekCook.

Rather than simply asking:

```text
Give me a recipe.
```

the application provides a detailed output specification.

The model is instructed to return:

### Recipe Name

### Preparation Time

### Cooking Time

### Servings

### Ingredients

### Instructions

### Tips & Substitutions

The application also specifies that the instructions should be:

* Simple
* Practical
* Beginner-friendly
* Suitable for a normal home kitchen

The prompt further instructs the model to prioritize the ingredients supplied by the user and avoid assuming unusual ingredients.

This structured prompt improves consistency and makes the model's output easier to display in the Streamlit interface.

---

# 15. Communication with the LLM

Once the prompt has been constructed, the application invokes Ollama:

```python
response = chat(
    model=MODEL_NAME,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
```

The model receives the prompt as a user message.

The generated response is then extracted using:

```python
return response.message.content
```

This is the central AI inference step in the application.

---

# 16. User Input

The application uses a Streamlit form:

```python
with st.form("recipe_form"):
```

Inside the form, the user is presented with a multi-line text area.

Example placeholder:

```text
chicken, onion, tomato, garlic, rice, capsicum
```

The user input is stored in:

```python
user_input
```

The application also provides the button:

```text
🍳 Get Recipe Recommendations
```

The relevant implementation is contained in the user-input section of `app.py`.

---

# 17. Input Validation

Before sending the request to the LLM, the application checks whether the user entered any ingredients:

```python
if not user_input.strip():
```

If the input is empty, the application displays:

```text
⚠️ Please enter at least one ingredient.
```

This prevents unnecessary LLM calls and provides immediate feedback to the user.

---

# 18. Loading State

LLM inference can take some time, particularly when the model is running locally.

The application therefore displays a spinner:

```python
with st.spinner(
    "👨‍🍳 GeekCook is preparing your recipe..."
):
```

This provides visual feedback while the model is generating the recipe.

---

# 19. Error Handling

The model invocation is wrapped in a `try/except` block.

If an exception occurs, the application displays:

```text
❌ Something went wrong while generating your recipe.
```

The actual exception is also displayed as supporting diagnostic information.

This prevents the Streamlit application from failing silently and makes troubleshooting easier during development.

---

# 20. Recipe Display

Once the model successfully generates a response, the application displays it using:

```python
st.markdown(recipe)
```

Because the prompt requests Markdown-compatible headings and lists, the generated recipe can be rendered in a structured format directly within Streamlit.

---

# 21. End-to-End Execution Flow

The complete execution flow is:

### Step 1 — Application Startup

The user starts the application using:

```bash
streamlit run app.py
```

### Step 2 — Streamlit Initialization

Streamlit loads the page configuration and user interface.

### Step 3 — Ingredient Input

The user enters ingredients such as:

```text
chicken, onion, tomato, garlic, rice
```

### Step 4 — Form Submission

The user clicks:

```text
Get Recipe Recommendations
```

The Streamlit form submits the input as a batch. Streamlit forms are specifically designed to batch widget values until submission.

### Step 5 — Input Validation

The application verifies that the input is not empty.

### Step 6 — Prompt Creation

The ingredients are inserted into the predefined GeekCook prompt.

### Step 7 — Local LLM Request

Python calls:

```python
chat(
    model=MODEL_NAME,
    messages=[...]
)
```

### Step 8 — Model Inference

Ollama sends the prompt to:

```text
Qwen2.5 3B
```

running locally.

### Step 9 — Response Generation

Qwen generates the recipe.

### Step 10 — Response Extraction

The application extracts:

```python
response.message.content
```

### Step 11 — UI Rendering

Streamlit renders the generated Markdown recipe.

---

# 22. Why Local LLM Inference?

The original application architecture used hosted LLM APIs.

The local Ollama architecture has several advantages.

## Cost

No per-request OpenAI or hosted inference charge is required.

## Privacy

Ingredient information is processed locally rather than being sent to an external hosted LLM service.

## Offline Capability

Once Ollama and the model are installed, inference can be performed without depending on an external API service.

## Learning Value

The architecture provides practical exposure to:

* LLMs
* Prompt engineering
* Local inference
* Python APIs
* Streamlit
* AI application development

---

# 23. Limitations

The current implementation has several limitations.

## 23.1 Hardware Dependency

The model runs on the user's computer, so response speed depends on available CPU/GPU resources and memory.

## 23.2 Recipe Accuracy

The generated recipes are AI-generated and may contain inaccurate measurements, substitutions or cooking instructions.

The system should therefore be treated as a recommendation tool rather than a guaranteed culinary authority.

## 23.3 No Recipe Database

The current application does not use a structured recipe database.

Recipes are generated dynamically by the LLM.

## 23.4 No Personalization

The current implementation does not collect:

* Dietary preferences
* Allergies
* Cuisine preferences
* Cooking skill
* Maximum cooking time
* Calorie requirements

These can be added in future versions.

## 23.5 No Conversation Memory

Each recipe request is independent.

The application does not currently maintain conversation history between requests.

---

# 24. Future Enhancements

The current architecture provides a strong foundation for additional functionality.

### 24.1 Cuisine Selection

Add a dropdown:

```text
Indian
Chinese
Italian
Continental
Mexican
Bengali
```

The selected cuisine can be included in the prompt.

### 24.2 Dietary Preferences

Allow users to select:

```text
Vegetarian
Non-Vegetarian
Vegan
High Protein
Low Carb
```

### 24.3 Cooking Time

Allow the user to specify:

```text
15 minutes
30 minutes
45 minutes
1 hour
```

The model can then generate recipes within that constraint.

### 24.4 Difficulty Level

Provide:

```text
Easy
Medium
Advanced
```

### 24.5 Serving Size

Allow users to specify the number of people.

### 24.6 Allergy Management

Users could specify allergens such as:

```text
Peanuts
Dairy
Eggs
Shellfish
Gluten
```

The information could be incorporated into the prompt.

### 24.7 Recipe History

Store previous recommendations in a local database such as SQLite.

### 24.8 Favorites

Allow users to save recipes they like.

### 24.9 Nutritional Information

A future version could calculate or retrieve:

* Calories
* Protein
* Carbohydrates
* Fat
* Fiber

### 24.10 Image Generation

A future version could generate or retrieve a visual representation of the finished recipe.

---

# 25. Testing Strategy

The application should be tested using multiple categories of inputs.

## Test Case 1 — Valid Ingredients

**Input:**

```text
chicken, onion, tomato, garlic
```

**Expected Result:**

A valid chicken-based recipe is generated.

---

## Test Case 2 — Single Ingredient

**Input:**

```text
eggs
```

**Expected Result:**

The system generates a recipe using eggs.

---

## Test Case 3 — Empty Input

**Input:**

```text
```

**Expected Result:**

```text
Please enter at least one ingredient.
```

---

## Test Case 4 — Multiple Ingredients

**Input:**

```text
rice, onion, carrot, capsicum, soy sauce
```

**Expected Result:**

The model generates an appropriate rice-based recipe.

---

## Test Case 5 — Unusual Combination

**Input:**

```text
banana, tomato, rice, chocolate
```

**Expected Result:**

The application should still return a model response, although the recipe may require user judgment.

---

## Test Case 6 — Ollama Unavailable

If Ollama is not running, the application should enter the exception handler and display an appropriate error message.

---

# 26. Deployment Model

The current application is designed for local execution.

Required components:

```text
Mac / PC
│
├── Python
│
├── Streamlit
│
├── Ollama
│
└── Qwen2.5 3B
```

The user starts Ollama and then starts the Streamlit application.

The application communicates with the locally running model rather than a cloud API.

---

# 27. Installation Procedure

## Step 1 — Install Python

Install Python on the development machine.

## Step 2 — Create Virtual Environment

```bash
python -m venv .venv
```

Activate it:

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

The current requirements file contains Streamlit and Ollama.

## Step 4 — Install Ollama

Install Ollama on the development machine.

## Step 5 — Download the Model

```bash
ollama pull qwen2.5:3b
```

## Step 6 — Verify the Model

```bash
ollama list
```

The Qwen model should appear in the list.

## Step 7 — Start the Application

```bash
streamlit run app.py
```

---

# 28. Security Considerations

The current architecture eliminates the need for API keys.

There is no:

```text
OPENAI_API_KEY
HF_TOKEN
```

required by the application.

This also means there is no need for:

```text
.streamlit/secrets.toml
```

in the current architecture.

However, if future functionality introduces external services, credentials should be stored using environment variables or Streamlit secrets rather than hard-coded into the source code.

---

# 29. Current Application Summary

The current GeekCook implementation can be summarized as:

```text
INPUT
  │
  │ Ingredients
  ▼
STREAMLIT
  │
  │ Prompt
  ▼
OLLAMA
  │
  │ Local inference
  ▼
QWEN2.5 3B
  │
  │ Generated recipe
  ▼
STREAMLIT
  │
  ▼
OUTPUT
```

The implementation is intentionally lightweight: the current `app.py` contains the UI, model configuration, prompt construction, model invocation, validation, error handling and response rendering in one application file.

---

# 30. Conclusion

GeekCook demonstrates how a traditional Python web application can be enhanced with a locally hosted Large Language Model.

The system combines:

* **Python** for application logic
* **Streamlit** for the web interface
* **Ollama** for local LLM execution
* **Qwen2.5 3B** for recipe generation
* **Prompt engineering** for structured recipe recommendations

The architecture is simple enough for a learning project while providing a practical introduction to modern Generative AI application development.

The use of a local model also removes the need for cloud API credentials and provides a cost-effective environment for experimentation.

The current design can subsequently be extended into a more complete personalized recipe platform by adding dietary preferences, cuisine selection, nutritional analysis, recipe history, favorites, and personalization.
