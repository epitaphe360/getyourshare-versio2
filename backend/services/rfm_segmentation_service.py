"""
RFM Segmentation Service for ShareYourSales
Customer segmentation using Recency, Frequency, and Monetary analysis

Dependencies:
    pip install pandas numpy

RFM Metrics:
    - Recency: How recently did the customer make a purchase?
    - Frequency: How often do they purchase?
    - Monetary: How much do they spend?

Customer Segments:
    - Champions: Bought recently, buy often, spend the most
    - Loyal Customers: Buy regularly
    - Potential Loyalists: Recent customers with average frequency
    - Recent Customers: Bought recently but not often
    - Promising: Recent shoppers but haven't spent much
    - Need Attention: Above average recency, frequency & monetary, may not buy recently
    - About to Sleep: Below average recency, frequency & monetary
    - At Risk: Bought often & spent big, but long time ago
    - Can't Lose Them: Made big purchases & used to visit often, but long time ago
    - Hibernating: Last purchase was long ago, low spenders & low frequency
    - Lost: Lowest recency, frequency & monetary scores
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("pandas not installed. Run: pip install pandas numpy")


logger = logging.getLogger(__name__)


class RFMSegmentationService:
    """
    RFM (Recency, Frequency, Monetary) customer segmentation

    Example:
        service = RFMSegmentationService()

        # Calculate RFM scores
        rfm_data = service.calculate_rfm(transactions)

        # Get segments
        segments = service.segment_customers(rfm_data)

        # Get customer segment
        segment = service.get_customer_segment(user_id="u123")
    """

    # Segment definitions based on RFM scores
    SEGMENT_MAP = {
        (5, 5, 5): "Champions",
        (5, 4, 5): "Champions",
        (4, 5, 5): "Champions",
        (5, 5, 4): "Champions",

        (5, 3, 5): "Loyal Customers",
        (4, 4, 5): "Loyal Customers",
        (5, 4, 4): "Loyal Customers",
        (5, 3, 4): "Loyal Customers",
        (4, 5, 4): "Loyal Customers",

        (5, 3, 3): "Potential Loyalists",
        (5, 2, 3): "Potential Loyalists",
        (4, 3, 3): "Potential Loyalists",
        (4, 4, 3): "Potential Loyalists",
        (5, 3, 2): "Potential Loyalists",

        (5, 1, 5): "Recent Customers",
        (5, 1, 4): "Recent Customers",
        (5, 1, 3): "Recent Customers",
        (5, 2, 5): "Recent Customers",
        (5, 2, 4): "Recent Customers",
        (4, 1, 5): "Recent Customers",

        (5, 1, 2): "Promising",
        (5, 1, 1): "Promising",
        (4, 1, 2): "Promising",
        (4, 1, 1): "Promising",
        (5, 2, 2): "Promising",
        (5, 2, 1): "Promising",

        (3, 3, 5): "Need Attention",
        (3, 4, 5): "Need Attention",
        (3, 5, 5): "Need Attention",
        (3, 4, 4): "Need Attention",
        (4, 4, 4): "Need Attention",

        (3, 3, 3): "About to Sleep",
        (3, 2, 3): "About to Sleep",
        (3, 3, 2): "About to Sleep",
        (3, 2, 2): "About to Sleep",
        (4, 2, 3): "About to Sleep",

        (2, 5, 5): "At Risk",
        (2, 4, 5): "At Risk",
        (2, 5, 4): "At Risk",
        (2, 4, 4): "At Risk",
        (1, 5, 5): "At Risk",

        (1, 4, 5): "Can't Lose Them",
        (1, 5, 4): "Can't Lose Them",
        (2, 5, 3): "Can't Lose Them",
        (1, 4, 4): "Can't Lose Them",

        (2, 2, 2): "Hibernating",
        (2, 1, 2): "Hibernating",
        (2, 2, 1): "Hibernating",
        (2, 1, 1): "Hibernating",
        (3, 1, 2): "Hibernating",
        (3, 1, 1): "Hibernating",

        (1, 1, 1): "Lost",
        (1, 2, 1): "Lost",
        (1, 1, 2): "Lost",
        (1, 2, 2): "Lost",
        (1, 3, 1): "Lost",
        (1, 3, 2): "Lost",
    }

    def __init__(self):
        """Initialize RFM segmentation service"""
        if not PANDAS_AVAILABLE:
            logger.warning("pandas not available. Install with: pip install pandas numpy")

        self.rfm_data = None
        self.segments = None

    # ===== RFM Calculation =====

    def calculate_rfm(
        self,
        transactions: List[Dict[str, Any]],
        customer_id_field: str = "user_id",
        date_field: str = "timestamp",
        amount_field: str = "amount",
        analysis_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Calculate RFM scores for customers

        Args:
            transactions: List of transaction records
            customer_id_field: Field name for customer ID
            date_field: Field name for transaction date
            amount_field: Field name for transaction amount
            analysis_date: Reference date for recency calculation (default: today)

        Returns:
            DataFrame with RFM scores
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required")

        # Create DataFrame
        df = pd.DataFrame(transactions)

        # Convert date field to datetime
        df[date_field] = pd.to_datetime(df[date_field])

        # Set analysis date
        if analysis_date is None:
            analysis_date = datetime.now()
        else:
            analysis_date = pd.to_datetime(analysis_date)

        # Calculate RFM metrics
        rfm = df.groupby(customer_id_field).agg({
            date_field: lambda x: (analysis_date - x.max()).days,  # Recency
            'id': 'count' if 'id' in df.columns else lambda x: len(x),  # Frequency
            amount_field: 'sum'  # Monetary
        }).reset_index()

        rfm.columns = [customer_id_field, 'Recency', 'Frequency', 'Monetary']

        # Calculate RFM scores (1-5 scale using quintiles)
        # Note: For Recency, lower is better (more recent)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')

        # Convert to int
        rfm['R_Score'] = rfm['R_Score'].astype(int)
        rfm['F_Score'] = rfm['F_Score'].astype(int)
        rfm['M_Score'] = rfm['M_Score'].astype(int)

        # Calculate RFM score (concatenated)
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

        # Calculate overall score (average)
        rfm['RFM_Total'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

        self.rfm_data = rfm

        return rfm

    # ===== Customer Segmentation =====

    def segment_customers(
        self,
        rfm_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Assign customer segments based on RFM scores

        Args:
            rfm_data: RFM DataFrame (uses self.rfm_data if not provided)

        Returns:
            DataFrame with segment assignments
        """
        if rfm_data is None:
            if self.rfm_data is None:
                raise ValueError("No RFM data available. Run calculate_rfm first.")
            rfm_data = self.rfm_data

        # Create copy
        segmented = rfm_data.copy()

        # Assign segments
        segmented['Segment'] = segmented.apply(
            lambda row: self._get_segment(row['R_Score'], row['F_Score'], row['M_Score']),
            axis=1
        )

        self.segments = segmented

        return segmented

    def _get_segment(self, r: int, f: int, m: int) -> str:
        """
        Get segment name from RFM scores

        Args:
            r: Recency score
            f: Frequency score
            m: Monetary score

        Returns:
            Segment name
        """
        # Try exact match
        if (r, f, m) in self.SEGMENT_MAP:
            return self.SEGMENT_MAP[(r, f, m)]

        # Fallback logic based on score ranges
        rfm_total = r + f + m

        if rfm_total >= 13:
            return "Champions"
        elif rfm_total >= 10:
            if r >= 4:
                return "Loyal Customers"
            else:
                return "Need Attention"
        elif rfm_total >= 7:
            if r >= 4:
                return "Potential Loyalists"
            elif r >= 3:
                return "About to Sleep"
            else:
                return "At Risk"
        else:
            if r >= 3:
                return "Promising"
            elif r == 2:
                return "Hibernating"
            else:
                return "Lost"

    # ===== Analysis Methods =====

    def get_segment_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for each segment

        Returns:
            Summary data by segment
        """
        if self.segments is None:
            raise ValueError("No segments available. Run segment_customers first.")

        summary = self.segments.groupby('Segment').agg({
            'user_id': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean',
            'RFM_Total': 'mean'
        }).reset_index()

        summary.columns = ['Segment', 'Customer_Count', 'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Avg_RFM_Score']

        # Calculate percentages
        total_customers = summary['Customer_Count'].sum()
        summary['Percentage'] = (summary['Customer_Count'] / total_customers * 100).round(2)

        # Calculate total revenue by segment
        summary['Total_Revenue'] = summary['Customer_Count'] * summary['Avg_Monetary']

        # Sort by customer count
        summary = summary.sort_values('Customer_Count', ascending=False)

        return summary.to_dict('records')

    def get_customer_segment(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get segment information for a specific customer

        Args:
            user_id: Customer ID

        Returns:
            Customer segment data
        """
        if self.segments is None:
            raise ValueError("No segments available. Run segment_customers first.")

        customer_data = self.segments[self.segments['user_id'] == user_id]

        if customer_data.empty:
            return None

        customer = customer_data.iloc[0]

        return {
            "user_id": user_id,
            "segment": customer['Segment'],
            "recency_days": int(customer['Recency']),
            "frequency": int(customer['Frequency']),
            "monetary_value": float(customer['Monetary']),
            "r_score": int(customer['R_Score']),
            "f_score": int(customer['F_Score']),
            "m_score": int(customer['M_Score']),
            "rfm_score": customer['RFM_Score'],
            "rfm_total": int(customer['RFM_Total'])
        }

    def get_segment_customers(self, segment_name: str) -> List[str]:
        """
        Get list of customer IDs in a specific segment

        Args:
            segment_name: Segment name

        Returns:
            List of customer IDs
        """
        if self.segments is None:
            raise ValueError("No segments available. Run segment_customers first.")

        segment_customers = self.segments[self.segments['Segment'] == segment_name]

        return segment_customers['user_id'].tolist()

    # ===== Recommendations by Segment =====

    def get_segment_actions(self, segment_name: str) -> Dict[str, Any]:
        """
        Get recommended actions for a segment

        Args:
            segment_name: Segment name

        Returns:
            Recommended marketing actions
        """
        actions = {
            "Champions": {
                "priority": "High",
                "actions": [
                    "Reward them for being top customers",
                    "Ask for reviews and testimonials",
                    "Introduce them to exclusive products",
                    "Make them brand ambassadors"
                ],
                "marketing_focus": "Retention & Advocacy",
                "recommended_channels": ["Email", "Push", "SMS"],
                "offer_type": "Exclusive VIP offers"
            },
            "Loyal Customers": {
                "priority": "High",
                "actions": [
                    "Upsell higher value products",
                    "Encourage referrals with incentives",
                    "Engage on social media",
                    "Build long-term relationship"
                ],
                "marketing_focus": "Upselling & Cross-selling",
                "recommended_channels": ["Email", "Push"],
                "offer_type": "Premium product recommendations"
            },
            "Potential Loyalists": {
                "priority": "Medium-High",
                "actions": [
                    "Offer membership or loyalty program",
                    "Recommend related products",
                    "Send personalized offers",
                    "Engage with educational content"
                ],
                "marketing_focus": "Building loyalty",
                "recommended_channels": ["Email", "Push"],
                "offer_type": "Loyalty program enrollment"
            },
            "Recent Customers": {
                "priority": "Medium",
                "actions": [
                    "Provide onboarding support",
                    "Start building relationship",
                    "Recommend complementary products",
                    "Ask for feedback"
                ],
                "marketing_focus": "Activation & Engagement",
                "recommended_channels": ["Email", "In-app"],
                "offer_type": "Welcome discount on 2nd purchase"
            },
            "Promising": {
                "priority": "Medium",
                "actions": [
                    "Create brand awareness",
                    "Offer free shipping or discounts",
                    "Showcase popular products",
                    "Limited-time offers"
                ],
                "marketing_focus": "Conversion",
                "recommended_channels": ["Email", "Social Media"],
                "offer_type": "First-time buyer discount"
            },
            "Need Attention": {
                "priority": "Medium-High",
                "actions": [
                    "Limited time offers",
                    "Recommend new products",
                    "Re-engage with special campaigns",
                    "Ask for feedback"
                ],
                "marketing_focus": "Re-activation",
                "recommended_channels": ["Email", "SMS", "Push"],
                "offer_type": "Come back discount (10-15%)"
            },
            "About to Sleep": {
                "priority": "Medium",
                "actions": [
                    "Win-back campaigns",
                    "Special reactivation offers",
                    "Share new product launches",
                    "Survey to understand issues"
                ],
                "marketing_focus": "Win-back",
                "recommended_channels": ["Email", "Retargeting Ads"],
                "offer_type": "Significant discount (20%+)"
            },
            "At Risk": {
                "priority": "High",
                "actions": [
                    "Urgent win-back campaign",
                    "Personalized offers based on past purchases",
                    "Identify and solve issues",
                    "VIP treatment to revive"
                ],
                "marketing_focus": "Immediate retention",
                "recommended_channels": ["Email", "SMS", "Phone Call"],
                "offer_type": "Major discount or exclusive offer"
            },
            "Can't Lose Them": {
                "priority": "Critical",
                "actions": [
                    "Personal outreach (call/email)",
                    "Understand what went wrong",
                    "Major incentives to return",
                    "Exclusive win-back offers"
                ],
                "marketing_focus": "Critical win-back",
                "recommended_channels": ["Phone Call", "Email", "Direct Mail"],
                "offer_type": "VIP re-engagement package"
            },
            "Hibernating": {
                "priority": "Low-Medium",
                "actions": [
                    "Re-engagement campaigns",
                    "Recreate brand value",
                    "Low-cost offers to test interest",
                    "Survey for feedback"
                ],
                "marketing_focus": "Re-activation",
                "recommended_channels": ["Email"],
                "offer_type": "Low-cost trial offer"
            },
            "Lost": {
                "priority": "Low",
                "actions": [
                    "Final win-back attempt",
                    "Understand why they left",
                    "Minimal marketing spend",
                    "Consider removing from active lists"
                ],
                "marketing_focus": "Final attempt or sunset",
                "recommended_channels": ["Email (final)"],
                "offer_type": "Last chance offer"
            }
        }

        return actions.get(segment_name, {
            "priority": "Unknown",
            "actions": ["Analyze customer behavior", "Define custom strategy"],
            "marketing_focus": "Analysis required",
            "recommended_channels": ["Email"],
            "offer_type": "Standard offer"
        })

    # ===== Trend Analysis =====

    def analyze_segment_movement(
        self,
        previous_rfm: pd.DataFrame,
        current_rfm: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze how customers move between segments over time

        Args:
            previous_rfm: RFM data from previous period
            current_rfm: RFM data from current period

        Returns:
            Movement analysis
        """
        # Segment both datasets
        prev_segments = self.segment_customers(previous_rfm)
        curr_segments = self.segment_customers(current_rfm)

        # Merge on user_id
        movement = prev_segments[['user_id', 'Segment']].merge(
            curr_segments[['user_id', 'Segment']],
            on='user_id',
            suffixes=('_prev', '_curr'),
            how='outer'
        )

        # Identify changes
        movement['Changed'] = movement['Segment_prev'] != movement['Segment_curr']

        # Count movements
        movements = movement[movement['Changed']].groupby(['Segment_prev', 'Segment_curr']).size().reset_index(name='count')

        return {
            "total_customers_prev": len(prev_segments),
            "total_customers_curr": len(curr_segments),
            "customers_changed_segment": int(movement['Changed'].sum()),
            "change_percentage": float((movement['Changed'].sum() / len(movement)) * 100),
            "movements": movements.to_dict('records')
        }


# ===== Usage Example =====
if __name__ == "__main__":
    service = RFMSegmentationService()

    # Sample transactions
    transactions = [
        {"user_id": "u1", "id": "t1", "amount": 100, "timestamp": "2024-11-01"},
        {"user_id": "u1", "id": "t2", "amount": 150, "timestamp": "2024-11-15"},
        {"user_id": "u2", "id": "t3", "amount": 50, "timestamp": "2024-09-10"},
        {"user_id": "u3", "id": "t4", "amount": 500, "timestamp": "2024-12-01"},
    ]

    # Calculate RFM
    rfm = service.calculate_rfm(transactions)
    print("RFM Data:")
    print(rfm)

    # Segment customers
    segments = service.segment_customers()
    print("\nSegmented Customers:")
    print(segments)

    # Get summary
    summary = service.get_segment_summary()
    print("\nSegment Summary:")
    for seg in summary:
        print(seg)

    # Get segment actions
    actions = service.get_segment_actions("Champions")
    print("\nActions for Champions:")
    print(actions)
