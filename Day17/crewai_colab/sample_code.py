from crewai import Agent, Task, Crew, LLM
import os

# Choose LLM (OpenAI or Groq)

llm = LLM(
    model="gpt-4o-mini",  # OpenAI model OR Groq model like "llama3-70b-8192"
)

# 1. Create Agent
agent = Agent(
    role="Tester Agent",
    goal="Check if API key is working",
    backstory="You are a system tester",
    llm=llm,
    verbose=True
)

# 2. Create Task
task = Task(
    description="Say 'API is working successfully' and nothing else.",
    expected_output="A confirmation message",
    agent=agent
)

# 3. Crew (Team)
crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

# 4. Run
result = crew.kickoff()

print("\nFINAL OUTPUT:\n")
print(result)