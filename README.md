# singapore-hackathon-2024

## After cloning repo

```bash
poetry install
```

## Server setup from blank

```bash
# Basic
poetry init
poetry add pydantic devtools
poetry add mypy black pytest --group dev
```

Add to `pyproject.toml`

```bash
[tool.mypy]
# Many Google's libraries do not have stub packages.
ignore_missing_imports = true
```

```bash
# Application
poetry add beautifulsoup4 googlesearch-python networkx sympy
# Gemini
poetry add google-generativeai
# Google auth
poetry add google-api-python-client google-auth-httplib2 google-auth-oauthlib
# Rag
poetry add google.ai.generativelanguage google-labs-html-chunker
# Streamlit
poetry add streamlit
```
