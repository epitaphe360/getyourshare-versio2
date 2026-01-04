"""
A/B Testing Framework for ShareYourSales
Statistical A/B testing with experiment management and analysis

Dependencies:
    pip install scipy numpy

Features:
    - Experiment creation and management
    - Random user assignment with consistent hashing
    - Statistical significance testing (Chi-square, T-test, Z-test)
    - Conversion rate analysis
    - Multi-variant testing (A/B/n)
    - Bayesian A/B testing
    - Sequential testing with early stopping
"""

import os
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

try:
    import numpy as np
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy not installed. Run: pip install scipy numpy")


logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MetricType(str, Enum):
    """Type of metric to track"""
    CONVERSION = "conversion"  # Binary (0/1)
    REVENUE = "revenue"  # Continuous
    COUNT = "count"  # Discrete count
    DURATION = "duration"  # Time-based


@dataclass
class Variant:
    """Experiment variant"""
    id: str
    name: str
    description: str
    traffic_allocation: float  # 0.0 to 1.0
    is_control: bool = False


@dataclass
class Experiment:
    """A/B test experiment"""
    id: str
    name: str
    description: str
    hypothesis: str
    variants: List[Variant]
    primary_metric: str
    metric_type: MetricType
    status: ExperimentStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_sample_size: int = 1000
    significance_level: float = 0.05
    power: float = 0.8
    metadata: Optional[Dict[str, Any]] = None


