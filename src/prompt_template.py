
CONCISE_ANSWER_PROMPT = """
Given page:
- Title: {title}
- URL: {url}
- Content:
\"\"\"
{details}
\"\"\"

Generate a concise answer to the query: \"{query}\"
"""