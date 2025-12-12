import os
import yaml
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger


def load_prompt(agent_name: str, prompt_key: str = None) -> ChatPromptTemplate:
    """
    Load prompt template from YAML file.
    
    Args:
        agent_name: Name of the agent (matches YAML filename)
        prompt_key: Optional key for multi-prompt files (e.g., 'fictional_product')
        
    Returns:
        ChatPromptTemplate configured from YAML
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
        KeyError: If prompt_key not found in YAML
    """
    # Get the prompts directory path
    current_dir = Path(__file__).parent.parent
    prompts_dir = current_dir / "prompts"
    prompt_file = prompts_dir / f"{agent_name}.yaml"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    # Load YAML file
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts_data = yaml.safe_load(f)
    
    # Handle nested prompts (e.g., comparison_generator has multiple)
    if prompt_key:
        if prompt_key not in prompts_data:
            raise KeyError(f"Prompt key '{prompt_key}' not found in {prompt_file}")
        prompts_data = prompts_data[prompt_key]
    
    # Validate required keys
    if 'system_prompt' not in prompts_data or 'user_prompt' not in prompts_data:
        raise KeyError(f"YAML must contain 'system_prompt' and 'user_prompt' keys")
    
    # Create ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompts_data["system_prompt"]),
        ("user", prompts_data["user_prompt"])
    ])
    
    logger.debug(f"Loaded prompt template: {agent_name}" + (f".{prompt_key}" if prompt_key else ""))
    return prompt
