from graph.graph_builder import graph
from langsmith import traceable

class OrchestratorAgent:
    @traceable(name="AutoHealAI Workflow")
    def run(self, city, weather_result, failure_mode):

        state = {
            "city": city,
            "failure_mode": failure_mode,
            "weather_result": weather_result,
            "monitoring": None,
            "diagnosis": None,
            "healing": None,
            "verification": None,
            "ticket": None,
        }

        result = graph.invoke(state)

        return {
            "incident": result["monitoring"],
            "diagnosis": result["diagnosis"],
            "healing": result["healing"],
            "verification": result["verification"],
            "ticket": result["ticket"],
        }