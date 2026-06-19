from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

def planner_agent(query):
    prompt = f"""
    You are a planner agent.

    Break the problem into steps.

    Query:
    {query}
    """

    response = llm.invoke(prompt)

    return response.content


def executor_agent(plan):
    prompt = f"""
    Execute this plan.

    Plan:
    {plan}
    """

    response = llm.invoke(prompt)

    return response.content


def verifier_agent(query, result):

    prompt = f"""
    Verify whether result satisfies user request.

    User Query:
    {query}

    Result:
    {result}

    Return only:

    PASS
    or
    FAIL

    Then reason.
    """

    response = llm.invoke(prompt)

    return response.content