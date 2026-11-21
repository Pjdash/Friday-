"""MitraSeva scheme assistant for Mitrapur Pradesh."""
import os

# Privacy: LangGraph/LangChain upload run traces (inputs included) to LangSmith when tracing is enabled.
# This service handles citizens' messages and records, so tracing is forced off. Opt in explicitly with
# MITRA_ALLOW_TRACING=1 only if the destination is approved to receive personal data.
if os.environ.get("MITRA_ALLOW_TRACING") != "1":
    for _name in ("LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING_V2", "LANGCHAIN_TRACING"):
        os.environ[_name] = "false"
