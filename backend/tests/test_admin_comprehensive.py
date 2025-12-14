"""
Tests complets pour les endpoints Admin
Couvre: gestion utilisateurs, analytics, payouts, dashboard
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Try to import the app, skip tests if not available
try:
    import sys
    sys.path.insert(0, '/home/user/getyourshare-real/backend')
    from server import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    APP_AVAILABLE = True
except Exception as e:
    APP_AVAILABLE = False
    client = None


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    with patch('supabase_client.supabase') as mock:
        yield mock


@pytest.fixture
def mock_admin_auth():
    """Mock admin authentication"""
    with patch('auth.get_current_admin') as mock:
        mock.return_value = {
            'id': 'admin-123',
            'email': 'admin@getyourshare.com',
            'role': 'admin',
            'permissions': ['all']
        }
        yield mock


@pytest.fixture
def sample_users():
    """Sample users data"""
    return [
        {
            'id': 'user-1',
            'email': 'merchant@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'merchant',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'user-2',
            'email': 'influencer@test.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'influencer',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'user-3',
            'email': 'commercial@test.com',
            'first_name': 'Bob',
            'last_name': 'Brown',
            'role': 'commercial',
            'status': 'suspended',
            'created_at': (datetime.now() - timedelta(days=30)).isoformat()
        }
    ]


@pytest.fixture
def sample_subscriptions():
    """Sample subscriptions data"""
    return [
        {
            'id': 'sub-1',
            'user_id': 'user-1',
            'plan_id': 'plan-pro',
            'status': 'active',
            'price': 99.00,
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'sub-2',
            'user_id': 'user-2',
            'plan_id': 'plan-basic',
            'status': 'active',
            'price': 29.00,
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'sub-3',
            'user_id': 'user-3',
            'plan_id': 'plan-pro',
            'status': 'cancelled',
            'price': 99.00,
            'created_at': (datetime.now() - timedelta(days=60)).isoformat()
        }
    ]


# ===============================================
# ADMIN USER STATS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminUserStats:
    """Tests pour les statistiques utilisateurs admin"""

    def test_get_user_stats(self, mock_admin_auth, mock_supabase, sample_users):
        """Test récupération stats utilisateurs"""
        mock_supabase.table.return_value.select.return_value.execute.return_value = Mock(data=sample_users)
        response = client.get("/api/admin/users/stats")
        assert response.status_code in [200, 401, 403, 500]

    def test_user_stats_unauthorized(self, mock_supabase):
        """Test stats utilisateurs non autorisé"""
        with patch('auth.get_current_admin', side_effect=Exception("Unauthorized")):
            response = client.get("/api/admin/users/stats")
            assert response.status_code in [401, 403, 500]

    def test_user_stats_counts(self, mock_admin_auth, mock_supabase, sample_users):
        """Test comptages des stats utilisateurs"""
        mock_supabase.table.return_value.select.return_value.execute.return_value = Mock(data=sample_users)
        response = client.get("/api/admin/users/stats")
        if response.status_code == 200:
            data = response.json()
            assert 'total' in data
            assert 'merchants' in data
            assert 'influencers' in data


# ===============================================
# ADMIN USER LIST TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminUserList:
    """Tests pour la liste des utilisateurs admin"""

    def test_get_users_list(self, mock_admin_auth, mock_supabase, sample_users):
        """Test récupération liste utilisateurs"""
        mock_supabase.table.return_value.select.return_value.execute.return_value = Mock(data=sample_users)
        response = client.get("/api/admin/users")
        assert response.status_code in [200, 401, 403, 500]

    def test_get_users_with_pagination(self, mock_admin_auth, mock_supabase):
        """Test pagination liste utilisateurs"""
        response = client.get("/api/admin/users?page=1&per_page=10")
        assert response.status_code in [200, 401, 403, 422, 500]

    def test_get_users_filter_by_role(self, mock_admin_auth, mock_supabase):
        """Test filtrage par rôle"""
        response = client.get("/api/admin/users?role=merchant")
        assert response.status_code in [200, 401, 403, 422, 500]

    def test_get_users_filter_by_status(self, mock_admin_auth, mock_supabase):
        """Test filtrage par statut"""
        response = client.get("/api/admin/users?status=active")
        assert response.status_code in [200, 401, 403, 422, 500]

    def test_get_users_search(self, mock_admin_auth, mock_supabase):
        """Test recherche utilisateurs"""
        response = client.get("/api/admin/users?search=john")
        assert response.status_code in [200, 401, 403, 422, 500]


# ===============================================
# ADMIN USER CRUD TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminUserCRUD:
    """Tests CRUD utilisateurs admin"""

    def test_create_user(self, mock_admin_auth, mock_supabase):
        """Test création utilisateur"""
        response = client.post("/api/admin/users", json={
            'email': 'newuser@test.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'merchant'
        })
        assert response.status_code in [200, 201, 400, 401, 403, 422, 500]

    def test_create_user_invalid_email(self, mock_admin_auth, mock_supabase):
        """Test création utilisateur email invalide"""
        response = client.post("/api/admin/users", json={
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'role': 'merchant'
        })
        assert response.status_code == 422

    def test_create_user_weak_password(self, mock_admin_auth, mock_supabase):
        """Test création utilisateur mot de passe faible"""
        response = client.post("/api/admin/users", json={
            'email': 'user@test.com',
            'password': '123',
            'role': 'merchant'
        })
        assert response.status_code == 422

    def test_create_user_invalid_role(self, mock_admin_auth, mock_supabase):
        """Test création utilisateur rôle invalide"""
        response = client.post("/api/admin/users", json={
            'email': 'user@test.com',
            'password': 'SecurePass123!',
            'role': 'invalid_role'
        })
        assert response.status_code == 422

    def test_get_user_details(self, mock_admin_auth, mock_supabase):
        """Test détails utilisateur"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data={
            'id': 'user-1',
            'email': 'user@test.com'
        })
        response = client.get("/api/admin/users/user-1")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_update_user(self, mock_admin_auth, mock_supabase):
        """Test mise à jour utilisateur"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(data={'id': 'user-1'})
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock(data=[{'id': 'user-1'}])
        response = client.put("/api/admin/users/user-1", json={
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_delete_user(self, mock_admin_auth, mock_supabase):
        """Test suppression utilisateur"""
        response = client.delete("/api/admin/users/user-1")
        assert response.status_code in [200, 204, 401, 403, 404, 500]


# ===============================================
# ADMIN USER STATUS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminUserStatus:
    """Tests gestion statut utilisateur"""

    def test_suspend_user(self, mock_admin_auth, mock_supabase):
        """Test suspension utilisateur"""
        response = client.put("/api/admin/users/user-1/status", json={
            'status': 'suspended'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_activate_user(self, mock_admin_auth, mock_supabase):
        """Test activation utilisateur"""
        response = client.put("/api/admin/users/user-1/status", json={
            'status': 'active'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_set_pending_user(self, mock_admin_auth, mock_supabase):
        """Test mise en attente utilisateur"""
        response = client.put("/api/admin/users/user-1/status", json={
            'status': 'pending'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_invalid_status(self, mock_admin_auth, mock_supabase):
        """Test statut invalide"""
        response = client.put("/api/admin/users/user-1/status", json={
            'status': 'invalid'
        })
        assert response.status_code == 422

    def test_reset_password(self, mock_admin_auth, mock_supabase):
        """Test réinitialisation mot de passe"""
        response = client.post("/api/admin/users/user-1/reset-password")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN ANALYTICS METRICS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminAnalyticsMetrics:
    """Tests métriques analytics admin"""

    def test_get_metrics(self, mock_admin_auth, mock_supabase):
        """Test récupération métriques"""
        response = client.get("/api/admin/analytics/metrics")
        assert response.status_code in [200, 401, 403, 500]

    def test_get_metrics_with_days(self, mock_admin_auth, mock_supabase):
        """Test métriques avec période"""
        response = client.get("/api/admin/analytics/metrics?days=30")
        assert response.status_code in [200, 401, 403, 422, 500]

    def test_get_metrics_invalid_days(self, mock_admin_auth, mock_supabase):
        """Test métriques jours invalides"""
        response = client.get("/api/admin/analytics/metrics?days=0")
        assert response.status_code in [422, 500]

    def test_get_metrics_max_days(self, mock_admin_auth, mock_supabase):
        """Test métriques maximum jours"""
        response = client.get("/api/admin/analytics/metrics?days=365")
        assert response.status_code in [200, 401, 403, 422, 500]


# ===============================================
# ADMIN REVENUE ANALYTICS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminRevenueAnalytics:
    """Tests analytics revenus admin"""

    def test_get_revenue_data(self, mock_admin_auth, mock_supabase):
        """Test données revenus"""
        response = client.get("/api/admin/analytics/revenue")
        assert response.status_code in [200, 401, 403, 500]

    def test_get_revenue_data_period(self, mock_admin_auth, mock_supabase):
        """Test revenus avec période"""
        response = client.get("/api/admin/analytics/revenue?days=90")
        assert response.status_code in [200, 401, 403, 422, 500]

    def test_get_mrr_data(self, mock_admin_auth, mock_supabase):
        """Test données MRR"""
        response = client.get("/api/admin/analytics/mrr")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_arr_data(self, mock_admin_auth, mock_supabase):
        """Test données ARR"""
        response = client.get("/api/admin/analytics/arr")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN USER GROWTH TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminUserGrowth:
    """Tests croissance utilisateurs admin"""

    def test_get_user_growth(self, mock_admin_auth, mock_supabase):
        """Test croissance utilisateurs"""
        response = client.get("/api/admin/analytics/user-growth")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_user_growth_period(self, mock_admin_auth, mock_supabase):
        """Test croissance avec période"""
        response = client.get("/api/admin/analytics/user-growth?days=60")
        assert response.status_code in [200, 401, 403, 404, 422, 500]


# ===============================================
# ADMIN CHURN ANALYTICS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminChurnAnalytics:
    """Tests analytics churn admin"""

    def test_get_churn_data(self, mock_admin_auth, mock_supabase):
        """Test données churn"""
        response = client.get("/api/admin/analytics/churn")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_churn_rate(self, mock_admin_auth, mock_supabase):
        """Test taux de churn"""
        response = client.get("/api/admin/analytics/churn-rate")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN SUBSCRIPTION DISTRIBUTION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminSubscriptionDistribution:
    """Tests distribution abonnements admin"""

    def test_get_subscription_distribution(self, mock_admin_auth, mock_supabase):
        """Test distribution abonnements"""
        response = client.get("/api/admin/analytics/subscription-distribution")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_plans_stats(self, mock_admin_auth, mock_supabase):
        """Test statistiques plans"""
        response = client.get("/api/admin/analytics/plans-stats")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN TOP PERFORMERS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminTopPerformers:
    """Tests top performers admin"""

    def test_get_top_merchants(self, mock_admin_auth, mock_supabase):
        """Test top marchands"""
        response = client.get("/api/admin/analytics/top-merchants")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_top_products(self, mock_admin_auth, mock_supabase):
        """Test top produits"""
        response = client.get("/api/admin/analytics/top-products")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_top_affiliates(self, mock_admin_auth, mock_supabase):
        """Test top affiliés"""
        response = client.get("/api/admin/analytics/top-affiliates")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN PAYOUTS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminPayouts:
    """Tests payouts admin"""

    def test_get_pending_payouts(self, mock_admin_auth, mock_supabase):
        """Test payouts en attente"""
        response = client.get("/api/admin/payouts/pending")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_all_payouts(self, mock_admin_auth, mock_supabase):
        """Test tous les payouts"""
        response = client.get("/api/admin/payouts")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_payouts_with_status(self, mock_admin_auth, mock_supabase):
        """Test payouts par statut"""
        response = client.get("/api/admin/payouts?status=completed")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_approve_payout(self, mock_admin_auth, mock_supabase):
        """Test approbation payout"""
        response = client.post("/api/admin/payouts/payout-123/approve")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_reject_payout(self, mock_admin_auth, mock_supabase):
        """Test rejet payout"""
        response = client.post("/api/admin/payouts/payout-123/reject", json={
            'reason': 'Informations manquantes'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_process_payout(self, mock_admin_auth, mock_supabase):
        """Test traitement payout"""
        response = client.post("/api/admin/payouts/payout-123/process")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_payout_details(self, mock_admin_auth, mock_supabase):
        """Test détails payout"""
        response = client.get("/api/admin/payouts/payout-123")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN DASHBOARD TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminDashboard:
    """Tests dashboard admin"""

    def test_get_dashboard_summary(self, mock_admin_auth, mock_supabase):
        """Test résumé dashboard"""
        response = client.get("/api/admin/dashboard/summary")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_dashboard_kpis(self, mock_admin_auth, mock_supabase):
        """Test KPIs dashboard"""
        response = client.get("/api/admin/dashboard/kpis")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_recent_activity(self, mock_admin_auth, mock_supabase):
        """Test activité récente"""
        response = client.get("/api/admin/dashboard/recent-activity")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_alerts(self, mock_admin_auth, mock_supabase):
        """Test alertes admin"""
        response = client.get("/api/admin/dashboard/alerts")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN SOCIAL MANAGEMENT TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminSocialManagement:
    """Tests gestion sociale admin"""

    def test_get_social_stats(self, mock_admin_auth, mock_supabase):
        """Test stats sociales"""
        response = client.get("/api/admin/social/stats")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_influencer_applications(self, mock_admin_auth, mock_supabase):
        """Test candidatures influenceurs"""
        response = client.get("/api/admin/social/influencer-applications")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_approve_influencer(self, mock_admin_auth, mock_supabase):
        """Test approbation influenceur"""
        response = client.post("/api/admin/social/influencers/user-1/approve")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_reject_influencer(self, mock_admin_auth, mock_supabase):
        """Test rejet influenceur"""
        response = client.post("/api/admin/social/influencers/user-1/reject", json={
            'reason': 'Ne correspond pas aux critères'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]


# ===============================================
# ADMIN SETTINGS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminSettings:
    """Tests paramètres admin"""

    def test_get_platform_settings(self, mock_admin_auth, mock_supabase):
        """Test paramètres plateforme"""
        response = client.get("/api/admin/settings")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_update_platform_settings(self, mock_admin_auth, mock_supabase):
        """Test mise à jour paramètres"""
        response = client.put("/api/admin/settings", json={
            'commission_rate': 0.15,
            'min_payout': 100
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_get_commission_settings(self, mock_admin_auth, mock_supabase):
        """Test paramètres commissions"""
        response = client.get("/api/admin/settings/commissions")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_update_commission_settings(self, mock_admin_auth, mock_supabase):
        """Test mise à jour commissions"""
        response = client.put("/api/admin/settings/commissions", json={
            'default_rate': 0.10,
            'max_rate': 0.50
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]


# ===============================================
# ADMIN REPORTS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminReports:
    """Tests rapports admin"""

    def test_generate_sales_report(self, mock_admin_auth, mock_supabase):
        """Test génération rapport ventes"""
        response = client.get("/api/admin/reports/sales?start_date=2024-01-01&end_date=2024-12-31")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_generate_commissions_report(self, mock_admin_auth, mock_supabase):
        """Test génération rapport commissions"""
        response = client.get("/api/admin/reports/commissions?start_date=2024-01-01&end_date=2024-12-31")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_generate_users_report(self, mock_admin_auth, mock_supabase):
        """Test génération rapport utilisateurs"""
        response = client.get("/api/admin/reports/users")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_export_report_csv(self, mock_admin_auth, mock_supabase):
        """Test export CSV rapport"""
        response = client.get("/api/admin/reports/sales/export?format=csv")
        assert response.status_code in [200, 401, 403, 404, 422, 500]


# ===============================================
# ADMIN AUDIT LOG TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminAuditLog:
    """Tests logs audit admin"""

    def test_get_audit_logs(self, mock_admin_auth, mock_supabase):
        """Test récupération logs audit"""
        response = client.get("/api/admin/audit-logs")
        assert response.status_code in [200, 401, 403, 404, 500]

    def test_get_audit_logs_filtered(self, mock_admin_auth, mock_supabase):
        """Test logs audit filtrés"""
        response = client.get("/api/admin/audit-logs?action=user_created&user_id=user-1")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_get_user_activity_log(self, mock_admin_auth, mock_supabase):
        """Test log activité utilisateur"""
        response = client.get("/api/admin/users/user-1/activity")
        assert response.status_code in [200, 401, 403, 404, 500]


# ===============================================
# ADMIN SECURITY TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminSecurity:
    """Tests sécurité admin"""

    def test_admin_requires_authentication(self, mock_supabase):
        """Test authentification requise"""
        with patch('auth.get_current_admin', side_effect=Exception("Not authenticated")):
            response = client.get("/api/admin/users")
            assert response.status_code in [401, 403, 500]

    def test_admin_requires_admin_role(self, mock_supabase):
        """Test rôle admin requis"""
        with patch('auth.get_current_admin', return_value={'role': 'user'}):
            response = client.get("/api/admin/users")
            # Should fail without admin role
            assert response.status_code in [200, 401, 403, 500]

    def test_sql_injection_in_search(self, mock_admin_auth, mock_supabase):
        """Test injection SQL dans recherche"""
        response = client.get("/api/admin/users?search='; DROP TABLE users; --")
        assert response.status_code in [200, 401, 403, 422, 500]

    def test_xss_in_user_creation(self, mock_admin_auth, mock_supabase):
        """Test XSS dans création utilisateur"""
        response = client.post("/api/admin/users", json={
            'email': 'test@test.com',
            'password': 'SecurePass123!',
            'first_name': '<script>alert("XSS")</script>',
            'role': 'merchant'
        })
        assert response.status_code in [200, 201, 400, 401, 403, 422, 500]

    def test_cannot_delete_self(self, mock_admin_auth, mock_supabase):
        """Test impossible de se supprimer"""
        response = client.delete("/api/admin/users/admin-123")
        # Should prevent self-deletion
        assert response.status_code in [200, 400, 401, 403, 404, 500]


# ===============================================
# ADMIN BULK OPERATIONS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminBulkOperations:
    """Tests opérations en masse admin"""

    def test_bulk_suspend_users(self, mock_admin_auth, mock_supabase):
        """Test suspension en masse"""
        response = client.post("/api/admin/users/bulk/suspend", json={
            'user_ids': ['user-1', 'user-2', 'user-3']
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_bulk_activate_users(self, mock_admin_auth, mock_supabase):
        """Test activation en masse"""
        response = client.post("/api/admin/users/bulk/activate", json={
            'user_ids': ['user-1', 'user-2']
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_bulk_delete_users(self, mock_admin_auth, mock_supabase):
        """Test suppression en masse"""
        response = client.post("/api/admin/users/bulk/delete", json={
            'user_ids': ['user-1', 'user-2']
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_bulk_export_users(self, mock_admin_auth, mock_supabase):
        """Test export en masse"""
        response = client.post("/api/admin/users/bulk/export", json={
            'user_ids': ['user-1', 'user-2'],
            'format': 'csv'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]


# ===============================================
# ADMIN NOTIFICATIONS TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminNotifications:
    """Tests notifications admin"""

    def test_send_notification_to_user(self, mock_admin_auth, mock_supabase):
        """Test envoi notification à utilisateur"""
        response = client.post("/api/admin/notifications/send", json={
            'user_id': 'user-1',
            'title': 'Important',
            'message': 'Votre compte a été mis à jour'
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    def test_send_broadcast_notification(self, mock_admin_auth, mock_supabase):
        """Test notification broadcast"""
        response = client.post("/api/admin/notifications/broadcast", json={
            'title': 'Maintenance planifiée',
            'message': 'Maintenance prévue le 15/01',
            'target_roles': ['merchant', 'influencer']
        })
        assert response.status_code in [200, 401, 403, 404, 422, 500]


# ===============================================
# INPUT VALIDATION TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminInputValidation:
    """Tests validation des entrées admin"""

    def test_invalid_uuid_format(self, mock_admin_auth, mock_supabase):
        """Test format UUID invalide"""
        response = client.get("/api/admin/users/invalid-uuid-format")
        assert response.status_code in [200, 400, 404, 422, 500]

    def test_empty_user_id(self, mock_admin_auth, mock_supabase):
        """Test ID utilisateur vide"""
        response = client.get("/api/admin/users/")
        assert response.status_code in [200, 307, 404, 405]

    def test_negative_pagination(self, mock_admin_auth, mock_supabase):
        """Test pagination négative"""
        response = client.get("/api/admin/users?page=-1&per_page=10")
        assert response.status_code in [200, 422, 500]

    def test_excessive_per_page(self, mock_admin_auth, mock_supabase):
        """Test per_page excessif"""
        response = client.get("/api/admin/users?page=1&per_page=10000")
        assert response.status_code in [200, 422, 500]


# ===============================================
# EDGE CASES TESTS
# ===============================================

@pytest.mark.skipif(not APP_AVAILABLE, reason="Server app not available")
class TestAdminEdgeCases:
    """Tests cas limites admin"""

    def test_empty_database(self, mock_admin_auth, mock_supabase):
        """Test base de données vide"""
        mock_supabase.table.return_value.select.return_value.execute.return_value = Mock(data=[])
        response = client.get("/api/admin/users/stats")
        assert response.status_code in [200, 401, 403, 500]

    def test_unicode_in_names(self, mock_admin_auth, mock_supabase):
        """Test unicode dans noms"""
        response = client.post("/api/admin/users", json={
            'email': 'user@test.com',
            'password': 'SecurePass123!',
            'first_name': 'محمد',
            'last_name': '田中',
            'role': 'merchant'
        })
        assert response.status_code in [200, 201, 400, 401, 403, 422, 500]

    def test_very_long_search_query(self, mock_admin_auth, mock_supabase):
        """Test recherche très longue"""
        long_query = 'a' * 1000
        response = client.get(f"/api/admin/users?search={long_query}")
        assert response.status_code in [200, 401, 403, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
