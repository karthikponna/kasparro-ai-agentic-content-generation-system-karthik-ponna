import os
import json
import sys
from pathlib import Path
from typing import Union, Optional
from pydantic import BaseModel, ValidationError

from loguru import logger
from config import settings

from workflow import run_workflow
from models import FAQPage, ProductPage, ComparisonPage


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


def validate_and_save_output(
    data: Optional[BaseModel], 
    model_class: type[BaseModel],
    filename: str, 
    output_dir: str = None
) -> bool:
    """
    Validate Pydantic model and save as JSON file.
    
    Args:
        data: Data to validate and save (Pydantic model instance)
        model_class: Pydantic model class for validation
        filename: Output filename
        output_dir: Output directory path. Defaults to config setting.
        
    Returns:
        True if validation and save succeeded, False otherwise
    """
    if data is None:
        logger.warning(f"No data provided for {filename}")
        return False
    
    try:
        # Validate the data against the model
        if not isinstance(data, model_class):
            logger.error(f"Data for {filename} is not an instance of {model_class.__name__}")
            return False
        
        # Additional validation by re-parsing (ensures all validators run)
        validated_data = model_class.model_validate(data.model_dump())
        
        # Create output directory
        output_path = Path(output_dir or settings.OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict
        data_dict = validated_data.model_dump()
        
        # Write JSON file
        filepath = output_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Validated and saved: {filepath}")
        return True
        
    except ValidationError as e:
        logger.error(f"Validation failed for {filename}:")
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error['loc'])
            logger.error(f"  • {field}: {error['msg']}")
        return False
        
    except Exception as e:
        logger.error(f"Error saving {filename}: {str(e)}")
        return False


def main() -> None:
    """Main execution function."""
    try:
        # Load product data
        product_data = load_product_data()
        logger.info(f"Processing: {product_data.get('product_name', 'Unknown Product')}")
        
        # Run workflow
        final_state = run_workflow(product_data)
        
        # Check for workflow errors
        if final_state.error:
            logger.error(f"Workflow Error: {final_state.error}")
            sys.exit(1)
        
        # Validation tracking
        validation_results = {}
        
        # Validate and save FAQ page
        logger.info("Validating FAQ page...")
        validation_results['faq'] = validate_and_save_output(
            final_state.faq_page,
            FAQPage,
            "faq.json"
        )
        
        # Validate and save Product page
        logger.info("Validating Product page...")
        validation_results['product'] = validate_and_save_output(
            final_state.product_page,
            ProductPage,
            "product_page.json"
        )
        
        # Validate and save Comparison page
        logger.info("Validating Comparison page...")
        validation_results['comparison'] = validate_and_save_output(
            final_state.comparison_page,
            ComparisonPage,
            "comparison_page.json"
        )
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*50)
        
        success_count = sum(validation_results.values())
        total_count = len(validation_results)
        
        for output_type, success in validation_results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            logger.info(f"{output_type.upper():15} {status}")
        
        logger.info("="*50)
        logger.info(f"Results: {success_count}/{total_count} outputs validated successfully")
        
        # Exit with error if any validation failed
        if success_count < total_count:
            logger.error("Some outputs failed validation")
            sys.exit(1)
        else:
            logger.info("✓ All outputs validated and saved successfully")
        
    except FileNotFoundError as e:
        logger.critical(f"File Error: {str(e)}")
        sys.exit(1)
        
    except json.JSONDecodeError as e:
        logger.critical(f"JSON Parse Error: {str(e)}")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()