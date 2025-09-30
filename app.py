# app.py
import os
import sys
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Union
from dotenv import load_dotenv


from factories.agent_factory import UnifiedAgentFactory
from factories.service_factory import ServiceFactory
from factories.model_client_factory import get_factories
from services.routing_service import RoutingService
from Mcp.Mcp_Client import get_mcp_tools

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# -----------------------------
# Request/Response Models
# -----------------------------
class ChatRequest(BaseModel):
    input: Union[str, bytes]  # input can be string or audio file
    user_id: Optional[str] = "default_user"
    session_id: Optional[str] = None

# -----------------------------
# Initialize FastAPI
# -----------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------------
# Initialize model client and factories
# -----------------------------
factories = get_factories()
model_client = factories["azure"].create_autogen_client()
agent_factory = UnifiedAgentFactory(model_client)
service_factory = ServiceFactory(agent_factory=agent_factory)

# -----------------------------
# Register your stateful services
# -----------------------------
from services.goal_service import GoalService
from services.planning_service import PlanningService
from services.questionnaire_service import QuestionnaireService
from services.recommender_service import RecommenderService

service_factory.register_service("goal_service", GoalService(agent_factory))
service_factory.register_service("planning_service", PlanningService(agent_factory))
service_factory.register_service("questionnaire_service", QuestionnaireService(agent_factory))
service_factory.register_service("recommender_service", RecommenderService(agent_factory))

# -----------------------------
# Initialize RoutingService
# -----------------------------
routing_service = RoutingService(
    service_factory=service_factory,
    agent_factory=agent_factory,
    model_client=model_client
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Serve the HTML file from frontend directory
    return FileResponse("test.html")


# -----------------------------
# Health check
# -----------------------------
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "RoutingService API running"}

# -----------------------------
# Chat endpoint
# -----------------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_message = request.input
        user_id = request.user_id or "default_user"
        session_id = request.session_id or f"session_{user_id}"

        if not user_message:
            return JSONResponse(
                content={
                    "error": "Message input is required",
                    "success": False,
                    "status_code": 400
                },
                status_code=400
            )

        print(f"Processing message from user {user_id}: {user_message}")

        # --- Delegate message through RoutingService ---
        response = await routing_service.route(user_message, context=f"user_id: {user_id}")

        # --- Ensure response is JSON safe and add agent info ---
        if isinstance(response, dict):
            # Add agent information if not present
            if 'agent' not in response and hasattr(routing_service, 'active_service') and routing_service.active_service:
                response['agent'] = routing_service.active_service.name
            elif 'agent' not in response:
                # Try to determine agent from routing service logic
                routing_agent_name = None
                if hasattr(routing_service, 'routing_agent') and routing_service.routing_agent:
                    # Map service name back to agent name
                    service_to_agent = {
                        "planning_service": "goal_planning_agent",
                        "goal_service": "goal_suggest_agent", 
                        "questionnaire_service": "questionnaire_agent",
                        "form_service": "questionnaire_agent",
                        "recommender_service": "recommender_agent",
                        "personalization_service": "personalization_agent"
                    }
                    if routing_service.active_service:
                        # Find the service name and map to agent
                        for service_name, agent_name in service_to_agent.items():
                            if routing_service.active_service.name.lower().replace(" ", "_") + "_service" == service_name:
                                routing_agent_name = agent_name
                                break
                response['agent'] = routing_agent_name or "unknown"
            # Add success status code
            response['status_code'] = 200
            return JSONResponse(content=response, status_code=200)
        else:
            # Fallback for non-dict responses
            return JSONResponse(
                content={
                    "response": str(response),
                    "agent": "unknown", 
                    "success": True,
                    "status_code": 200
                },
                status_code=200
            )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            content={
                "error": str(e),
                "success": False,
                "status_code": 500
            },
            status_code=500
        )

# -----------------------------
# Optional: MCP test endpoint
# -----------------------------
@app.get("/api/test-mcp")
async def test_mcp():
    try:
        mcp_tools = await get_mcp_tools()
        return {
            "status": "ok",
            "tools_count": len(mcp_tools),
            "tool_names": [t.name for t in mcp_tools]
        }
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
