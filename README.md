# LangGraph Email Support Agent

A simple customer-support email agent built with **LangGraph**, **LangChain**, and **OpenAI**.

The agent reads a customer email, classifies its intent and urgency, searches relevant support information, generates a response, and decides whether the response should be sent directly or reviewed by a human.

> This project is currently a local prototype. The `send_reply()` node prints the generated email response in the terminal. It does not send a real email.

---

## Features

- Reads customer email content
- Classifies email intent and urgency
- Identifies the email topic
- Routes emails to the correct workflow
- Searches mock support documentation
- Creates mock bug-tracking tickets
- Generates professional email responses
- Supports human approval using LangGraph interrupts
- Preserves workflow state using a checkpointer
- Prints the final response in the terminal

---

## Workflow

The main workflow is:

```text
START
  |
  v
Read Email
  |
  v
Classify Intent
  |
  +-------------------------------+
  |               |               |
  v               v               v
Document Search   Bug Tracking    Draft Response
  |               |               |
  +---------------+---------------+
                  |
                  v
             Draft Response
                  |
          +-------+--------+
          |                |
          v                v
     Human Review      Send Reply
          |                |
          +-------+--------+
                  |
                  v
                 END


The agent performs the following tasks:

- Reads incoming customer emails
- Classifies email intent and urgency
- Identifies the email topic
- Searches relevant documentation (currently mocked)
- Generates a professional support response
- Routes complex or high-priority emails for human review
- Simulates sending the final response by printing it to the terminal

The project follows LangGraph's node-based workflow architecture, where each node performs one specific task and passes updated state to the next node.

---

# Installation

### Clone the repository

```bash
git clone <your-github-repository-url>
cd AI_LangGraph
```

### Create or activate your Python environment

If using Conda:

```bash
conda activate C:\Users\Hp\AI_LangGraph\Lenv
```

If using a virtual environment:

```bash
source Lenv/bin/activate
```

Windows:

```bash
Lenv\Scripts\activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

# Requirements

- Python 3.11+
- LangGraph
- LangChain
- LangChain OpenAI
- python-dotenv
- Pydantic
- Typing Extensions
- OpenAI API Key

Example `requirements.txt`

```text
langgraph
langchain
langchain-openai
python-dotenv
pydantic
typing_extensions
ipykernel
```

---

# OpenAI API Key Setup

Create a file named **`.env`** in the project root.

```text
AI_LangGraph/
│
├── .env
├── requirements.txt
├── test_agent.py
└── email_agent/
```

Add your OpenAI API Key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Verify that the API key is loaded correctly:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(bool(os.getenv('OPENAI_API_KEY')))"
```

Expected output:

```text
True
```

---

# Running the Project

Run the test workflow from the project root:

```bash
python test_agent.py
```

Example test input:

```python
initial_state = {
    "email_content": "How can I reset my password?",
    "sender_email": "customer@example.com",
    "email_id": "email-001",
    "classification": None,
    "search_results": None,
    "customer_history": None,
    "draft_response": None,
    "messages": None,
}
```

Example workflow execution:

```text
START
   │
   ▼
Read Email
   │
   ▼
Classify Intent
   │
   ▼
Search Documentation
   │
   ▼
Draft Response
   │
   ▼
Send Reply
   │
   ▼
END
```

Expected terminal output:

```text
Searching documentation for: question password reset

--- EMAIL RESPONSE ---
Subject: How to reset your password

Hello,

Here’s how you can reset your password...

----------------------

Final state:
{
    ...
}
```

> **Note:** The current implementation of `send_reply()` only prints the generated email response to the terminal. It does **not** send a real email. This allows the workflow to be safely tested without integrating an email service such as Gmail, Outlook, SMTP, or SendGrid.