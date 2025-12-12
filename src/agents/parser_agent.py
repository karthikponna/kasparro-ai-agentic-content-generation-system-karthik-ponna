from typing import Dict, Any
from loguru import logger
from pydantic import ValidationError as PydanticValidationError
from exceptions import ValidationError, ParsingError

from models import ProductData, WorkflowState


def parse_product_data(state: WorkflowState) -> Dict[str, Any]:
    """
    Parse raw product data into structured ProductData model.
    
    Args:
        state: Current workflow state containing raw product data
        
    Returns:
        Updated state with parsed product data
        
    Raises:
        ValidationError: If Pydantic validation fails
        ParsingError: If data parsing fails
    """

    try:
        raw_data = state.raw_product_data

        if not raw_data:
            raise ValidationError(
                "No raw product data provided",
                {"agent": "parser_agent"}
            )

        try:
            product_data = ProductData(
                product_name=raw_data.get("product_name", ""),
                concentration=raw_data.get("concentration", ""),
                skin_type=raw_data.get("skin_type", []),
                key_ingredients=raw_data.get("key_ingredients", []),
                benefits=raw_data.get("benefits", []),
                how_to_use=raw_data.get("how_to_use", ""),
                side_effects=raw_data.get("side_effects", ""),
                price=raw_data.get("price", "")
            )
        except PydanticValidationError as e:
            raise ValidationError(
                f"Pydantic validation failed: {str(e)}",
                {"agent": "parser_agent", "fields": str(e.errors())}
            ) from e
        except (KeyError, TypeError) as e:
            raise ParsingError(
                f"Data parsing failed: {str(e)}",
                {"agent": "parser_agent"}
            ) from e
        
        logger.info(f"Successfully parsed product data: {product_data.product_name}")
        return {"product_data": product_data}
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e)}
        
    except ParsingError as e:
        logger.error(f"Parsing error: {str(e)}", exc_info=True)
        return {"error": str(e)}

