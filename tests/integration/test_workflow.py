import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


# Skip integration tests if no API key is set
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping integration tests"
)


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""
    
    def test_workflow_end_to_end(self, sample_product_data_dict):
        """Test complete workflow execution."""
        from src.workflow import run_workflow
        
        final_state = run_workflow(sample_product_data_dict)
        
        # Check no errors
        assert final_state.error is None, f"Workflow error: {final_state.error}"
        
        # Check all outputs are generated
        assert final_state.product_data is not None
        assert final_state.questions is not None
        assert final_state.content_blocks is not None
        assert final_state.faq_page is not None
        assert final_state.product_page is not None
        assert final_state.comparison_page is not None
    
    def test_workflow_generates_minimum_15_questions(self, sample_product_data_dict):
        """Test workflow generates at least 15 questions."""
        from src.workflow import run_workflow
        
        final_state = run_workflow(sample_product_data_dict)
        
        assert final_state.error is None
        assert len(final_state.questions) >= 15, \
            f"Expected at least 15 questions, got {len(final_state.questions)}"
    
    def test_workflow_generates_minimum_15_faqs(self, sample_product_data_dict):
        """Test workflow generates at least 15 FAQs as per requirements."""
        from src.workflow import run_workflow
        
        final_state = run_workflow(sample_product_data_dict)
        
        assert final_state.error is None
        assert final_state.faq_page.total_questions >= 15, \
            f"Expected at least 15 FAQs, got {final_state.faq_page.total_questions}"
    
    def test_workflow_product_page_has_all_sections(self, sample_product_data_dict):
        """Test product page has all required sections."""
        from src.workflow import run_workflow
        
        final_state = run_workflow(sample_product_data_dict)
        
        assert final_state.error is None
        
        section_names = [s.section_name for s in final_state.product_page.sections]
        assert "Overview" in section_names
        assert "Benefits" in section_names
        assert "Key Ingredients" in section_names
        assert "How to Use" in section_names
        assert "Safety Information" in section_names
        assert "Pricing" in section_names
    
    def test_workflow_comparison_page_has_both_products(self, sample_product_data_dict):
        """Test comparison page has both products."""
        from src.workflow import run_workflow
        
        final_state = run_workflow(sample_product_data_dict)
        
        assert final_state.error is None
        assert final_state.comparison_page.product_a is not None
        assert final_state.comparison_page.product_b is not None
        assert len(final_state.comparison_page.comparison_matrix) > 0


class TestWorkflowErrorHandling:
    """Tests for workflow error handling."""
    
    def test_workflow_with_empty_data(self):
        """Test workflow handles empty data gracefully."""
        from src.workflow import run_workflow
        
        final_state = run_workflow({})
        
        # Should complete but may have validation errors
        assert final_state is not None
