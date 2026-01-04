"""
Cohort Analysis Service for ShareYourSales
Analyze user behavior and retention over time using cohort analysis

Dependencies:
    pip install pandas numpy

Features:
    - User retention cohorts
    - Revenue cohorts
    - Engagement cohorts
    - Churn analysis
    - Lifetime value analysis
    - Cohort comparison
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("pandas not installed. Run: pip install pandas numpy")


logger = logging.getLogger(__name__)


class CohortAnalysisService:
    """
    Cohort analysis service for user behavior tracking

    Types of cohorts:
    1. Acquisition Cohorts - Users grouped by signup date
    2. Behavioral Cohorts - Users grouped by specific actions
    3. Revenue Cohorts - Users grouped by spending patterns

    Example:
        service = CohortAnalysisService()

        # Analyze retention
        retention = service.calculate_retention_cohorts(
            users=user_data,
            events=event_data,
            cohort_period="month"
        )

        # Analyze revenue
        revenue = service.calculate_revenue_cohorts(
            users=user_data,
            transactions=transaction_data
        )
    """

    def __init__(self):
        """Initialize cohort analysis service"""
        if not PANDAS_AVAILABLE:
            logger.warning("pandas not available. Install with: pip install pandas numpy")

    # ===== User Retention Cohorts =====

    def calculate_retention_cohorts(
        self,
        users: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        cohort_period: str = "month",  # "day", "week", "month"
        periods_to_analyze: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate user retention cohorts

        Args:
            users: List of users with id, created_at
            events: List of user events with user_id, timestamp, event_type
            cohort_period: Grouping period (day, week, month)
            periods_to_analyze: Number of periods to track

        Returns:
            Retention cohort data with matrix and percentages
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required")

        # Create DataFrame
        users_df = pd.DataFrame(users)
        events_df = pd.DataFrame(events)

        # Convert timestamps
        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])

        # Create cohort column based on signup date
        if cohort_period == "day":
            users_df['cohort'] = users_df['created_at'].dt.date
            events_df['event_period'] = events_df['timestamp'].dt.date
        elif cohort_period == "week":
            users_df['cohort'] = users_df['created_at'].dt.to_period('W').dt.start_time
            events_df['event_period'] = events_df['timestamp'].dt.to_period('W').dt.start_time
        else:  # month
            users_df['cohort'] = users_df['created_at'].dt.to_period('M').dt.start_time
            events_df['event_period'] = events_df['timestamp'].dt.to_period('M').dt.start_time

        # Merge users with events
        merged = events_df.merge(users_df[['id', 'cohort']], left_on='user_id', right_on='id', how='left')

        # Calculate period index (periods since cohort start)
        if cohort_period == "day":
            merged['period_index'] = (merged['event_period'] - merged['cohort']).dt.days
        elif cohort_period == "week":
            merged['period_index'] = ((merged['event_period'] - merged['cohort']).dt.days / 7).astype(int)
        else:  # month
            merged['period_index'] = ((merged['event_period'].dt.year - merged['cohort'].dt.year) * 12 +
                                      merged['event_period'].dt.month - merged['cohort'].dt.month)

        # Count unique users per cohort per period
        cohort_data = merged.groupby(['cohort', 'period_index'])['user_id'].nunique().reset_index()
        cohort_data.columns = ['cohort', 'period_index', 'users']

        # Pivot to create retention matrix
        retention_matrix = cohort_data.pivot(index='cohort', columns='period_index', values='users')

        # Calculate cohort sizes (period 0)
        cohort_sizes = retention_matrix[0]

        # Calculate retention percentages
        retention_pct = retention_matrix.divide(cohort_sizes, axis=0) * 100

        # Prepare result
        result = {
            "cohort_period": cohort_period,
            "cohorts": retention_matrix.index.strftime('%Y-%m-%d').tolist(),
            "periods": list(range(periods_to_analyze)),
            "retention_matrix": retention_matrix.fillna(0).to_dict('index'),
            "retention_percentages": retention_pct.fillna(0).to_dict('index'),
            "cohort_sizes": cohort_sizes.to_dict(),
            "average_retention": {}
        }

        # Calculate average retention per period
        for period in range(min(periods_to_analyze, len(retention_pct.columns))):
            if period in retention_pct.columns:
                result["average_retention"][f"period_{period}"] = float(retention_pct[period].mean())

        return result

    # ===== Revenue Cohorts =====

    def calculate_revenue_cohorts(
        self,
        users: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        cohort_period: str = "month",
        periods_to_analyze: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate revenue cohorts (LTV analysis)

        Args:
            users: List of users with id, created_at
            transactions: List of transactions with user_id, amount, timestamp
            cohort_period: Grouping period
            periods_to_analyze: Number of periods

        Returns:
            Revenue cohort data
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required")

        users_df = pd.DataFrame(users)
        transactions_df = pd.DataFrame(transactions)

        # Convert timestamps
        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        transactions_df['timestamp'] = pd.to_datetime(transactions_df['timestamp'])

        # Create cohorts
        if cohort_period == "month":
            users_df['cohort'] = users_df['created_at'].dt.to_period('M').dt.start_time
            transactions_df['transaction_period'] = transactions_df['timestamp'].dt.to_period('M').dt.start_time
        elif cohort_period == "week":
            users_df['cohort'] = users_df['created_at'].dt.to_period('W').dt.start_time
            transactions_df['transaction_period'] = transactions_df['timestamp'].dt.to_period('W').dt.start_time
        else:
            users_df['cohort'] = users_df['created_at'].dt.date
            transactions_df['transaction_period'] = transactions_df['timestamp'].dt.date

        # Merge
        merged = transactions_df.merge(users_df[['id', 'cohort']], left_on='user_id', right_on='id', how='left')

        # Calculate period index
        if cohort_period == "month":
            merged['period_index'] = ((merged['transaction_period'].dt.year - merged['cohort'].dt.year) * 12 +
                                      merged['transaction_period'].dt.month - merged['cohort'].dt.month)
        elif cohort_period == "week":
            merged['period_index'] = ((merged['transaction_period'] - merged['cohort']).dt.days / 7).astype(int)
        else:
            merged['period_index'] = (merged['transaction_period'] - merged['cohort']).dt.days

        # Calculate revenue per cohort per period
        revenue_data = merged.groupby(['cohort', 'period_index'])['amount'].sum().reset_index()

        # Pivot
        revenue_matrix = revenue_data.pivot(index='cohort', columns='period_index', values='amount')

        # Calculate cumulative revenue
        cumulative_revenue = revenue_matrix.cumsum(axis=1)

        # Get cohort sizes
        cohort_sizes = users_df.groupby('cohort')['id'].count()

        # Calculate average revenue per user
        arpu_matrix = revenue_matrix.divide(cohort_sizes, axis=0)
        cumulative_arpu = cumulative_revenue.divide(cohort_sizes, axis=0)

        return {
            "cohort_period": cohort_period,
            "cohorts": revenue_matrix.index.strftime('%Y-%m-%d').tolist(),
            "revenue_matrix": revenue_matrix.fillna(0).to_dict('index'),
            "cumulative_revenue": cumulative_revenue.fillna(0).to_dict('index'),
            "arpu_matrix": arpu_matrix.fillna(0).to_dict('index'),
            "cumulative_arpu": cumulative_arpu.fillna(0).to_dict('index'),
            "cohort_sizes": cohort_sizes.to_dict(),
            "total_revenue_by_cohort": revenue_matrix.sum(axis=1).to_dict()
        }

    # ===== Engagement Cohorts =====

    def calculate_engagement_cohorts(
        self,
        users: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        cohort_period: str = "month"
    ) -> Dict[str, Any]:
        """
        Calculate engagement cohorts (activity levels)

        Args:
            users: List of users
            events: List of events
            cohort_period: Grouping period

        Returns:
            Engagement cohort data
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required")

        users_df = pd.DataFrame(users)
        events_df = pd.DataFrame(events)

        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])

        # Create cohorts
        if cohort_period == "month":
            users_df['cohort'] = users_df['created_at'].dt.to_period('M').dt.start_time
            events_df['event_period'] = events_df['timestamp'].dt.to_period('M').dt.start_time
        else:
            users_df['cohort'] = users_df['created_at'].dt.to_period('W').dt.start_time
            events_df['event_period'] = events_df['timestamp'].dt.to_period('W').dt.start_time

        # Merge
        merged = events_df.merge(users_df[['id', 'cohort']], left_on='user_id', right_on='id', how='left')

        # Calculate period index
        if cohort_period == "month":
            merged['period_index'] = ((merged['event_period'].dt.year - merged['cohort'].dt.year) * 12 +
                                      merged['event_period'].dt.month - merged['cohort'].dt.month)
        else:
            merged['period_index'] = ((merged['event_period'] - merged['cohort']).dt.days / 7).astype(int)

        # Count events per user per cohort per period
        engagement_data = merged.groupby(['cohort', 'period_index', 'user_id']).size().reset_index(name='event_count')

        # Average events per user
        avg_engagement = engagement_data.groupby(['cohort', 'period_index'])['event_count'].mean().reset_index()

        # Pivot
        engagement_matrix = avg_engagement.pivot(index='cohort', columns='period_index', values='event_count')

        return {
            "cohort_period": cohort_period,
            "cohorts": engagement_matrix.index.strftime('%Y-%m-%d').tolist(),
            "engagement_matrix": engagement_matrix.fillna(0).to_dict('index'),
            "average_engagement_by_period": {
                f"period_{col}": float(engagement_matrix[col].mean())
                for col in engagement_matrix.columns
            }
        }

    # ===== Churn Analysis =====

    def calculate_churn_cohorts(
        self,
        users: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        inactivity_threshold_days: int = 30,
        cohort_period: str = "month"
    ) -> Dict[str, Any]:
        """
        Calculate churn rates by cohort

        Args:
            users: List of users
            events: List of events
            inactivity_threshold_days: Days of inactivity to consider churned
            cohort_period: Grouping period

        Returns:
            Churn cohort data
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required")

        users_df = pd.DataFrame(users)
        events_df = pd.DataFrame(events)

        users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])

        # Create cohorts
        if cohort_period == "month":
            users_df['cohort'] = users_df['created_at'].dt.to_period('M').dt.start_time
        else:
            users_df['cohort'] = users_df['created_at'].dt.to_period('W').dt.start_time

        # Get last activity per user
        last_activity = events_df.groupby('user_id')['timestamp'].max().reset_index()
        last_activity.columns = ['user_id', 'last_activity']

        # Merge with users
        users_with_activity = users_df.merge(last_activity, left_on='id', right_on='user_id', how='left')

        # Calculate days since last activity
        today = pd.Timestamp.now()
        users_with_activity['days_inactive'] = (today - users_with_activity['last_activity']).dt.days

        # Mark churned users
        users_with_activity['churned'] = users_with_activity['days_inactive'] > inactivity_threshold_days

        # Calculate churn rate by cohort
        churn_by_cohort = users_with_activity.groupby('cohort').agg({
            'id': 'count',
            'churned': 'sum'
        }).reset_index()

        churn_by_cohort['churn_rate'] = (churn_by_cohort['churned'] / churn_by_cohort['id']) * 100

        return {
            "cohort_period": cohort_period,
            "inactivity_threshold_days": inactivity_threshold_days,
            "cohorts": churn_by_cohort['cohort'].dt.strftime('%Y-%m-%d').tolist(),
            "cohort_sizes": churn_by_cohort['id'].tolist(),
            "churned_users": churn_by_cohort['churned'].tolist(),
            "churn_rates": churn_by_cohort['churn_rate'].tolist(),
            "overall_churn_rate": float((churn_by_cohort['churned'].sum() / churn_by_cohort['id'].sum()) * 100)
        }

    # ===== Lifetime Value Analysis =====

    def calculate_ltv_cohorts(
        self,
        users: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        cohort_period: str = "month",
        discount_rate: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate Customer Lifetime Value by cohort

        Args:
            users: List of users
            transactions: List of transactions
            cohort_period: Grouping period
            discount_rate: Monthly discount rate for NPV calculation

        Returns:
            LTV cohort data
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas required")

        # Calculate revenue cohorts first
        revenue_cohorts = self.calculate_revenue_cohorts(users, transactions, cohort_period)

        # Extract cumulative ARPU (this is LTV over time)
        cumulative_arpu = pd.DataFrame(revenue_cohorts['cumulative_arpu'])

        # Apply discount rate if specified
        if discount_rate > 0:
            for period in cumulative_arpu.columns:
                discount_factor = 1 / ((1 + discount_rate) ** int(period))
                cumulative_arpu[period] = cumulative_arpu[period] * discount_factor

        # Calculate projected LTV (based on latest available data)
        projected_ltv = cumulative_arpu[cumulative_arpu.columns[-1]]

        return {
            "cohort_period": cohort_period,
            "discount_rate": discount_rate,
            "cohorts": revenue_cohorts['cohorts'],
            "ltv_by_period": cumulative_arpu.to_dict('index'),
            "projected_ltv": projected_ltv.to_dict(),
            "average_ltv": float(projected_ltv.mean()),
            "median_ltv": float(projected_ltv.median())
        }

    # ===== Cohort Comparison =====

    def compare_cohorts(
        self,
        cohort_data: Dict[str, Any],
        cohorts_to_compare: List[str],
        metric: str = "retention"
    ) -> Dict[str, Any]:
        """
        Compare specific cohorts against each other

        Args:
            cohort_data: Cohort analysis data
            cohorts_to_compare: List of cohort identifiers
            metric: Metric to compare

        Returns:
            Comparison data
        """
        if metric == "retention":
            matrix_key = "retention_percentages"
        elif metric == "revenue":
            matrix_key = "arpu_matrix"
        else:
            matrix_key = "engagement_matrix"

        comparison = {}
        for cohort in cohorts_to_compare:
            if cohort in cohort_data[matrix_key]:
                comparison[cohort] = cohort_data[matrix_key][cohort]

        return {
            "metric": metric,
            "cohorts": cohorts_to_compare,
            "comparison_data": comparison
        }


# ===== Usage Example =====
if __name__ == "__main__":
    service = CohortAnalysisService()

    # Sample data
    users = [
        {"id": "u1", "created_at": "2024-01-15"},
        {"id": "u2", "created_at": "2024-01-20"},
        {"id": "u3", "created_at": "2024-02-10"},
    ]

    events = [
        {"user_id": "u1", "timestamp": "2024-01-16", "event_type": "login"},
        {"user_id": "u1", "timestamp": "2024-02-15", "event_type": "login"},
        {"user_id": "u2", "timestamp": "2024-01-25", "event_type": "login"},
    ]

    transactions = [
        {"user_id": "u1", "amount": 100, "timestamp": "2024-01-20"},
        {"user_id": "u1", "amount": 50, "timestamp": "2024-02-20"},
    ]

    # Calculate retention cohorts
    retention = service.calculate_retention_cohorts(users, events)
    print("Retention cohorts:", retention)

    # Calculate revenue cohorts
    revenue = service.calculate_revenue_cohorts(users, transactions)
    print("Revenue cohorts:", revenue)
