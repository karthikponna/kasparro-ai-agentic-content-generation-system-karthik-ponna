from typing import Dict, Any, List
from loguru import logger
from exceptions import ValidationError, LLMError, ContentGenerationError
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI

from models import ContentBlock, ProductData, WorkflowState
from utils.prompt_loader import load_prompt
from utils.llm_factory import create_structured_llm, invoke_with_retry


class ContentBlockList(BaseModel):
    """List of content blocks for different sections."""
    benefits: str = Field(..., description="Benefits content block with rich, detailed descriptions")
    usage: str = Field(..., description="Usage instructions content block with clear, actionable steps")
    ingredients: str = Field(..., description="Ingredients content block with detailed explanations")
    safety: str = Field(..., description="Safety information content block with comprehensive precautions")


def create_content_blocks(state: WorkflowState) -> Dict[str, Any]:

    """
    Create all reusable content blocks for the product using AI.
    
    Args:
        state: Current workflow state with product data
        
    Returns:
        Updated state with AI-generated content blocks
        
    Raises:
        ValidationError: If product data is missing
        LLMError: If LLM API call fails
    """

    try:
        product_data = state.product_data

        if not product_data:
            raise ValidationError(
                "No product data available",
                {"agent": "content_logic"}
            )
        
        logger.info(f"Creating content blocks for product: {product_data.product_name}")
        
        # Initialize LLM with structured output using factory
        structured_llm = create_structured_llm(ContentBlockList)

        # Load prompt from YAML
        prompt = load_prompt("content_logic")

        chain = prompt | structured_llm
        try:
            result = invoke_with_retry(chain, {
                "product_name": product_data.product_name,
                "concentration": product_data.concentration,
                "skin_type": ", ".join(product_data.skin_type),
                "key_ingredients": ", ".join(product_data.key_ingredients),
                "benefits": ", ".join(product_data.benefits),
                "how_to_use": product_data.how_to_use,
                "side_effects": product_data.side_effects,
                "price": product_data.price
            })
        except Exception as e:
            # Wrap LLM errors
            if "openai" in str(type(e).__module__).lower() or "api" in str(e).lower():
                raise LLMError(
                    f"LLM API call failed: {str(e)}",
                    {"product": product_data.product_name}
                ) from e
            raise ContentGenerationError(f"Content block generation failed: {str(e)}") from e

        # sturcturing hte generated content to ContentBlock objects
        content_blocks = {
            "benefits": ContentBlock(
                block_type="benefits",
                content=result.benefits,
                metadata={"benefit_count": len(product_data.benefits)}
            ),
            "usage": ContentBlock(
                block_type="usage",
                content=result.usage,
                metadata={"skin_types": product_data.skin_type}
            ),
            "ingredients": ContentBlock(
                block_type="ingredients",
                content=result.ingredients,
                metadata={"ingredient_count": len(product_data.key_ingredients)}
            ),
            "safety": ContentBlock(
                block_type="safety",
                content=result.safety,
                metadata={"side_effects": product_data.side_effects}
            )
        }

        logger.info("Successfully created all 4 content blocks")
        return {"content_blocks": content_blocks}
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        return {"error": str(e)}