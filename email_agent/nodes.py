from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from email_agent.state import EmailAgentState, EmailClassification
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-5-nano")

def read_email(state: EmailAgentState) -> dict:
    """Extract and parse email content"""
    # In production, this would connect to your email service
    return {
        "messages": [HumanMessage(content=f"Processing email: {state['email_content']}")]
    }

def classify_intent(
    state: EmailAgentState,
) -> Command[
    Literal[
        "search_documentation",
        "draft_response",
        "bug_tracking",
    ]
]:
    """Classify the email and route it to the next step."""

    structured_llm = llm.with_structured_output(EmailClassification)

    classification_prompt = f"""
    Analyze this customer email and classify it.

    Email: {state["email_content"]}
    From: {state["sender_email"]}

    Return:
    - intent
    - urgency
    - topic
    - summary
    """

    classification = structured_llm.invoke(classification_prompt)

    if classification["intent"] in ["question", "feature"]:
        goto = "search_documentation"
    elif classification["intent"] == "bug":
        goto = "bug_tracking"
    else:
        goto = "draft_response"

    return Command(
        update={"classification": classification},
        goto=goto,
    )

def search_documentation(
    state: EmailAgentState,
) -> Command[Literal["draft_response"]]:
    """Search knowledge base for relevant information."""

    classification = state.get("classification") or {}

    query = (
        f"{classification.get('intent', '')} "
        f"{classification.get('topic', '')}"
    )

    print(f"Searching documentation for: {query}")

    search_results = [
        "Reset password via Settings > Security > Change Password",
        "Password must be at least 12 characters",
        "Include uppercase, lowercase, numbers, and symbols",
    ]

    return Command(
        update={"search_results": search_results},
        goto="draft_response",
    )

def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """Create or update bug tracking ticket"""

    # Create ticket in your bug tracking system
    ticket_id = "BUG-12345"  # Would be created via API

    return Command(
        update={
            "search_results": [f"Bug ticket {ticket_id} created"],
            "current_step": "bug_tracked"
        },
        goto="draft_response"
    )


def draft_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    """Generate response using context and route based on quality"""

    classification = state.get('classification', {})

    # Format context from raw state data on-demand
    context_sections = []

    if state.get('search_results'):
        # Format search results for the prompt
        formatted_docs = "\n".join([f"- {doc}" for doc in state['search_results']])
        context_sections.append(f"Relevant documentation:\n{formatted_docs}")

    if state.get('customer_history'):
        # Format customer data for the prompt
        context_sections.append(f"Customer tier: {state['customer_history'].get('tier', 'standard')}")

    # Build the prompt with formatted context
    draft_prompt = f"""
    Draft a response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent', 'unknown')}
    Urgency level: {classification.get('urgency', 'medium')}

    {chr(10).join(context_sections)}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided documentation when relevant
    """

    response = llm.invoke(draft_prompt)

    # Determine if human review needed based on urgency and intent
    needs_review = (
        classification.get('urgency') in ['high', 'critical'] or
        classification.get('intent') == 'complex'
    )

    # Route to appropriate next node
    goto = "human_review" if needs_review else "send_reply"

    return Command(
        update={"draft_response": response.content},  # Store only the raw response
        goto=goto
    )



def human_review(
    state: EmailAgentState,
) -> Command[Literal["send_reply", END]]:
    """Pause for human approval."""

    classification = state.get("classification") or {}

    human_decision = interrupt(
        {
            "email_id": state.get("email_id") or "",
            "original_email": state.get("email_content") or "",
            "draft_response": state.get("draft_response") or "",
            "urgency": classification.get("urgency"),
            "intent": classification.get("intent"),
            "action": "Please review and approve or edit this response",
        }
    )

    if human_decision.get("approved"):
        edited_response = (
            human_decision.get("edited_response")
            or state.get("draft_response")
            or ""
        )

        return Command(
            update={"draft_response": edited_response},
            goto="send_reply",
        )

    return Command(goto=END)

def send_reply(state: EmailAgentState) -> dict:
    """Simulate sending the email response."""

    response = state.get("draft_response") or ""

    print("\n--- EMAIL RESPONSE ---")
    print(response)
    print("----------------------")

    return {}