import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import routers (will need to mock supabase before importing if it's used at module level)
# But usually it's used inside functions.
# Let's mock supabase_client module
sys.modules['supabase_client'] = MagicMock()
from supabase_client import supabase, get_supabase_client

from referral_endpoints import generate_referral_code, validate_referral_code
from ai_features_endpoints import generate_product_recommendations, generate_content_template, ContentGenerationRequest
from roi_endpoints import calculate_roi, ROICalculationRequest

class TestWowFeatures(unittest.IsolatedAsyncioTestCase):
    
    async def test_roi_calculator(self):
        print("\nTesting ROI Calculator...")
        request = ROICalculationRequest(
            budget=1000,
            industry="fashion",
            campaign_type="influencer",
            average_order_value=75.0
        )
        response = await calculate_roi(request)
        print(f"ROI Response: {response}")
        self.assertGreater(response['roi_percentage'], 0)
        self.assertGreater(response['estimated_revenue'], 1000)

    async def test_referral_generation(self):
        print("\nTesting Referral Code Generation...")
        # Mock supabase response
        mock_client = MagicMock()
        # Mock existing code check (empty)
        mock_client.table().select().eq().execute.return_value.data = []
        # Mock RPC call
        mock_client.rpc().execute.return_value.data = "TESTCODE123"
        # Mock insert
        mock_client.table().insert().execute.return_value.data = [{"code": "TESTCODE123"}]
        
        with patch('referral_endpoints.get_supabase_client', return_value=mock_client):
            response = await generate_referral_code("user_123")
            print(f"Referral Code: {response}")
            self.assertEqual(response['code'], "TESTCODE123")

    async def test_ai_content_generation(self):
        print("\nTesting AI Content Generation...")
        # Mock supabase
        mock_client = MagicMock()
        # Mock product fetch
        mock_client.table().select().eq().execute.return_value.data = [{
            "name": "Super Product",
            "description": "Amazing product",
            "price": 100,
            "category": "Tech"
        }]
        # Mock insert template
        mock_client.table().insert().execute.return_value.data = [{"id": "template_123"}]
        
        request = ContentGenerationRequest(
            product_id="prod_123",
            platform="instagram",
            content_type="post",
            language="fr",
            tone="fun"
        )
        
        with patch('ai_features_endpoints.get_supabase_client', return_value=mock_client):
            # Patch internal generation to avoid OpenAI call
            with patch('ai_features_endpoints._generate_content_with_ai') as mock_gen:
                mock_gen.return_value = {
                    "title": "Test Title",
                    "content": "Test Content",
                    "hashtags": ["#test"],
                    "cta": "Buy now",
                    "best_time": "10:00",
                    "best_day": "Monday"
                }
                
                response = await generate_content_template(request, "influencer_123")
                print(f"AI Content: {response}")
                self.assertEqual(response['template_id'], "template_123")

if __name__ == '__main__':
    unittest.main()
