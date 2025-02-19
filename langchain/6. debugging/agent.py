import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import (
    START,
    END,
    StateGraph,
    MessagesState,
)
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver


dotenv.load_dotenv()

def simple_graph():
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

    llm_model = ChatOpenAI(temperature=0)
    def call_model(state:MessagesState):
        return{"messages":[llm_model.invoke(state['messages'])]
               }
    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node('assistant', call_model)

    graph_builder.add_edge(START, 'assistant')
    graph_builder.add_edge('assistant', END)

    graph = graph_builder.compile()    

    return graph



def graph_with_tool():
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

    @tool
    def add(a:int, b:int)-> int:
        """
            Adds two integers
        """
        return a+b
    
    llm_model = ChatOpenAI(temperature=0).bind_tools([add])
    def call_model(state:MessagesState):
        return{"messages":[llm_model.invoke(state['messages'])]
               }
    
    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node('assistant', call_model)
    graph_builder.add_node('tools', ToolNode([add]))
    graph_builder.add_edge(START, 'assistant')
    graph_builder.add_conditional_edges('assistant', tools_condition)
    graph_builder.add_edge('tools','assistant')

    graph = graph_builder.compile()    

    return graph


agent = graph_with_tool()


    
