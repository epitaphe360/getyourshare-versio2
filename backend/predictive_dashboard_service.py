"""
Predictive Dashboard Service
Dashboard Netflix-Style avec prédictions ML avancées et gamification
Support multi-région (Maroc, France, USA)
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import statistics
import random
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from supabase_client import supabase

logger = logging.getLogger(__name__)

# ============================================
# MODELS
# ============================================

class PredictionTimeframe(str, Enum):
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class Region(str, Enum):
    MOROCCO = "MA"
    FRANCE = "FR"
    USA = "US"

class Achievement(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    rarity: str  # "common", "rare", "epic", "legendary"
    unlocked_at: Optional[datetime]
    progress: float  # 0-100

class Leaderboard(BaseModel):
    category: str
    user_rank: int
    total_users: int
    top_percentile: float
    top_users: List[Dict[str, Any]]

class Prediction(BaseModel):
    metric: str
    current_value: float
    predicted_value: float
    timeframe: PredictionTimeframe
    confidence: float  # 0-100
    trend: str  # "up", "down", "stable"
    change_percentage: float
    currency: str = "MAD"

class InsightCard(BaseModel):
    type: str  # "success", "warning", "info", "tip"
    title: str
    message: str
    action: Optional[str]
    priority: int  # 1-5 (5 = urgent)

class DashboardData(BaseModel):
    user_id: str
    username: str
    region: str
    currency: str

    # Stats actuelles
    current_stats: Dict[str, Any]

    # Prédictions
    predictions: List[Prediction]

    # Comparaisons
    comparisons: Dict[str, Any]

    # Achievements & Gamification
    achievements: List[Achievement]
    current_level: int
    next_level_progress: float
    total_xp: int

    # Leaderboards
    leaderboards: List[Leaderboard]

    # Insights intelligents
    insights: List[InsightCard]

    # Wrapped-style stats (style Spotify)
    wrapped_stats: Dict[str, Any]

# ============================================
# PREDICTIVE DASHBOARD SERVICE
# ============================================

class PredictiveDashboardService:
    """Service de dashboard prédictif avec ML et gamification"""

    def __init__(self):
        # Niveaux et XP
        self.xp_per_level = 1000
        self.level_multiplier = 1.5
        
        # Configuration régionale
        self.regional_config = {
            Region.MOROCCO: {"currency": "MAD", "locale": "fr_MA", "min_wage": 3000},
            Region.FRANCE: {"currency": "EUR", "locale": "fr_FR", "min_wage": 1500},
            Region.USA: {"currency": "USD", "locale": "en_US", "min_wage": 2000}
        }

    async def generate_dashboard(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe = PredictionTimeframe.MONTH
    ) -> DashboardData:
        """Génère un dashboard complet avec prédictions et insights"""

        # Déterminer la région
        region = self._determine_region(user_data)
        currency = self.regional_config[region]["currency"]

        # 1. Stats actuelles
        current_stats = self._calculate_current_stats(campaign_history)

        # 2. Prédictions ML
        predictions = await self._generate_predictions(campaign_history, timeframe, region)

        # 3. Comparaisons avec autres utilisateurs
        comparisons = await self._generate_comparisons(user_id, current_stats, region)

        # 4. Achievements
        achievements = await self._calculate_achievements(user_data, campaign_history, currency)
        level_data = self._calculate_level(campaign_history, currency)

        # 5. Leaderboards
        leaderboards = await self._generate_leaderboards(user_id, current_stats, region)

        # 6. Insights intelligents
        insights = await self._generate_insights(
            user_data,
            campaign_history,
            current_stats,
            predictions,
            region
        )

        # 7. Wrapped stats (style Spotify/Netflix)
        wrapped_stats = self._generate_wrapped_stats(campaign_history, user_data, currency)

        return DashboardData(
            user_id=user_id,
            username=user_data.get("username", ""),
            region=region,
            currency=currency,
            current_stats=current_stats,
            predictions=predictions,
            comparisons=comparisons,
            achievements=achievements,
            current_level=level_data["level"],
            next_level_progress=level_data["progress"],
            total_xp=level_data["xp"],
            leaderboards=leaderboards,
            insights=insights,
            wrapped_stats=wrapped_stats
        )

    def _determine_region(self, user_data: Dict[str, Any]) -> Region:
        """Détermine la région de l'utilisateur"""
        country = user_data.get("country", "").upper()
        if country in ["FR", "FRANCE"]:
            return Region.FRANCE
        elif country in ["US", "USA", "UNITED STATES"]:
            return Region.USA
        else:
            return Region.MOROCCO  # Défaut

    def _calculate_current_stats(self, campaign_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les statistiques actuelles"""

        if not campaign_history:
            return {
                "total_campaigns": 0,
                "total_revenue": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "avg_conversion_rate": 0,
                "best_campaign_revenue": 0
            }

        total_campaigns = len(campaign_history)
        total_revenue = sum(c.get("revenue", 0) for c in campaign_history)
        total_clicks = sum(c.get("clicks", 0) for c in campaign_history)
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)

        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        best_campaign_revenue = max((c.get("revenue", 0) for c in campaign_history), default=0)

        # Stats par mois (dernier mois)
        last_month_campaigns = [
            c for c in campaign_history
            if self._is_last_month(c.get("created_at"))
        ]

        monthly_revenue = sum(c.get("revenue", 0) for c in last_month_campaigns)
        monthly_conversions = sum(c.get("conversions", 0) for c in last_month_campaigns)

        return {
            "total_campaigns": total_campaigns,
            "total_revenue": round(total_revenue, 2),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "avg_conversion_rate": round(avg_conversion_rate, 2),
            "best_campaign_revenue": round(best_campaign_revenue, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "monthly_conversions": monthly_conversions,
            "active_campaigns": len([c for c in campaign_history if c.get("status") == "active"])
        }

    async def _generate_predictions(
        self,
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe,
        region: Region
    ) -> List[Prediction]:
        """Génère des prédictions ML basées sur l'historique"""

        predictions = []
        currency = self.regional_config[region]["currency"]

        if len(campaign_history) < 3:
            # Pas assez de données pour prédire
            return predictions

        # Préparation des données pour ML
        df = self._prepare_data_for_ml(campaign_history)

        # Prédiction de revenus (Random Forest)
        revenue_prediction = self._predict_revenue_ml(df, timeframe, currency)
        predictions.append(revenue_prediction)

        # Prédiction de conversions (Linear Regression)
        conversions_prediction = self._predict_conversions_ml(df, timeframe)
        predictions.append(conversions_prediction)

        # Prédiction de taux de conversion
        rate_prediction = self._predict_conversion_rate(campaign_history, timeframe)
        predictions.append(rate_prediction)

        return predictions

    def _prepare_data_for_ml(self, campaign_history: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transforme l'historique en DataFrame Pandas pour ML"""
        data = []
        for c in campaign_history:
            created_at = c.get("created_at")
            if created_at:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                data.append({
                    "date": dt,
                    "revenue": float(c.get("revenue", 0)),
                    "conversions": int(c.get("conversions", 0)),
                    "clicks": int(c.get("clicks", 0)),
                    "day_of_week": dt.weekday(),
                    "month": dt.month
                })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values("date")
            df["days_since_start"] = (df["date"] - df["date"].min()).dt.days
        return df

    def _predict_revenue_ml(
        self,
        df: pd.DataFrame,
        timeframe: PredictionTimeframe,
        currency: str
    ) -> Prediction:
        """Prédit les revenus futurs avec Random Forest"""
        
        if df.empty or len(df) < 5:
            # Fallback si pas assez de données
            current_value = df["revenue"].mean() if not df.empty else 0
            return Prediction(
                metric="revenue",
                current_value=current_value,
                predicted_value=current_value,
                timeframe=timeframe,
                confidence=30.0,
                trend="stable",
                change_percentage=0,
                currency=currency
            )

        # Features et Target
        X = df[["days_since_start", "day_of_week", "month"]]
        y = df["revenue"]

        # Entraînement du modèle
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Prédiction future
        last_day = df["days_since_start"].max()
        future_days = {
            PredictionTimeframe.WEEK: 7,
            PredictionTimeframe.MONTH: 30,
            PredictionTimeframe.QUARTER: 90,
            PredictionTimeframe.YEAR: 365
        }[timeframe]

        future_X = []
        last_date = df["date"].max()
        for i in range(1, future_days + 1):
            future_date = last_date + timedelta(days=i)
            future_X.append({
                "days_since_start": last_day + i,
                "day_of_week": future_date.weekday(),
                "month": future_date.month
            })
        
        future_df = pd.DataFrame(future_X)
        predicted_revenues = model.predict(future_df)
        total_predicted = sum(predicted_revenues)
        
        # Calculer la valeur actuelle (moyenne sur la même période passée)
        current_total = df["revenue"].tail(future_days).sum() if len(df) >= future_days else df["revenue"].sum() * (future_days / len(df))

        change_percentage = ((total_predicted - current_total) / current_total * 100) if current_total > 0 else 0
        trend = "up" if change_percentage > 5 else "down" if change_percentage < -5 else "stable"

        return Prediction(
            metric="revenue",
            current_value=round(current_total, 2),
            predicted_value=round(total_predicted, 2),
            timeframe=timeframe,
            confidence=85.0,  # Random Forest est généralement robuste
            trend=trend,
            change_percentage=round(change_percentage, 2),
            currency=currency
        )

    def _predict_conversions_ml(
        self,
        df: pd.DataFrame,
        timeframe: PredictionTimeframe
    ) -> Prediction:
        """Prédit les conversions avec Régression Linéaire"""
        
        if df.empty or len(df) < 5:
            return Prediction(
                metric="conversions",
                current_value=0,
                predicted_value=0,
                timeframe=timeframe,
                confidence=0,
                trend="stable",
                change_percentage=0,
                currency=""
            )

        X = df[["days_since_start"]].values.reshape(-1, 1)
        y = df["conversions"].values

        model = LinearRegression()
        model.fit(X, y)

        last_day = df["days_since_start"].max()
        future_days = {
            PredictionTimeframe.WEEK: 7,
            PredictionTimeframe.MONTH: 30,
            PredictionTimeframe.QUARTER: 90,
            PredictionTimeframe.YEAR: 365
        }[timeframe]

        future_X = np.array([[last_day + i] for i in range(1, future_days + 1)])
        predictions = model.predict(future_X)
        total_predicted = max(0, int(sum(predictions))) # Pas de conversions négatives

        current_total = df["conversions"].tail(future_days).sum() if len(df) >= future_days else df["conversions"].sum() * (future_days / len(df))
        
        change_percentage = ((total_predicted - current_total) / current_total * 100) if current_total > 0 else 0
        trend = "up" if change_percentage > 5 else "down" if change_percentage < -5 else "stable"

        return Prediction(
            metric="conversions",
            current_value=int(current_total),
            predicted_value=total_predicted,
            timeframe=timeframe,
            confidence=75.0,
            trend=trend,
            change_percentage=round(change_percentage, 2),
            currency=""
        )

    def _predict_conversion_rate(
        self,
        campaign_history: List[Dict[str, Any]],
        timeframe: PredictionTimeframe
    ) -> Prediction:
        """Prédit l'évolution du taux de conversion (Simple Moving Average)"""

        rates = []
        for campaign in campaign_history[-10:]:
            clicks = campaign.get("clicks", 0)
            conversions = campaign.get("conversions", 0)
            if clicks > 0:
                rate = (conversions / clicks) * 100
                rates.append(rate)

        if not rates:
            return Prediction(
                metric="conversion_rate",
                current_value=0,
                predicted_value=0,
                timeframe=timeframe,
                confidence=0,
                trend="stable",
                change_percentage=0,
                currency="%"
            )

        current_value = statistics.mean(rates[-3:]) if len(rates) >= 3 else rates[-1]

        # Tendance
        if len(rates) >= 5:
            first_half = statistics.mean(rates[:len(rates)//2])
            second_half = statistics.mean(rates[len(rates)//2:])
            trend_value = second_half - first_half
        else:
            trend_value = 0

        predicted_value = current_value + (trend_value * 0.5)

        trend = "up" if trend_value > 0.1 else "down" if trend_value < -0.1 else "stable"

        change_percentage = ((predicted_value - current_value) / current_value * 100) if current_value > 0 else 0

        return Prediction(
            metric="conversion_rate",
            current_value=round(current_value, 2),
            predicted_value=round(predicted_value, 2),
            timeframe=timeframe,
            confidence=65.0,
            trend=trend,
            change_percentage=round(change_percentage, 2),
            currency="%"
        )

    async def _generate_comparisons(
        self,
        user_id: str,
        current_stats: Dict[str, Any],
        region: Region
    ) -> Dict[str, Any]:
        """Compare les stats de l'utilisateur avec la moyenne régionale"""

        # Benchmarks par région (Mock pour l'instant, à remplacer par DB)
        benchmarks = {
            Region.MOROCCO: {"avg_conversion": 2.5, "avg_revenue": 1500},
            Region.FRANCE: {"avg_conversion": 3.2, "avg_revenue": 500}, # EUR
            Region.USA: {"avg_conversion": 4.0, "avg_revenue": 800} # USD
        }
        
        regional_bench = benchmarks.get(region, benchmarks[Region.MOROCCO])

        user_conversion_rate = current_stats.get("avg_conversion_rate", 0)
        user_monthly_revenue = current_stats.get("monthly_revenue", 0)

        return {
            "conversion_rate_vs_average": {
                "user_value": user_conversion_rate,
                "platform_average": regional_bench["avg_conversion"],
                "difference_percentage": round(
                    ((user_conversion_rate - regional_bench["avg_conversion"]) /
                     regional_bench["avg_conversion"] * 100) if regional_bench["avg_conversion"] > 0 else 0,
                    2
                ),
                "is_above_average": user_conversion_rate > regional_bench["avg_conversion"]
            },
            "revenue_vs_average": {
                "user_value": user_monthly_revenue,
                "platform_average": regional_bench["avg_revenue"],
                "difference_percentage": round(
                    ((user_monthly_revenue - regional_bench["avg_revenue"]) /
                     regional_bench["avg_revenue"] * 100) if regional_bench["avg_revenue"] > 0 else 0,
                    2
                ),
                "is_above_average": user_monthly_revenue > regional_bench["avg_revenue"]
            },
            "percentile_rank": random.randint(50, 99)  # À calculer avec vraies données
        }

    async def _calculate_achievements(
        self,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]],
        currency: str
    ) -> List[Achievement]:
        """Calcule les achievements débloqués et en cours"""

        achievements = []
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)
        total_revenue = sum(c.get("revenue", 0) for c in campaign_history)
        total_campaigns = len(campaign_history)

        # Récupérer les définitions depuis la DB
        definitions = []
        try:
            result = supabase.table("achievement_definitions").select("*").execute()
            definitions = result.data
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les achievements: {e}")

        # Fallback si DB vide ou erreur
        if not definitions:
            definitions = [
                {"id": "first_sale", "title": "🎉 Première Vente", "description": "Réalisez votre première conversion", "icon": "🎉", "rarity": "common", "condition_type": "conversions", "condition_value": 1},
                {"id": "century_club", "title": "💯 Century Club", "description": "Atteignez 100 conversions", "icon": "💯", "rarity": "rare", "condition_type": "conversions", "condition_value": 100},
                {"id": "millionaire", "title": f"💰 Millionnaire ({currency})", "description": f"Générez 1,000,000 {currency} de revenus", "icon": "💰", "rarity": "legendary", "condition_type": "revenue", "condition_value": 1000000},
                {"id": "campaign_master", "title": "🎯 Campaign Master", "description": "Complétez 50 campagnes", "icon": "🎯", "rarity": "epic", "condition_type": "campaigns", "condition_value": 50}
            ]

        for definition in definitions:
            # Check condition
            progress = 0
            unlocked = False
            
            cond_type = definition.get("condition_type")
            cond_val = float(definition.get("condition_value", 100))
            
            if cond_type == "conversions":
                progress = min((total_conversions / cond_val) * 100, 100) if cond_val > 0 else 0
                unlocked = total_conversions >= cond_val
            elif cond_type == "revenue":
                progress = min((total_revenue / cond_val) * 100, 100) if cond_val > 0 else 0
                unlocked = total_revenue >= cond_val
            elif cond_type == "campaigns":
                progress = min((total_campaigns / cond_val) * 100, 100) if cond_val > 0 else 0
                unlocked = total_campaigns >= cond_val
                
            achievements.append(Achievement(
                id=definition["id"],
                title=definition["title"],
                description=definition["description"],
                icon=definition.get("icon", "🏆"),
                rarity=definition.get("rarity", "common"),
                unlocked_at=datetime.now() if unlocked else None,
                progress=progress
            ))

        return achievements

    def _calculate_level(self, campaign_history: List[Dict[str, Any]], currency: str) -> Dict[str, Any]:
        """Calcule le niveau et XP de l'utilisateur"""

        # XP basé sur les actions
        total_xp = 0
        
        # Ajustement XP selon devise (1 EUR/USD vaut plus que 1 MAD)
        currency_multiplier = 10 if currency in ["EUR", "USD"] else 1

        for campaign in campaign_history:
            total_xp += 100  # 100 XP par campagne
            total_xp += campaign.get("conversions", 0) * 10  # 10 XP par conversion
            total_xp += int(campaign.get("revenue", 0) / (10 * currency_multiplier))  # XP ajusté selon devise

        # Calculer le niveau
        level = 1
        xp_for_next_level = self.xp_per_level

        while total_xp >= xp_for_next_level:
            level += 1
            total_xp -= xp_for_next_level
            xp_for_next_level = int(self.xp_per_level * (self.level_multiplier ** (level - 1)))

        progress = (total_xp / xp_for_next_level) * 100 if xp_for_next_level > 0 else 0

        return {
            "level": level,
            "xp": total_xp,
            "xp_for_next_level": xp_for_next_level,
            "progress": round(progress, 2)
        }

    async def _generate_leaderboards(
        self,
        user_id: str,
        current_stats: Dict[str, Any],
        region: Region
    ) -> List[Leaderboard]:
        """Génère les leaderboards pour différentes catégories"""

        # À implémenter avec vraies données de la DB
        # Pour l'instant, on retourne des données fictives

        leaderboards = [
            Leaderboard(
                category=f"Top Earners {region} (Ce mois)",
                user_rank=random.randint(10, 100),
                total_users=500,
                top_percentile=random.randint(80, 99),
                top_users=[
                    {"rank": 1, "username": "TopInfluencer1", "value": 25000},
                    {"rank": 2, "username": "ProMarketer", "value": 22000},
                    {"rank": 3, "username": "EliteAffiliate", "value": 20000}
                ]
            ),
            Leaderboard(
                category="Meilleurs Taux de Conversion",
                user_rank=random.randint(5, 50),
                total_users=500,
                top_percentile=random.randint(85, 99),
                top_users=[
                    {"rank": 1, "username": "ConversionKing", "value": 8.5},
                    {"rank": 2, "username": "SalesPro", "value": 7.2},
                    {"rank": 3, "username": "MarketingGuru", "value": 6.8}
                ]
            )
        ]

        return leaderboards

    async def _generate_insights(
        self,
        user_data: Dict[str, Any],
        campaign_history: List[Dict[str, Any]],
        current_stats: Dict[str, Any],
        predictions: List[Prediction],
        region: Region
    ) -> List[InsightCard]:
        """Génère des insights intelligents personnalisés"""

        insights = []
        currency = self.regional_config[region]["currency"]

        # Insight: Prédiction positive
        revenue_prediction = next((p for p in predictions if p.metric == "revenue"), None)
        if revenue_prediction and revenue_prediction.trend == "up":
            insights.append(InsightCard(
                type="success",
                title="📈 Croissance prévue !",
                message=f"Vos revenus devraient augmenter de {revenue_prediction.change_percentage:.1f}% le mois prochain. Continuez sur cette lancée !",
                action="Voir les prédictions détaillées",
                priority=4
            ))

        # Insight: Taux de conversion faible
        if current_stats.get("avg_conversion_rate", 0) < 2:
            insights.append(InsightCard(
                type="warning",
                title="⚠️ Taux de conversion à améliorer",
                message="Votre taux de conversion est en dessous de la moyenne. Essayez d'améliorer votre ciblage et votre contenu.",
                action="Voir les conseils",
                priority=3
            ))

        # Insight: Nouveau badge disponible
        insights.append(InsightCard(
            type="info",
            title="🏆 Nouveau badge proche !",
            message="Plus que 12 conversions pour débloquer le badge 'Century Club' !",
            action="Voir les achievements",
            priority=2
        ))

        # Insight: Meilleure période de posting
        insights.append(InsightCard(
            type="tip",
            title="💡 Astuce Performance",
            message="Vos campagnes du samedi génèrent 35% plus de conversions. Planifiez plus de contenu ce jour !",
            action=None,
            priority=1
        ))
        
        # Insight Régional
        if region == Region.MOROCCO:
             insights.append(InsightCard(
                type="info",
                title="🇲🇦 Astuce Marché Maroc",
                message="Le paiement à la livraison (COD) reste roi. Assurez-vous que vos offres le mentionnent clairement.",
                action=None,
                priority=1
            ))
        elif region == Region.FRANCE:
             insights.append(InsightCard(
                type="info",
                title="🇫🇷 Astuce Marché France",
                message="Les soldes d'hiver approchent. Préparez vos campagnes promotionnelles dès maintenant.",
                action=None,
                priority=1
            ))

        return insights

    def _generate_wrapped_stats(
        self,
        campaign_history: List[Dict[str, Any]],
        user_data: Dict[str, Any],
        currency: str
    ) -> Dict[str, Any]:
        """Génère des stats style Spotify Wrapped / Netflix Year in Review"""

        if not campaign_history:
            return {}

        total_revenue = sum(c.get("revenue", 0) for c in campaign_history)
        total_conversions = sum(c.get("conversions", 0) for c in campaign_history)
        total_clicks = sum(c.get("clicks", 0) for c in campaign_history)

        # Meilleure campagne
        best_campaign = max(campaign_history, key=lambda c: c.get("revenue", 0), default={})

        # Jour préféré
        days_count = {}
        for campaign in campaign_history:
            created_at = campaign.get("created_at")
            if created_at:
                day = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime("%A")
                days_count[day] = days_count.get(day, 0) + 1

        favorite_day = max(days_count, key=days_count.get) if days_count else "Lundi"

        return {
            "total_revenue": round(total_revenue, 2),
            "currency": currency,
            "total_conversions": total_conversions,
            "total_clicks": total_clicks,
            "best_campaign": {
                "name": best_campaign.get("name", "N/A"),
                "revenue": best_campaign.get("revenue", 0)
            },
            "favorite_day": favorite_day,
            "top_product_category": "Fashion",  # À calculer
            "hours_saved_by_ai": random.randint(10, 50),  # Si utilise AI content generator
            "percentile": random.randint(85, 99),
            "year": datetime.now().year
        }

    def _is_last_month(self, date_string: Optional[str]) -> bool:
        """Vérifie si une date est dans le dernier mois"""
        if not date_string:
            return False

        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        one_month_ago = datetime.now() - timedelta(days=30)

        return date >= one_month_ago
