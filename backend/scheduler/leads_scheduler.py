"""
Scheduler pour le système LEADS
Vérification automatique des dépôts et alertes multi-niveau
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.deposit_service import DepositService
from services.notification_service import NotificationService
from services.lead_service import LeadService
from supabase_client import supabase
from utils.logger import logger

# Delayed initialization of services and scheduler to avoid import-time side-effects
deposit_service = None
notification_service = None
lead_service = None
_scheduler = None


def check_deposits_and_send_alerts():
    """
    Vérification HORAIRE des dépôts et envoi d'alertes multi-niveau
    
    Niveaux d'alerte:
    - 50% solde: Notification dashboard uniquement (INFO)
    - 80% solde: Email + Notification (ATTENTION)
    - 90% solde: Email + SMS + Notification (WARNING)
    - 100% solde: Email + SMS + WhatsApp + Blocage leads (CRITICAL)
    """
    logger.info(f"\n🔍 [{datetime.now()}] Vérification des dépôts...")
    
    try:
        # Récupérer tous les dépôts actifs
        # Use the global supabase client (initialized on import) and services that will be
        # set by start_scheduler() before the scheduler runs.
        response = supabase.table('company_deposits')\
            .select('*')\
            .eq('status', 'active')\
            .execute()
        
        deposits = response.data if response.data else []
        
        if not deposits:
            logger.info("✅ Aucun dépôt actif à vérifier")
            return
        
        alerts_sent = {
            'HEALTHY': 0,
            'ATTENTION': 0,
            'WARNING': 0,
            'CRITICAL': 0,
            'DEPLETED': 0
        }
        
        for deposit in deposits:
            try:
                deposit_id = deposit['id']
                merchant_id = deposit['merchant_id']
                current_balance = float(deposit['current_balance'])
                initial_amount = float(deposit['initial_amount'])
                
                # Calculer le pourcentage restant
                percentage = (current_balance / initial_amount) * 100 if initial_amount > 0 else 0
                
                # Déterminer le niveau d'alerte
                if current_balance <= 0:
                    # 🔴 DEPLETED - Blocage total
                    alert_level = 'DEPLETED'
                    
                    # Marquer le dépôt comme épuisé
                    supabase.table('company_deposits')\
                        .update({
                            'status': 'depleted',
                            'depleted_at': datetime.now().isoformat()
                        })\
                        .eq('id', deposit_id)\
                        .execute()
                    
                    # Arrêter toutes les campagnes associées
                    if deposit.get('campaign_id'):
                        supabase.table('campaigns')\
                            .update({'status': 'paused'})\
                            .eq('id', deposit['campaign_id'])\
                            .execute()
                    
                    # Envoyer alerte CRITIQUE (Email + SMS + WhatsApp + Dashboard)
                    if notification_service:
                        notification_service.send_deposit_depleted_alert(
                        merchant_id=merchant_id,
                        deposit_id=deposit_id,
                        campaign_id=deposit.get('campaign_id')
                    )
                    
                    alerts_sent['DEPLETED'] += 1
                    logger.info(f"🔴 DEPLETED: Dépôt {deposit_id} épuisé (0 dhs)")
                
                elif percentage <= 10:
                    # 🟠 CRITICAL - 90%+ utilisé
                    alert_level = 'CRITICAL'
                    
                    # Email + SMS + WhatsApp + Dashboard
                    if notification_service:
                        notification_service.send_low_balance_alert(
                        merchant_id=merchant_id,
                        deposit_id=deposit_id,
                        current_balance=current_balance,
                        threshold=deposit['alert_threshold'],
                        alert_level='CRITICAL',
                        channels=['email', 'sms', 'whatsapp', 'dashboard']
                    )
                    
                    alerts_sent['CRITICAL'] += 1
                    logger.error(f"🟠 CRITICAL: Dépôt {deposit_id} à {percentage:.1f}% ({current_balance} dhs)")
                
                elif percentage <= 20:
                    # 🟡 WARNING - 80%+ utilisé
                    alert_level = 'WARNING'
                    
                    # Email + SMS + Dashboard
                    if notification_service:
                        notification_service.send_low_balance_alert(
                        merchant_id=merchant_id,
                        deposit_id=deposit_id,
                        current_balance=current_balance,
                        threshold=deposit['alert_threshold'],
                        alert_level='WARNING',
                        channels=['email', 'sms', 'dashboard']
                    )
                    
                    alerts_sent['WARNING'] += 1
                    logger.warning(f"🟡 WARNING: Dépôt {deposit_id} à {percentage:.1f}% ({current_balance} dhs)")
                
                elif percentage <= 50:
                    # 🟢 ATTENTION - 50%+ utilisé
                    alert_level = 'ATTENTION'
                    
                    # Email + Dashboard uniquement
                    if notification_service:
                        notification_service.send_low_balance_alert(
                        merchant_id=merchant_id,
                        deposit_id=deposit_id,
                        current_balance=current_balance,
                        threshold=deposit['alert_threshold'],
                        alert_level='ATTENTION',
                        channels=['email', 'dashboard']
                    )
                    
                    alerts_sent['ATTENTION'] += 1
                    logger.info(f"🟢 ATTENTION: Dépôt {deposit_id} à {percentage:.1f}% ({current_balance} dhs)")
                
                else:
                    # ✅ HEALTHY - Plus de 50% restant
                    alert_level = 'HEALTHY'
                    alerts_sent['HEALTHY'] += 1
                
                # Mettre à jour la date de dernière alerte
                if alert_level != 'HEALTHY':
                    supabase.table('company_deposits')\
                        .update({'last_alert_sent': datetime.now().isoformat()})\
                        .eq('id', deposit_id)\
                        .execute()
            
            except Exception as e:
                logger.info(f"❌ Erreur lors du traitement du dépôt {deposit.get('id')}: {e}")
                continue
        
        # Résumé
        logger.info(f"\n📊 Résumé de la vérification:")
        logger.info(f"   ✅ HEALTHY: {alerts_sent['HEALTHY']} dépôts")
        logger.info(f"   🟢 ATTENTION (50%): {alerts_sent['ATTENTION']} alertes")
        logger.warning(f"   🟡 WARNING (80%): {alerts_sent['WARNING']} alertes")
        logger.error(f"   🟠 CRITICAL (90%): {alerts_sent['CRITICAL']} alertes")
        logger.info(f"   🔴 DEPLETED (100%): {alerts_sent['DEPLETED']} dépôts épuisés")
        
    except Exception as e:
        logger.info(f"❌ Erreur lors de la vérification des dépôts: {e}")


def cleanup_expired_leads():
    """
    Nettoyer les leads expirés (plus de 72h en pending sans validation)
    Exécuté tous les jours à 23:00
    """
    logger.info(f"\n🧹 [{datetime.now()}] Nettoyage des leads expirés...")
    
    try:
        # Récupérer les leads en attente depuis plus de 72h
        expiration_date = (datetime.now() - timedelta(hours=72)).isoformat()
        
        response = supabase.table('leads')\
            .select('*')\
            .eq('status', 'pending')\
            .lt('created_at', expiration_date)\
            .execute()
        
        expired_leads = response.data if response.data else []
        
        if not expired_leads:
            logger.info("✅ Aucun lead expiré à nettoyer")
            return
        
        logger.info(f"📦 {len(expired_leads)} leads expirés trouvés")
        
        for lead in expired_leads:
            try:
                lead_id = lead['id']
                
                # Marquer comme "lost" (perdu)
                supabase.table('leads')\
                    .update({
                        'status': 'lost',
                        'rejection_reason': 'Expiré - Aucune validation après 72h',
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', lead_id)\
                    .execute()
                
                # Libérer la commission réservée
                if lead.get('commission_amount'):
                    deposit_id = supabase.table('company_deposits')\
                        .select('id')\
                        .eq('merchant_id', lead['merchant_id'])\
                        .eq('status', 'active')\
                        .limit(1)\
                        .execute()
                    
                    if deposit_id.data and len(deposit_id.data) > 0:
                        # NOTE: keep operations simple here; services should handle complex logic when available
                        try:
                            current_reserved = supabase.table('company_deposits').select('reserved_amount').eq('id', deposit_id.data[0]['id']).execute().data[0]['reserved_amount']
                            supabase.table('company_deposits')\
                                .update({
                                    'reserved_amount': float(current_reserved) - float(lead['commission_amount'])
                                })\
                                .eq('id', deposit_id.data[0]['id'])\
                                .execute()
                        except Exception:
                            pass
                
                logger.info(f"   🗑️  Lead {lead_id} expiré et marqué comme perdu")
            
            except Exception as e:
                logger.info(f"   ❌ Erreur lead {lead.get('id')}: {e}")
                continue
        
        logger.info(f"✅ {len(expired_leads)} leads expirés nettoyés")
    
    except Exception as e:
        logger.info(f"❌ Erreur lors du nettoyage: {e}")


def generate_daily_report():
    """
    Génère un rapport quotidien pour les admins
    Exécuté tous les jours à 09:00
    """
    logger.info(f"\n📊 [{datetime.now()}] Génération du rapport quotidien...")
    
    try:
        # Statistiques leads des dernières 24h
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        # Compter leads créés
        leads_created = supabase.table('leads')\
            .select('id', count='exact')\
            .gte('created_at', yesterday)\
            .execute()
        
        # Compter leads validés
        leads_validated = supabase.table('leads')\
            .select('id', count='exact')\
            .gte('validated_at', yesterday)\
            .eq('status', 'validated')\
            .execute()
        
        # Compter leads rejetés
        leads_rejected = supabase.table('leads')\
            .select('id', count='exact')\
            .gte('updated_at', yesterday)\
            .eq('status', 'rejected')\
            .execute()
        rejected_count = leads_rejected.count if hasattr(leads_rejected, 'count') else 0
        
        # Dépôts bas
        low_deposits = supabase.table('company_deposits')\
            .select('*')\
            .eq('status', 'active')\
            .execute()
        
        deposits_below_50 = sum(1 for d in (low_deposits.data or []) 
                                if (float(d['current_balance']) / float(d['initial_amount']) * 100) <= 50)
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'leads_created_24h': leads_created.count if hasattr(leads_created, 'count') else 0,
            'leads_validated_24h': leads_validated.count if hasattr(leads_validated, 'count') else 0,
            'leads_rejected_24h': rejected_count,
            'deposits_below_50_percent': deposits_below_50,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\n📈 Rapport quotidien:")
        logger.info(f"   📦 Leads créés (24h): {report['leads_created_24h']}")
        logger.info(f"   ✅ Leads validés (24h): {report['leads_validated_24h']}")
        logger.info(f"   ❌ Leads rejetés (24h): {report['leads_rejected_24h']}")
        logger.info(f"   ⚠️  Dépôts < 50%: {report['deposits_below_50_percent']}")
        
        # Envoyer le rapport aux admins
        # TODO: Implémenter l'envoi email du rapport
        
        return report
    
    except Exception as e:
        logger.info(f"❌ Erreur génération rapport: {e}")


# ============================================
# CONFIGURATION DU SCHEDULER
# ============================================

def _create_scheduler_jobs(scheduler_obj):
    """Register jobs on the provided scheduler object."""
    # Vérification des dépôts TOUTES LES HEURES
    scheduler_obj.add_job(
        check_deposits_and_send_alerts,
        trigger=CronTrigger(minute=0),  # Chaque heure à H:00
        id='check_deposits',
        name='Vérification dépôts et alertes',
        replace_existing=True
    )

    # Nettoyage des leads expirés TOUS LES JOURS à 23:00
    scheduler_obj.add_job(
        cleanup_expired_leads,
        trigger=CronTrigger(hour=23, minute=0),  # 23:00 tous les jours
        id='cleanup_leads',
        name='Nettoyage leads expirés',
        replace_existing=True
    )

    # Rapport quotidien TOUS LES JOURS à 09:00
    scheduler_obj.add_job(
        generate_daily_report,
        trigger=CronTrigger(hour=9, minute=0),  # 09:00 tous les jours
        id='daily_report',
        name='Rapport quotidien',
        replace_existing=True
    )


def start_scheduler():
    """Démarre le scheduler"""
    global _scheduler, deposit_service, notification_service, lead_service
    if _scheduler is not None:
        logger.info("ℹ️ Scheduler already started")
        return _scheduler

    try:
        # Initialize services only when starting the scheduler to avoid import-time work
        try:
            deposit_service = DepositService(supabase)
            notification_service = NotificationService(supabase)
            lead_service = LeadService(supabase)
        except Exception as e:
            logger.info(f"⚠️ Could not initialize services for scheduler: {e}")

        _scheduler = BackgroundScheduler(timezone='Africa/Casablanca')
        _create_scheduler_jobs(_scheduler)
        _scheduler.start()
        logger.info("\n✅ Scheduler LEADS démarré avec succès!")
        logger.info("   🔄 Vérification dépôts: Toutes les heures")
        logger.info("   🧹 Nettoyage leads expirés: 23:00 quotidien")
        logger.info("   📊 Rapport quotidien: 09:00 quotidien")
        return _scheduler
    except Exception as e:
        logger.info(f"❌ Erreur démarrage scheduler: {e}")
        _scheduler = None
        return None


def stop_scheduler():
    """Arrête le scheduler"""
    global _scheduler
    try:
        if _scheduler is None:
            logger.info("ℹ️ Scheduler not running")
            return
        _scheduler.shutdown()
        _scheduler = None
        logger.info("✅ Scheduler arrêté")
    except Exception as e:
        logger.info(f"❌ Erreur arrêt scheduler: {e}")


if __name__ == "__main__":
    # Test manuel
    logger.info("🧪 Test manuel du scheduler LEADS\n")
    
    logger.info("1️⃣ Test vérification dépôts...")
    check_deposits_and_send_alerts()
    
    logger.info("\n2️⃣ Test nettoyage leads expirés...")
    cleanup_expired_leads()
    
    logger.info("\n3️⃣ Test rapport quotidien...")
    generate_daily_report()
    
    logger.info("\n✅ Tests terminés")
