import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hr-service")

VACATION_DATA: dict[str, dict[str, object]] = {
    "me": {"employee_id": "me", "remaining_days": 18, "accrual_rate": 2.08},
    "e001": {"employee_id": "e001", "remaining_days": 22, "accrual_rate": 2.08},
    "e005": {"employee_id": "e005", "remaining_days": 15, "accrual_rate": 2.08},
}

PAYROLL_DATA: dict[str, dict[str, object]] = {
    "me": {"employee_id": "me", "last_payslip": "2026-03-31", "net_eur": 3850.00},
    "e001": {"employee_id": "e001", "last_payslip": "2026-03-31", "net_eur": 5200.00},
    "e005": {"employee_id": "e005", "last_payslip": "2026-03-31", "net_eur": 4600.00},
}


@mcp.tool()
async def get_vacation_balance(employee_id: str = "me") -> dict[str, object]:
    """Use this tool when the user asks about PTO, time off, vacation balance,
    remaining vacation days, or how many days off they have left.
    Returns the number of remaining vacation days and the monthly accrual rate
    for the given employee. Defaults to the current user if no ID is provided."""
    await asyncio.sleep(0.2)
    if employee_id in VACATION_DATA:
        return VACATION_DATA[employee_id]
    return {"employee_id": employee_id, "remaining_days": 0, "accrual_rate": 0.0}


@mcp.tool()
async def get_payroll_summary(employee_id: str = "me") -> dict[str, object]:
    """Use this tool when the user asks about their salary, payslip, pay,
    compensation, net income, or payroll details. Returns the date and net
    amount of the most recent payslip for the given employee. Defaults to
    the current user if no ID is provided."""
    await asyncio.sleep(0.2)
    if employee_id in PAYROLL_DATA:
        return PAYROLL_DATA[employee_id]
    return {"employee_id": employee_id, "last_payslip": "N/A", "net_eur": 0.0}
