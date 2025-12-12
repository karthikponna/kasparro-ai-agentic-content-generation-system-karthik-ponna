import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.agents.parser_agent import parse_product_data
from src.models import WorkflowState, ProductData


class TestParserAgent:
    """Tests for parse_product_data function."""
    
    def test_parse_product_data_success(self, sample_workflow_state):
        """Test successful parsing of product data."""
        result = parse_product_data(sample_workflow_state)
        
        assert "product_data" in result
        assert result["product_data"].product_name == "GlowBoost Vitamin C Serum"
        assert result["product_data"].concentration == "10% Vitamin C"
        assert len(result["product_data"].skin_type) == 2
        assert "Oily" in result["product_data"].skin_type
    
    def test_parse_product_data_empty_input(self, empty_workflow_state):
        """Test parsing with empty product data returns validation error."""
        result = parse_product_data(empty_workflow_state)
        
        # Should return error for empty data
        assert "error" in result
        assert "No raw product data" in result["error"]
    
    def test_parse_product_data_partial_input(self):
        """Test parsing with partial product data."""
        state = WorkflowState(raw_product_data={
            "product_name": "Test Product",
            "price": "₹500"
        })
        result = parse_product_data(state)
        
        assert "product_data" in result
        assert result["product_data"].product_name == "Test Product"
        assert result["product_data"].price == "₹500"
        assert result["product_data"].skin_type == []  # Default empty list
    
    def test_parse_product_data_all_fields(self, sample_product_data_dict):
        """Test parsing preserves all fields correctly."""
        state = WorkflowState(raw_product_data=sample_product_data_dict)
        result = parse_product_data(state)
        
        assert "product_data" in result
        product = result["product_data"]
        
        assert product.product_name == sample_product_data_dict["product_name"]
        assert product.concentration == sample_product_data_dict["concentration"]
        assert product.skin_type == sample_product_data_dict["skin_type"]
        assert product.key_ingredients == sample_product_data_dict["key_ingredients"]
        assert product.benefits == sample_product_data_dict["benefits"]
        assert product.how_to_use == sample_product_data_dict["how_to_use"]
        assert product.side_effects == sample_product_data_dict["side_effects"]
        assert product.price == sample_product_data_dict["price"]
