
CONCISE_ANSWER_PROMPT = """
Given page:
- Title: {title}
- URL: {url}
- Summary: {summary}
- Content:
\"\"\"
{details}
\"\"\"

Generate useful information that need to answer the query : \"{query}\" in language which used in the query.
If given page does not contain the answer, return "Page does not contain the answer." without any additional information.
"""