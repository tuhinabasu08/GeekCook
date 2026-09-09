
# 👨‍🍳 GeekCook

## Recipe Recommendation System

GeekCook is an AI-powered recipe recommendation application built with **Python, Streamlit, and Ollama Cloud**.

The application allows users to enter the ingredients they have available and interact with an AI recipe assistant. Users can continue the conversation to modify the recipe — for example, making it vegetarian, swapping ingredients, reducing cooking time, or changing the number of servings.

---

## ✨ Features

* 🥕 Ingredient-based recipe recommendations
* 💬 Conversational recipe refinement
* 🔄 Start-over functionality
* 🥗 Ingredient substitutions
* ⚡ Requests for faster/easier recipes
* 👨‍🍳 Beginner-friendly cooking instructions
* ☁️ Uses Ollama Cloud for AI inference
* 🚀 Deployable on Streamlit Community Cloud
* 🔐 API credentials managed securely through Streamlit Secrets

---

## 🏗️ Architecture

GeekCook uses Streamlit as the application layer and Ollama Cloud as the model inference layer.

```text
┌──────────────────────────────┐
│      Streamlit Web App       │
│                              │
│  • User Interface            │
│  • Chat History              │
│  • Session State             │
└──────────────┬───────────────┘
               │
               │ Ollama Python Client
               │ HTTPS + API Key
               ▼
┌──────────────────────────────┐
│        Ollama Cloud          │
│                              │
│       gpt-oss:120b           │
└──────────────┬───────────────┘
               │
               ▼
        AI-generated recipe
```

### Deployment Architecture

```text
GitHub Repository
       │
       ▼
Streamlit Community Cloud
       │
       │ OLLAMA_API_KEY
       ▼
Ollama Cloud
       │
       ▼
gpt-oss:120b
```

The model does **not** run on the Streamlit Community Cloud instance. Streamlit hosts the application while Ollama Cloud performs the model inference.

---

## 🧠 AI Model

GeekCook uses:

```text
gpt-oss:120b
```

The model is accessed through the Ollama Cloud API.

The application connects to:

```text
https://ollama.com
```

using the Ollama Python client.

---

## 🛠️ Technology Stack

| Component              | Technology                |
| ---------------------- | ------------------------- |
| Programming Language   | Python                    |
| Frontend / Application | Streamlit                 |
| AI Model Provider      | Ollama Cloud              |
| AI Model               | gpt-oss:120b              |
| AI Client              | Ollama Python SDK         |
| Deployment             | Streamlit Community Cloud |
| Source Control         | Git / GitHub              |
| Secrets Management     | Streamlit Secrets         |

---

## 📁 Project Structure

```text
GeekCook/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml        # Local only - do NOT commit
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd GeekCook
```

---

## 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The application requires:

```text
streamlit
ollama
```

---

# 🔑 Ollama Cloud API Key

GeekCook connects to Ollama Cloud using an API key.

The API key should **never be hard-coded into ****`app.py`**** or committed to GitHub**.

The application reads the key using Streamlit Secrets:

```python
OLLAMA_API_KEY = st.secrets["OLLAMA_API_KEY"]
```

The Ollama client is then configured as:

```python
from ollama import Client

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }
)
```

---

# 💻 Local Development

For local development, create the following file:

```text
.streamlit/secrets.toml
```

Add:

```toml
OLLAMA_API_KEY = "your_ollama_api_key"
```

Your local project should therefore look like:

```text
GeekCook/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml
```

### Important

Do **not** commit `secrets.toml` to GitHub.

Add the following to `.gitignore`:

```text
.streamlit/secrets.toml
.venv/
__pycache__/
.env
```

---

# ▶️ Run the Application Locally

Once the dependencies and API key are configured:

```bash
streamlit run app.py
```

Streamlit will start the application locally.

The application can then be opened in your browser using the local URL displayed in the terminal.

---

# ☁️ Deploying to Streamlit Community Cloud

GeekCook can be deployed directly from GitHub using Streamlit Community Cloud.

## Step 1 — Push the project to GitHub

Your GitHub repository should contain:

```text
app.py
requirements.txt
README.md
.gitignore
```

It should **not** contain:

```text
.streamlit/secrets.toml
```

---

## Step 2 — Create the Streamlit Cloud Application

Create a new application in Streamlit Community Cloud.

Select:

* GitHub repository
* Branch
* Main file: `app.py`

---

## Step 3 — Configure Secrets

In the application's advanced settings, add the following secret:

```toml
OLLAMA_API_KEY = "your_ollama_api_key"
```

This replaces the local:

```text
.streamlit/secrets.toml
```

configuration.

The application accesses the value using:

```python
st.secrets["OLLAMA_API_KEY"]
```

---

## Step 4 — Deploy

Once the application is deployed, Streamlit Community Cloud will:

```text
1. Clone the GitHub repository
2. Install requirements.txt
3. Load Streamlit Secrets
4. Start app.py
5. Connect to Ollama Cloud
6. Send prompts to gpt-oss:120b
7. Display the generated response
```

