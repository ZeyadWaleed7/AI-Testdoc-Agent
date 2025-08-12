"""
AI Pair Programming Agent for Automated Test Writing and Documentation

This package provides an AI agent that can:
- Monitor code diffs and detect changed functions
- Generate unit tests based on code changes
- Generate documentation for functions
- Learn from past patterns using a memory module
- Compare different prompting strategies
"""

from .agent import AIAgent
from .llm import PhindCodeLlamaLLM
from .generator import TestGenerator
from .documentation import DocumentationGenerator
from .memory import MemoryModule
from .prompts import PromptStrategy, PromptTemplates

__version__ = "1.0.0"
__author__ = "AI Research Team"

__all__ = [
    "AIAgent",
    "PhindCodeLlamaLLM", 
    "TestGenerator",
    "DocumentationGenerator",
    "MemoryModule",
    "PromptStrategy",
    "PromptTemplates"
] 