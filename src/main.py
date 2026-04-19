import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables.graph import MermaidDrawMethod
# from IPython.display import display, Image
from dotenv import load_dotenv
import os
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

class PlannerState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "The messages in the conversation"]
    city: str
    interests: List[str]
    itinerary: str

llm = ChatOpenAI(model="gpt-4o-mini")


itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a day trip itinerary for {city} based on the user's interests: {interests}. Provide a brief, bulleted itinerary."),
    ("human", "Create an itinerary for my day trip."),
])

def input_city(state: PlannerState)-> PlannerState:
    print("Please enter the city you want to visit for your day trip: ")
    user_message = input("your input: ")
    return {
        **state,
        "city":user_message,
        "messages": state['messages']+ [HumanMessage(content=user_message)],
        }

def input_interests(state: PlannerState)-> PlannerState:
    print(f"Please enter your interests for the trip to {state['city']} (comma-separated):")
    user_message = input("Your input: ")
    return {
        **state,
        "interests": [interest.strip() for interest in user_message.split(',')],
        "messages": state['messages'] + [HumanMessage(content=user_message)],
}

def create_itinerary(state:PlannerState) -> PlannerState:
    print(f"Creating an itinerary for {state['city']} based on interests: {', '.join(state['interests'])}..")
    response = llm.invoke(itinerary_prompt.format_messages(city=state['city'], interests=", ".join(state['interests'])))
    print("\n Final Itinerary:")
    print(response.content)
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response.content)],
        "itinerary": response.content,
        }

workflow  = StateGraph(PlannerState)

workflow.add_node("input_city", input_city)
workflow.add_node("input_interests", input_interests)
workflow.add_node("create_itinerary", create_itinerary)

workflow.set_entry_point("input_city")

workflow.add_edge("input_city", "input_interests")
workflow.add_edge("input_interests", "create_itinerary")
workflow.add_edge("create_itinerary", END)

app = workflow.compile()

# Display the graph structure

# display(
#     Image(
#         app.get_graph().draw_mermaid_png(
#             draw_method=MermaidDrawMethod.API,
#             )
#         )
#     )

# Add this import at the top
from langchain_core.runnables.graph import MermaidDrawMethod

# Replace the commented block with this
png_data = app.get_graph().draw_mermaid_png(
    draw_method=MermaidDrawMethod.API,
)
with open("graph.png", "wb") as f:
    f.write(png_data)
print("Graph saved to graph.png")

def run_travel_planner(user_request:str):
    print(f"Initial Request: {user_request}\n")
    state = {
        "messages": [HumanMessage(content=user_request)],
        "city": "",
        "interests": [],
        "itinerary": "",
        }

    for output in app.stream(state):
        pass

if __name__=="__main__":
    user_request = "I want to plan a day trip."
    run_travel_planner(user_request)

    print('Done Execution')