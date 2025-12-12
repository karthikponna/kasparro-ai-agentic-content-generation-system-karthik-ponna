from typing import Dict, Any, List
from loguru import logger
from exceptions import ValidationError, LLMError, ContentGenerationError

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from models import Question, QuestionCategory, WorkflowState
from utils.prompt_loader import load_prompt
from utils.llm_factory import create_structured_llm, invoke_with_retry


class QuestionList(BaseModel):
    """List of questions with categories."""
    questions: List[Question] = Field(..., description="List of generated questions", min_length=15)


def generate_questions(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate 15+ categorized user questions about the product.
    
    Args:
        state: Current workflow state with product data
        
    Returns:
        Updated state with generated questions
        
    Raises:
        ValidationError: If product data is missing
        LLMError: If LLM API call fails
    """

    try:
        product_data = state.product_data

        if not product_data:
            raise ValidationError(
                "No product data available", 
                {"agent": "question_generator"}
            )
        
        logger.info(f"Generating questions for product: {product_data.product_name}")
        
        
        # Initialize LLM with structured output using factory
        structured_llm = create_structured_llm(QuestionList)

        # Load prompt from YAML
        prompt = load_prompt("question_generator")

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
            raise ContentGenerationError(f"Question generation failed: {str(e)}") from e

        logger.info(f"Successfully generated {len(result.questions)} questions")
        return {"questions": result.questions}
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        return {"error": str(e)}