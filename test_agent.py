from langgraph.types import Command

from email_agent.workflow import app


def main() -> None:
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

    config = {
        "configurable": {
            "thread_id": "customer-001",
        }
    }

    result = app.invoke(initial_state, config=config)

    if "__interrupt__" in result:
        print("\nHuman review required:")
        print(result["__interrupt__"])

        decision = {
            "approved": True,
            "edited_response": (
                result.get("draft_response")
                or "Thank you for contacting support."
            ),
        }

        result = app.invoke(
            Command(resume=decision),
            config=config,
        )

    print("\nFinal state:")
    print(result)


if __name__ == "__main__":
    main()