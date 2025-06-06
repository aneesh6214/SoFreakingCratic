# config.py
"""
Configuration settings for the Multi-Agent Debate System
"""

import os
from typing import Dict, Any

# Debate Configuration
DEBATE_CONFIG = {
    "max_rounds": 10,
    "cooldown_rounds": 2,
    "reactivity_threshold": 0.3,
    "moderator_intervention_chance": 0.3,
    "memory_limit": 15,
    "max_message_length": 500,
    "speakers_per_round": 2
}

# LLM Configuration Template
LLM_CONFIG_TEMPLATE = {
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": 0.7,
            "max_tokens": 500,
        }
    ],
    "timeout": 120,
}

# Agent Configuration
AGENT_CONFIG = {
    "enable_reflection": True,
    "enable_memory": True,
    "enable_goals": True,
    "default_goals": {
        "deontology": ["Defend universal moral principles", "Emphasize duty over consequences"],
        "consequentialism": ["Maximize overall happiness", "Focus on practical outcomes"],
        "confucian": ["Promote social harmony", "Emphasize virtue and proper relationships"],
        "existentialist": ["Defend radical freedom", "Challenge imposed moral systems"],
        "buddhist": ["Reduce suffering for all beings", "Promote compassion and non-attachment"]
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_file": "debate_logs.txt",
    "save_transcripts": True,
    "transcript_dir": "transcripts/"
}

# Memory System Configuration
MEMORY_CONFIG = {
    "memory_decay_rate": 0.05,  # How much memories decay per round
    "belief_drift_threshold": 0.7,  # Threshold for system prompt modification
    "opinion_weight_decay": 0.95,  # How opinion weights decay toward neutral
    "importance_decay_threshold": 0.2,  # Minimum importance before memory is removed
    "relevant_memory_keyword_threshold": 3,  # Minimum common words for memory relevance
    "max_memories_per_agent": 15
}

def get_llm_config(model: str = "gpt-4", temperature: float = 0.7) -> Dict[str, Any]:
    """Get LLM configuration with custom parameters."""
    config = LLM_CONFIG_TEMPLATE.copy()
    config["config_list"][0]["model"] = model
    config["config_list"][0]["temperature"] = temperature
    return config

def validate_config() -> bool:
    """Validate that required configuration is present."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set your API key to use the debate system.")
        return False
    return True 