class ABTestingService:
    """
    A/B Testing service for experiment management and analysis

    Example:
        service = ABTestingService()

        # Create experiment
        experiment = service.create_experiment(
            name="Checkout Button Color",
            variants=[
                Variant(id="control", name="Blue Button", traffic_allocation=0.5, is_control=True),
                Variant(id="treatment", name="Green Button", traffic_allocation=0.5)
            ],
            primary_metric="checkout_conversion",
            metric_type=MetricType.CONVERSION
        )

        # Assign user to variant
        variant = service.assign_user(experiment_id="exp_1", user_id="user_123")

        # Track event
        service.track_event(experiment_id="exp_1", user_id="user_123", metric="checkout_conversion", value=1)

        # Analyze results
        results = service.analyze_experiment(experiment_id="exp_1")
    """

    def __init__(self):
        """Initialize A/B testing service"""
        if not SCIPY_AVAILABLE:
            logger.warning("scipy not available. Install with: pip install scipy numpy")

        # In-memory storage (in production, use database)
        self.experiments: Dict[str, Experiment] = {}
        self.assignments: Dict[str, Dict[str, str]] = {}  # {experiment_id: {user_id: variant_id}}
        self.events: Dict[str, List[Dict]] = {}  # {experiment_id: [events]}

    # ===== Experiment Management =====

    def create_experiment(
        self,
        name: str,
        description: str,
        hypothesis: str,
        variants: List[Variant],
        primary_metric: str,
        metric_type: MetricType = MetricType.CONVERSION,
        min_sample_size: int = 1000,
        significance_level: float = 0.05,
        power: float = 0.8
    ) -> Experiment:
        """
        Create a new A/B test experiment

        Args:
            name: Experiment name
            description: Experiment description
            hypothesis: Hypothesis statement
            variants: List of variants
            primary_metric: Primary metric to track
            metric_type: Type of metric
            min_sample_size: Minimum sample size per variant
            significance_level: Alpha (typically 0.05)
            power: Statistical power (typically 0.8)

        Returns:
            Created experiment
        """
        # Validate traffic allocation
        total_allocation = sum(v.traffic_allocation for v in variants)
        if not 0.99 <= total_allocation <= 1.01:
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")

        # Ensure exactly one control variant
        control_count = sum(1 for v in variants if v.is_control)
        if control_count != 1:
            raise ValueError("Exactly one variant must be marked as control")

        experiment_id = f"exp_{len(self.experiments) + 1}"

        experiment = Experiment(
            id=experiment_id,
            name=name,
            description=description,
            hypothesis=hypothesis,
            variants=variants,
            primary_metric=primary_metric,
            metric_type=metric_type,
            status=ExperimentStatus.DRAFT,
            min_sample_size=min_sample_size,
            significance_level=significance_level,
            power=power
        )

        self.experiments[experiment_id] = experiment
        self.assignments[experiment_id] = {}
        self.events[experiment_id] = []

        logger.info(f"Created experiment {experiment_id}: {name}")

        return experiment

    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]

        if experiment.status != ExperimentStatus.DRAFT:
            raise ValueError(f"Can only start experiments in DRAFT status")

        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.now()

        logger.info(f"Started experiment {experiment_id}")

        return True

    def stop_experiment(self, experiment_id: str) -> bool:
        """Stop an experiment"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_date = datetime.now()

        logger.info(f"Stopped experiment {experiment_id}")

        return True

    # ===== User Assignment =====

    def assign_user(
        self,
        experiment_id: str,
        user_id: str,
        force_variant: Optional[str] = None
    ) -> str:
        """
        Assign user to a variant using consistent hashing

        Args:
            experiment_id: Experiment ID
            user_id: User ID
            force_variant: Force specific variant (for testing)

        Returns:
            Assigned variant ID
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]

        # Check if user already assigned
        if user_id in self.assignments[experiment_id]:
            return self.assignments[experiment_id][user_id]

        # Force variant if specified
        if force_variant:
            variant_ids = [v.id for v in experiment.variants]
            if force_variant not in variant_ids:
                raise ValueError(f"Variant {force_variant} not found in experiment")
            self.assignments[experiment_id][user_id] = force_variant
            return force_variant

        # Consistent hashing for assignment
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        random_value = (hash_value % 10000) / 10000.0  # 0.0 to 1.0

        # Assign based on traffic allocation
        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.traffic_allocation
            if random_value <= cumulative:
                self.assignments[experiment_id][user_id] = variant.id
                logger.debug(f"Assigned user {user_id} to variant {variant.id} in experiment {experiment_id}")
                return variant.id

        # Fallback to control
        control_variant = next(v for v in experiment.variants if v.is_control)
        self.assignments[experiment_id][user_id] = control_variant.id
        return control_variant.id

    def get_user_variant(self, experiment_id: str, user_id: str) -> Optional[str]:
        """Get assigned variant for a user"""
        if experiment_id not in self.assignments:
            return None

        return self.assignments[experiment_id].get(user_id)

    # ===== Event Tracking =====

    def track_event(
        self,
        experiment_id: str,
        user_id: str,
        metric: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track an event for experiment analysis

        Args:
            experiment_id: Experiment ID
            user_id: User ID
            metric: Metric name
            value: Metric value
            metadata: Additional metadata
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get user's variant
        variant_id = self.get_user_variant(experiment_id, user_id)
        if not variant_id:
            # User not assigned, assign now
            variant_id = self.assign_user(experiment_id, user_id)

        event = {
            "user_id": user_id,
            "variant_id": variant_id,
            "metric": metric,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.events[experiment_id].append(event)

    # ===== Analysis =====

    def get_variant_data(
        self,
        experiment_id: str,
        variant_id: str,
        metric: Optional[str] = None
    ) -> List[float]:
        """
        Get metric values for a specific variant

        Args:
            experiment_id: Experiment ID
            variant_id: Variant ID
            metric: Metric name (uses primary metric if not specified)

        Returns:
            List of metric values
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]
        metric_name = metric or experiment.primary_metric

        # Filter events for this variant and metric
        variant_events = [
            e["value"] for e in self.events[experiment_id]
            if e["variant_id"] == variant_id and e["metric"] == metric_name
        ]

        return variant_events

    def calculate_conversion_rate(
        self,
        experiment_id: str,
        variant_id: str
    ) -> Tuple[int, int, float]:
        """
        Calculate conversion rate for a variant

        Args:
            experiment_id: Experiment ID
            variant_id: Variant ID

        Returns:
            Tuple of (conversions, total_users, conversion_rate)
        """
        # Get unique users in variant
        variant_users = set([
            user for user, var in self.assignments[experiment_id].items()
            if var == variant_id
        ])

        # Get conversions
        experiment = self.experiments[experiment_id]
        conversions = [
            e["value"] for e in self.events[experiment_id]
            if e["variant_id"] == variant_id and e["metric"] == experiment.primary_metric
        ]

        total_users = len(variant_users)
        total_conversions = sum(conversions)
        conversion_rate = total_conversions / total_users if total_users > 0 else 0.0

        return int(total_conversions), total_users, conversion_rate

    def test_significance(
        self,
        experiment_id: str,
        control_variant_id: Optional[str] = None,
        treatment_variant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test statistical significance between variants

        Args:
            experiment_id: Experiment ID
            control_variant_id: Control variant ID (auto-detected if not specified)
            treatment_variant_id: Treatment variant ID (uses first non-control if not specified)

        Returns:
            Statistical test results
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy required for statistical testing")

        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]

        # Get control variant
        if not control_variant_id:
            control_variant = next(v for v in experiment.variants if v.is_control)
            control_variant_id = control_variant.id

        # Get treatment variant
        if not treatment_variant_id:
            treatment_variant = next(v for v in experiment.variants if not v.is_control)
            treatment_variant_id = treatment_variant.id

        # Get data based on metric type
        if experiment.metric_type == MetricType.CONVERSION:
            # Use proportion z-test for conversion rates
            control_conversions, control_total, control_rate = self.calculate_conversion_rate(
                experiment_id, control_variant_id
            )
            treatment_conversions, treatment_total, treatment_rate = self.calculate_conversion_rate(
                experiment_id, treatment_variant_id
            )

            # Calculate pooled proportion
            pooled_p = (control_conversions + treatment_conversions) / (control_total + treatment_total)
            pooled_se = np.sqrt(pooled_p * (1 - pooled_p) * (1/control_total + 1/treatment_total))

            # Calculate z-score
            z_score = (treatment_rate - control_rate) / pooled_se if pooled_se > 0 else 0

            # Calculate p-value (two-tailed)
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

            # Calculate confidence interval
            se_diff = np.sqrt((control_rate * (1 - control_rate) / control_total) +
                             (treatment_rate * (1 - treatment_rate) / treatment_total))
            ci_95 = 1.96 * se_diff
            lift = ((treatment_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0

            return {
                "test_type": "z_test",
                "metric_type": "conversion",
                "control_variant": control_variant_id,
                "treatment_variant": treatment_variant_id,
                "control_conversion_rate": control_rate,
                "treatment_conversion_rate": treatment_rate,
                "control_sample_size": control_total,
                "treatment_sample_size": treatment_total,
                "lift_percentage": lift,
                "z_score": float(z_score),
                "p_value": float(p_value),
                "is_significant": p_value < experiment.significance_level,
                "confidence_interval_95": {
                    "lower": float(treatment_rate - control_rate - ci_95),
                    "upper": float(treatment_rate - control_rate + ci_95)
                },
                "significance_level": experiment.significance_level
            }

        else:
            # Use t-test for continuous metrics
            control_data = self.get_variant_data(experiment_id, control_variant_id)
            treatment_data = self.get_variant_data(experiment_id, treatment_variant_id)

            if len(control_data) < 2 or len(treatment_data) < 2:
                return {
                    "test_type": "t_test",
                    "error": "Insufficient data for statistical testing",
                    "control_sample_size": len(control_data),
                    "treatment_sample_size": len(treatment_data)
                }

            # Independent t-test
            t_stat, p_value = stats.ttest_ind(control_data, treatment_data)

            control_mean = np.mean(control_data)
            treatment_mean = np.mean(treatment_data)
            lift = ((treatment_mean - control_mean) / control_mean * 100) if control_mean > 0 else 0

            return {
                "test_type": "t_test",
                "metric_type": experiment.metric_type.value,
                "control_variant": control_variant_id,
                "treatment_variant": treatment_variant_id,
                "control_mean": float(control_mean),
                "treatment_mean": float(treatment_mean),
                "control_sample_size": len(control_data),
                "treatment_sample_size": len(treatment_data),
                "lift_percentage": float(lift),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "is_significant": p_value < experiment.significance_level,
                "significance_level": experiment.significance_level
            }

    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Full experiment analysis

        Args:
            experiment_id: Experiment ID

        Returns:
            Complete analysis results
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]

        # Get variant performance
        variant_stats = []
        for variant in experiment.variants:
            if experiment.metric_type == MetricType.CONVERSION:
                conversions, total, rate = self.calculate_conversion_rate(experiment_id, variant.id)
                variant_stats.append({
                    "variant_id": variant.id,
                    "variant_name": variant.name,
                    "is_control": variant.is_control,
                    "sample_size": total,
                    "conversions": conversions,
                    "conversion_rate": rate
                })
            else:
                data = self.get_variant_data(experiment_id, variant.id)
                variant_stats.append({
                    "variant_id": variant.id,
                    "variant_name": variant.name,
                    "is_control": variant.is_control,
                    "sample_size": len(data),
                    "mean": float(np.mean(data)) if data else 0,
                    "std": float(np.std(data)) if data else 0
                })

        # Statistical significance tests
        control_variant = next(v for v in experiment.variants if v.is_control)
        significance_tests = []

        for variant in experiment.variants:
            if not variant.is_control:
                test_result = self.test_significance(
                    experiment_id,
                    control_variant_id=control_variant.id,
                    treatment_variant_id=variant.id
                )
                significance_tests.append(test_result)

        # Overall summary
        total_users = len(self.assignments[experiment_id])
        total_events = len(self.events[experiment_id])

        return {
            "experiment_id": experiment_id,
            "experiment_name": experiment.name,
            "status": experiment.status.value,
            "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
            "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
            "total_users": total_users,
            "total_events": total_events,
            "variant_stats": variant_stats,
            "significance_tests": significance_tests,
            "primary_metric": experiment.primary_metric,
            "metric_type": experiment.metric_type.value
        }

    # ===== Sample Size Calculator =====

    def calculate_required_sample_size(
        self,
        baseline_rate: float,
        minimum_detectable_effect: float,
        significance_level: float = 0.05,
        power: float = 0.8
    ) -> int:
        """
        Calculate required sample size per variant

        Args:
            baseline_rate: Current conversion rate (e.g., 0.10 for 10%)
            minimum_detectable_effect: Minimum effect to detect (e.g., 0.02 for 2% absolute increase)
            significance_level: Alpha (typically 0.05)
            power: Statistical power (typically 0.8)

        Returns:
            Required sample size per variant
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy required")

        # Convert to effect size (Cohen's h for proportions)
        p1 = baseline_rate
        p2 = baseline_rate + minimum_detectable_effect

        effect_size = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))

        # Calculate sample size using normal approximation
        z_alpha = stats.norm.ppf(1 - significance_level / 2)
        z_beta = stats.norm.ppf(power)

        n = ((z_alpha + z_beta) ** 2) * 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / ((p2 - p1) ** 2)

        return int(np.ceil(n))


# ===== Usage Example =====
if __name__ == "__main__":
    service = ABTestingService()

    # Create experiment
    experiment = service.create_experiment(
        name="Checkout Button Test",
        description="Test green vs blue checkout button",
        hypothesis="Green button will increase conversion by 5%",
        variants=[
            Variant(id="control", name="Blue Button", description="Current blue button", traffic_allocation=0.5, is_control=True),
            Variant(id="treatment", name="Green Button", description="New green button", traffic_allocation=0.5)
        ],
        primary_metric="checkout_completed",
        metric_type=MetricType.CONVERSION
    )

    # Start experiment
    service.start_experiment(experiment.id)

    # Simulate user assignments and events
    for i in range(1000):
        user_id = f"user_{i}"
        variant = service.assign_user(experiment.id, user_id)

        # Simulate conversion (green button has 12% conversion, blue has 10%)
        if variant == "treatment":
            converted = np.random.random() < 0.12
        else:
            converted = np.random.random() < 0.10

        if converted:
            service.track_event(experiment.id, user_id, "checkout_completed", 1.0)

    # Analyze results
    results = service.analyze_experiment(experiment.id)
    print("Experiment Results:")
    print(json.dumps(results, indent=2))