---

# 🔐 Security

The Ollama API key is a sensitive credential.

### Never do this:

```python
client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer sk-xxxxxxxx"
    }
)
```

### Instead use:

```python
OLLAMA_API_KEY = st.secrets["OLLAMA_API_KEY"]
```

and:

```python
client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }
)
```

Also make sure the following file is included in `.gitignore`:

```text
.streamlit/secrets.toml
```

If an API key is accidentally committed to a public repository, revoke/rotate the key immediately.

---

# 💬 How the Chat Works

GeekCook maintains the conversation using Streamlit session state.

The initial conversation contains the system prompt:

```text
system
   │
   ▼
GeekCook instructions
```

When the user enters ingredients:

```text
user
   │
   ▼
"What can I make with chicken, rice and tomatoes?"
```

The conversation is sent to the Ollama Cloud model:

```text
system prompt
      +
conversation history
      +
user message
      │
      ▼
Ollama Cloud
      │
      ▼
gpt-oss:120b
      │
      ▼
recipe response
```

The assistant response is then added to the conversation history.

This allows users to make follow-up requests such as:

```text
"Make it vegetarian."

"Can I use pasta instead of rice?"

"Make it for 4 people."

"Can you make this in under 20 minutes?"
```

GeekCook returns the updated recipe while maintaining the conversation context.

---

# 🧑‍🍳 Recipe Response Format

GeekCook is instructed to structure recipes using:

```text
## 🍽️ Recipe Name

Preparation Time:
Cooking Time:
Servings:

### 🥕 Ingredients

### 👨‍🍳 Instructions

### 💡 Tips & Substitutions
```

The system prompt prioritizes:

* Ingredients provided by the user
* Beginner-friendly recipes
* Normal home-kitchen ingredients
* Simple cooking techniques
* Practical substitutions
* Complete updated recipes when the user requests modifications

---

# ⚙️ Configuration

The primary model configuration is defined in `app.py`:

```python
MODEL_NAME = "gpt-oss:120b"
```

The Ollama Cloud endpoint is:

```python
host="https://ollama.com"
```

The API key is loaded from:

```python
st.secrets["OLLAMA_API_KEY"]
```

---

# 🧪 Testing

Before deploying to Streamlit Community Cloud, test the Ollama connection locally.

You can verify that the model is accessible using:

```python
from ollama import Client

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer YOUR_API_KEY"
    }
)

response = client.chat(
    model="gpt-oss:120b",
    messages=[
        {
            "role": "user",
            "content": "Give me a simple scrambled egg recipe."
        }
    ]
)

print(response.message.content)
```

If this successfully returns a response, the Ollama Cloud connection is working.

---

# 🐛 Troubleshooting

## `KeyError: 'OLLAMA_API_KEY'`

This usually means the Streamlit secret has not been configured.

### Local

Check:

```text
.streamlit/secrets.toml
```

and make sure it contains:

```toml
OLLAMA_API_KEY = "your_api_key"
```

### Streamlit Cloud

Check the application's **Secrets** configuration and ensure:

```toml
OLLAMA_API_KEY = "your_api_key"
```

has been added.

---

## Authentication Error

If Ollama returns an authentication error:

1. Check that the API key is valid.
2. Check that the key has access to the required model.
3. Make sure the key has not expired or been revoked.
4. Verify that the application is connecting to:

```text
https://ollama.com
```

---

## Model Not Found

If `gpt-oss:120b` cannot be accessed:

1. Verify that the model is available through your Ollama Cloud account.
2. Confirm the model name in `app.py`.
3. Test the model using the Ollama client independently.

---

## Application Works Locally but Not on Streamlit Cloud

Check:

```text
✓ requirements.txt is committed
✓ OLLAMA_API_KEY is configured in Streamlit Secrets
✓ secrets.toml is NOT committed to GitHub
✓ app.py is the selected entrypoint
✓ Ollama Cloud API key is valid
✓ gpt-oss:120b is accessible
```

---

# 📦 Dependencies

The current application requires:

```text
streamlit
ollama
```

Install them using:

```bash
pip install -r requirements.txt
```

---

# 🔮 Future Enhancements

Potential future improvements include:

* 🍽️ Dietary preference filters
* ⏱️ Maximum cooking-time filters
* 💰 Budget-based recipe recommendations
* 🌶️ Spice-level preferences
* 🥗 Vegetarian / vegan modes
* 📊 Nutritional information
* 🛒 Automatic grocery lists
* ⭐ Save favourite recipes
* 📸 Image-based ingredient recognition
* 🧠 Personalized recipe recommendations
* 🔐 User authentication
* 📚 Recipe history

---

## 👨‍🍳 GeekCook

**AI-powered recipe recommendations from the ingredients you already have.**

Built with ❤️ using **Python + Streamlit + Ollama Cloud + gpt-oss:120b**.

