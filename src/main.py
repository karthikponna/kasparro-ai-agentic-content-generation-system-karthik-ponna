import os
import json
import sys
from pathlib import Path
from typing import Union
from pydantic import BaseModel

from loguru import logger
from config import settings

from workflow import run_workflow


def load_product_data(file_path: str = None) -> dict:
    """
    Load product data from JSON file.
    
    Args:
        file_path: Path to product data JSON file. Defaults to config setting.
        
    Returns:
        Product data dictionary.
        
    Raises:
        FileNotFoundError: If the product data file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path = Path(file_path or settings.PRODUCT_DATA_PATH)
    
    if not path.exists():
        raise FileNotFoundError(f"Product data file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded product data from: {path}")
    return data


def save_json_output(data: Union[BaseModel, dict], filename: str, output_dir: str = None) -> None:
    """
    Save data as JSON file.
    
    Args:
        data: Data to save (Pydantic model or dict)
        filename: Output filename
        output_dir: Output directory path. Defaults to config setting.
    """
    try:
        output_path = Path(output_dir or settings.OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert Pydantic model to dict if needed
        if isinstance(data, BaseModel):
            data_dict = data.model_dump()
        else:
            data_dict = data
        
        # Write JSON file
        filepath = output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated: {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving {filename}: {str(e)}")


def main() -> None:

    try:

        product_data = load_product_data()
        logger.info(f"Loaded: {product_data.get('product_name', 'Unknown Product')}")

        final_state = run_workflow(product_data)

        if final_state.error:
            logger.error(f"Workflow Error: {final_state.error}")

        # Save outputs
        if final_state.faq_page:
            save_json_output(final_state.faq_page, "faq.json")
        else:
            logger.warning("FAQ page not generated")
        
        if final_state.product_page:
            save_json_output(final_state.product_page, "product_page.json")
        else:
            logger.warning("Product page not generated")
        
        if final_state.comparison_page:
            save_json_output(final_state.comparison_page, "comparison_page.json")
        else:
            logger.warning("Comparison page not generated")

    except Exception as e:
        logger.critical(f"Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()