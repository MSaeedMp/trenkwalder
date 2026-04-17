from google.genai import types

LOCAL_TOOLS: list[types.FunctionDeclaration] = [
    types.FunctionDeclaration(
        name="search_documents",
        description=(
            "Search the company knowledge base (handbook, benefits, code of conduct) "
            "for information. Use this when the user asks about company policies, "
            "procedures, benefits, leave rules, expenses, remote work, or any topic "
            "covered in internal documents. Returns relevant text passages with source "
            "and section for citation."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "query": types.Schema(
                    type=types.Type.STRING,
                    description="The search query describing what information is needed",
                ),
                "source_filter": types.Schema(
                    type=types.Type.STRING,
                    description="Optional filename to restrict search to a specific document",
                ),
            },
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="find_employees",
        description=(
            "Search the employee directory by name, department, or role. "
            "Use this when the user asks about a specific person, who works in a "
            "department, or who has a particular role. At least one search parameter "
            "is required."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "name": types.Schema(
                    type=types.Type.STRING,
                    description="Full or partial employee name to search for",
                ),
                "department": types.Schema(
                    type=types.Type.STRING,
                    description="Department name (e.g. Engineering, Sales, HR, Finance)",
                ),
                "role": types.Schema(
                    type=types.Type.STRING,
                    description="Job role or title to search for",
                ),
            },
        ),
    ),
    types.FunctionDeclaration(
        name="get_department_headcount",
        description=(
            "Get the number of employees per department. Use this when the user asks "
            "how many people work in a department, team sizes, or headcount breakdowns. "
            "If no department is specified, returns a breakdown of all departments."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "department": types.Schema(
                    type=types.Type.STRING,
                    description="Optional department name to get headcount for",
                ),
            },
        ),
    ),
]
