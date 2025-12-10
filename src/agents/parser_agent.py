from typing import Dict, Any
from models import ProductData, WorkflowState


def parse_product_data(state: WorkflowState) -> Dict[str, Any]:

    try:
        raw_data = state.raw_product_data

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

        return {"product_data": product_data}
    
    except Exception as e:
        return {"error": f"Parser Agent Error: {str(e)}"}

