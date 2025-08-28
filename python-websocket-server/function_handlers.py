"""
Function handlers for OpenAI Realtime API function calling.

This module defines the available functions that can be called by the AI assistant.
Converted from TypeScript functionHandlers.ts to Python.

Each function handler includes:
1. Schema definition (for OpenAI API)
2. Implementation function (async Python function)
"""

import json
import httpx
from typing import Dict, Any, List
from models import FunctionSchema

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")



async def get_weather_from_coords(latitude: float, longitude: float) -> str:
    """
    Get current weather data from coordinates using Open-Meteo API.
    
    Converted from TypeScript fetch-based implementation to Python httpx.
    
    Args:
        latitude: Geographic latitude
        longitude: Geographic longitude
        
    Returns:
        JSON string containing weather data
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,wind_speed_10m"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
        current_temp = data.get("current", {}).get("temperature_2m")
        return json.dumps({"temp": current_temp})
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch weather: {str(e)}"})

async def search_estrabillio_faq(question: str) -> str:
    """
    Search Estrabillio FAQ knowledge base for answers to customer questions.
    
    Args:
        question: Customer's question about Estrabillio services
        
    Returns:
        JSON string containing the answer or support information
    """
    try:
        # Initialize your RAG components
        index_name = "estrabillio-faq-embedding"
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        
        pc = Pinecone()
        existing_indexes = [i["name"] for i in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            return json.dumps({
                "error": f"Knowledge base not available (index '{index_name}' not found)",
                "fallback": "Please contact our support team at support@estrabillio.com for assistance.",
                "status": "error"
            })
        
        vector_store = PineconeVectorStore(index=pc.Index(index_name), embedding=embeddings)
        
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={'k': 2}
        )
        
        rag_llm = ChatOpenAI(model="gpt-4o-mini")  # Fixed model name
        
        rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""Use the following context to answer the question accurately and completely.

Context: {context}

Question: {question}

Instructions:
- If you can answer the question using the provided context, provide a helpful and detailed response.
- If the context doesn't contain enough information to answer the question, respond with:

"I don't have enough information in my knowledge base to answer your question completely. For personalized assistance, please reach out to our support team:

📧 Email: [email from context]
📞 Phone: [phone no from context]
💬 Live Chat: Available on our website 24/7
🕒 Business Hours: [business hour from context]

Our team will be happy to help you with your specific inquiry."

Answer:"""
        )
        
        retriever_qa = RetrievalQA.from_chain_type(
            llm=rag_llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=False,
            chain_type_kwargs={"prompt": rag_prompt}
        )
        
        # Execute the query
        result = retriever_qa.invoke({"query": question})
        answer = result.get("result", "")
        
        return json.dumps({
            "answer": answer,
            "source": "Estrabillio FAQ Knowledge Base",
            "status": "success"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to search FAQ: {str(e)}",
            "fallback": "Please contact our support team for assistance.",
            "status": "error"
        })


# Function schema definitions (converted from TypeScript interfaces)
WEATHER_SCHEMA = FunctionSchema(
    name="get_weather_from_coords",
    type="function",
    description="Get the current weather from geographic coordinates",
    parameters={
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Geographic latitude coordinate"
            },
            "longitude": {
                "type": "number", 
                "description": "Geographic longitude coordinate"
            }
        },
        "required": ["latitude", "longitude"]
    }
)

FAQ_SCHEMA = FunctionSchema(
    name="search_estrabillio_faq",
    type="function", 
    description="Search Estrabillio FAQ knowledge base for answers to customer questions about services, policies, pricing, support, and general inquiries",
    parameters={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The customer's question about Estrabillio services, policies, or general inquiries"
            }
        },
        "required": ["question"]
    }
)

class FunctionRegistry:
    """
    Registry for managing function handlers and their schemas.
    
    Converted from TypeScript array-based approach to a more structured
    Python class-based registry pattern.
    """
    
    def __init__(self):
        self._functions: Dict[str, Dict[str, Any]] = {}
        self._register_default_functions()
    
    def _register_default_functions(self):
        """Register the default set of functions"""
        self.register_function(
            schema=WEATHER_SCHEMA,
            handler=get_weather_from_coords
        )

        self.register_function(
            schema=FAQ_SCHEMA,
            handler=search_estrabillio_faq
        )
    
    def register_function(self, schema: FunctionSchema, handler):
        """
        Register a new function with its schema and handler.
        
        Args:
            schema: OpenAI function schema
            handler: Async function implementation
        """
        self._functions[schema.name] = {
            "schema": schema,
            "handler": handler
        }
    
    def get_function_schemas(self) -> List[FunctionSchema]:
        """
        Get all registered function schemas.
        
        Returns:
            List of function schemas for OpenAI API
        """
        return [func_data["schema"] for func_data in self._functions.values()]
    
    async def call_function(self, name: str, arguments: str) -> str:
        """
        Call a registered function with the provided arguments.
        
        Converted from TypeScript promise-based approach to Python async/await.
        
        Args:
            name: Function name to call
            arguments: JSON string of function arguments
            
        Returns:
            JSON string result from function execution
        """
        if name not in self._functions:
            return json.dumps({
                "error": f"No handler found for function: {name}"
            })
        
        try:
            # Parse arguments (equivalent to JSON.parse in TypeScript)
            args = json.loads(arguments)
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Invalid JSON arguments for function call"
            })
        
        try:
            handler = self._functions[name]["handler"]
            
            # Call the handler with unpacked arguments
            if isinstance(args, dict):
                result = await handler(**args)
            else:
                result = await handler(args)
                
            return result
            
        except Exception as e:
            return json.dumps({
                "error": f"Error running function {name}: {str(e)}"
            })


# Global function registry instance
function_registry = FunctionRegistry()


def get_function_schemas() -> List[FunctionSchema]:
    """
    Get all available function schemas.
    
    Equivalent to the default export array in TypeScript version.
    """
    return function_registry.get_function_schemas()


async def handle_function_call(name: str, arguments: str) -> str:
    """
    Handle a function call from the OpenAI Realtime API.
    
    Converted from TypeScript handleFunctionCall function.
    
    Args:
        name: Function name
        arguments: JSON string of arguments
        
    Returns:
        JSON string result
    """
    return await function_registry.call_function(name, arguments)
