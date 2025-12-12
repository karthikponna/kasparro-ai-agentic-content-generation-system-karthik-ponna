from typing import Dict, Any, List
from loguru import logger
from exceptions import ValidationError, LLMError, ContentGenerationError
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI

from models import FAQPage, QAPair, WorkflowState
from utils.prompt_loader import load_prompt
from utils.llm_factory import create_structured_llm, invoke_with_retry


class FAQContent(BaseModel):
    """FAQ content structure for LLM output."""
    qa_pairs: List[QAPair] = Field(..., description="List of Q&A pairs", min_length=15)


def generate_faq_page(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate FAQ page with Q&A pairs.
    
    Args:
        state: Current workflow state with questions and content blocks
        
    Returns:
        Updated state with FAQ page
        
    Raises:
        ValidationError: If required data is missing
        LLMError: If LLM API call fails
    """
    try: 
        product_data = state.product_data
        questions = state.questions
        content_blocks = state.content_blocks

        if not product_data or not questions:
            raise ValidationError(
                "Missing required data (product_data or questions)",
                {"agent": "faq_generator"}
            )
        
        logger.info(f"Generating FAQ page for: {product_data.product_name}")
        
        question_count = len(questions)

        logger.info(f"Processing {question_count} questions for FAQ.")

        # Initialize LLM with structured output using factory
        structured_llm = create_structured_llm(FAQContent)

        # Load prompt from YAML
        prompt = load_prompt("faq_generator")

        questions_list = "\n".join([
            f"{i+1}. [{q.category.value}] {q.question}"
            for i, q in enumerate(questions)
        ])

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
                "price": product_data.price,
                "benefits_block": content_blocks["benefits"].content if content_blocks else "",
                "usage_block": content_blocks["usage"].content if content_blocks else "",
                "ingredients_block": content_blocks["ingredients"].content if content_blocks else "",
                "safety_block": content_blocks["safety"].content if content_blocks else "",
                "questions_list": questions_list,
                "question_count": question_count
            })
        except Exception as e:
            # Wrap LLM errors
            if "openai" in str(type(e).__module__).lower() or "api" in str(e).lower():
                raise LLMError(
                    f"LLM API call failed: {str(e)}",
                    {"product": product_data.product_name, "question_count": question_count}
                ) from e
            raise ContentGenerationError(f"FAQ generation failed: {str(e)}") from e

        # get unique categories
        categories = list(set([qa.category.value for qa in result.qa_pairs]))

        # create FAQ page
        faq_page = FAQPage(
            product_name=product_data.product_name,
            total_questions=len(result.qa_pairs),
            qa_pairs=result.qa_pairs,
            categories=categories
        )
        
        logger.info(f"Successfully generated FAQ page with {len(result.qa_pairs)} Q&A pairs")

        # Warn if we didn't meet the 15 FAQ minimum requirement
        if len(result.qa_pairs) < 15:
            logger.warning(f"FAQ count ({len(result.qa_pairs)}) is below minimum requirement of 15")
        

        return {"faq_page": faq_page}
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except LLMError as e:
        logger.error(f"LLM error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ContentGenerationError as e:
        logger.error(f"Content generation error: {str(e)}", exc_info=True)
        return {"error": str(e)}