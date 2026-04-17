import pytest

from app.core.errors.catalog.tool import ToolError
from app.services import HRService


class FakeMCPClient:
    def __init__(self, response: str = '{"ok": true}', error: Exception | None = None) -> None:
        self._response = response
        self._error = error

    async def call(self, name: str, args: dict[str, object]) -> str:
        if self._error:
            raise self._error
        return self._response


@pytest.mark.unit
@pytest.mark.asyncio
async def test_call_forwards_and_returns() -> None:
    fake = FakeMCPClient(response='{"remaining_days": 18}')
    svc = HRService(fake)  # type: ignore[arg-type]
    result = await svc.call("get_vacation_balance", {"employee_id": "me"})
    assert "remaining_days" in result
    assert "18" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_call_wraps_error() -> None:
    fake = FakeMCPClient(error=RuntimeError("connection lost"))
    svc = HRService(fake)  # type: ignore[arg-type]
    with pytest.raises(ToolError, match="connection lost"):
        await svc.call("get_vacation_balance", {"employee_id": "me"})
