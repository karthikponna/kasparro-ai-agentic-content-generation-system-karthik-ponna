import os
import json
import sys
from typing import Dict, Any

from loguru import logger
from config import settings

from workflow import run_workflow


def load_product_data() -> Dict[str, Any]:
    """
    Load the product data (GlowBoost Vitamin C Serum).
    
    Returns:
        Product data dictionary
    """
    return {
        "product_name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": ["Oily", "Combination"],
        "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
        "benefits": ["Brightening", "Fades dark spots"],
        "how_to_use": "Apply 2-3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }


def save_json_output(data: Any, filename: str, output_dir: str = "output") -> None:
    """
    Save data as JSON file.
    
    Args:
        data: Data to save (Pydantic model or dict)
        filename: Output filename
        output_dir: Output directory path
    """
    try:
        # create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # convert Pydantic model to dict if needed
        if hasattr(data, "model_dump"):
            data_dict = data.model_dump()
        else:
            data_dict = data
        
        # write JSON file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated: {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving {filename}: {str(e)}")


def main() -> None:
    
    try:

        product_data = load_product_data()
        logger.info(f"Loaded: {product_data['product_name']}")

        final_state = run_workflow(product_data)

        if final_state.error:
            logger.error(f"Workflow Error: {final_state.error}")

        # Save outputs
        if final_state.faq_page:
            save_json_output(final_state.faq_page, "faq.json")
        else:
            print("FAQ page not generated")
        
        if final_state.product_page:
            save_json_output(final_state.product_page, "product_page.json")
        else:
            print("Product page not generated")
        
        if final_state.comparison_page:
            save_json_output(final_state.comparison_page, "comparison_page.json")
        else:
            print("Comparison page not generated")

    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()