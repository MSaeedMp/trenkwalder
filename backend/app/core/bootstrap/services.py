from google import genai

from app.clients import MCPClient
from app.core.bootstrap.database import Repositories
from app.core.config import Settings
from app.services.chat_service import ChatService
from app.services.directory_service import DirectoryService
from app.services.hr_service import HRService
from app.services.rag_service import RAGService
from app.tools.registry import Services, build_tool_declarations
from pipelines.unstructured.transform import GeminiEmbeddingProvider


def init_services(
    settings: Settings,
    repos: Repositories,
    mcp_client: MCPClient,
) -> ChatService:
    """Wire all services together and return the top-level ChatService."""
    embedder = GeminiEmbeddingProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )

    services = Services(
        rag=RAGService(embedder=embedder, vector_repo=repos.vector),
        directory=DirectoryService(employee_repo=repos.employee),
        hr=HRService(mcp_client=mcp_client),
    )

    return ChatService(
        client=genai.Client(api_key=settings.gemini_api_key),
        services=services,
        tool_declarations=build_tool_declarations(mcp_client),
        conversation_repo=repos.conversation,
        model=settings.gemini_model,
    )
