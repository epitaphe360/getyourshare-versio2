
#!/usr/bin/env python3
"""
Script de seed pour les fonctionnalités manquantes:
- Abonnements (Subscriptions)
- Commissions
- Factures (Invoices)
- Avis produits (Reviews)
- Messagerie (Conversations & Messages)
- Mise à jour Marketplace (Featured, etc.)
"""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase_client import supabase
from utils.logger import logger

load_dotenv()

def seed_missing_features():
    logger.info("="*70)
    logger.info("🚀 SEEDING MISSING FEATURES (Subscriptions, Messages, Reviews...)")
    logger.info("="*70)
    print()

    try:
        # 1. Fetch Base Data
        logger.info("📥 Fetching base data...")
        users = supabase.table("users").select("id, role, email, first_name, last_name").execute().data
        products = supabase.table("products").select("id, merchant_id, name, price").execute().data
        sales = supabase.table("sales").select("id, influencer_id, amount, created_at, merchant_id").execute().data
        
        merchants = [u for u in users if u.get('role') == 'merchant']
        influencers = [u for u in users if u.get('role') == 'influencer']
        
        logger.info(f"  - Users: {len(users)} (Merchants: {len(merchants)}, Influencers: {len(influencers)})")
        logger.info(f"  - Products: {len(products)}")
        logger.info(f"  - Sales: {len(sales)}")
        print()

        # 2. Seed Subscriptions
        logger.info("💳 Seeding Subscriptions...")
        plans_res = supabase.table("subscription_plans").select("id, price").execute()
        plans = plans_res.data if plans_res.data else []
        
        if not plans:
            logger.info("  ⚠️ No subscription plans found. Skipping subscriptions.")
        else:
            subs_count = 0
            total_users = len(users)
            for i, user in enumerate(users):
                if i % 10 == 0:
                    logger.info(f"  ⏳ Processing user {i+1}/{total_users}...")
                
                # Check if sub exists
                try:
                    existing = supabase.table("subscriptions").select("id").eq("user_id", user['id']).execute()
                    if not existing.data:
                        plan = random.choice(plans)
                        status = random.choice(['active', 'active', 'active', 'cancelled'])
                        
                        sub_data = {
                            "user_id": user['id'],
                            "plan_id": plan['id'],
                            "status": status,
                            "current_period_start": datetime.now().isoformat(),
                            "current_period_end": (datetime.now() + timedelta(days=30)).isoformat(),
                            "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
                        }
                        supabase.table("subscriptions").insert(sub_data).execute()
                        subs_count += 1
                except Exception as e:
                    logger.error(f"  ❌ Error creating subscription for {user['email']}: {e}")
            logger.info(f"  ✅ Created {subs_count} subscriptions.")
        print()

        # 3. Seed Commissions
        logger.info("💰 Seeding Commissions...")
        commissions_count = 0
        total_sales = len(sales)
        for i, sale in enumerate(sales):
            if i % 10 == 0:
                logger.info(f"  ⏳ Processing sale {i+1}/{total_sales}...")
            
            # Check if commission exists
            try:
                existing = supabase.table("commissions").select("id").eq("sale_id", sale['id']).execute()
                if not existing.data and sale.get('influencer_id'):
                    amount = float(sale['amount']) * 0.10 # 10% commission
                    status = random.choice(['pending', 'approved', 'paid'])
                    
                    comm_data = {
                        "influencer_id": sale['influencer_id'],
                        "sale_id": sale['id'],
                        "amount": amount,
                        "status": status,
                        "created_at": sale['created_at'],
                        "merchant_id": sale.get('merchant_id') # Some schemas have this
                    }
                    
                    # Remove merchant_id if it causes error (schema variation)
                    try:
                        supabase.table("commissions").insert(comm_data).execute()
                        commissions_count += 1
                    except Exception as e:
                        if "merchant_id" in str(e):
                            del comm_data["merchant_id"]
                            try:
                                supabase.table("commissions").insert(comm_data).execute()
                                commissions_count += 1
                            except Exception as e2:
                                pass
                        else:
                            pass
            except Exception as e:
                logger.error(f"  ❌ Error processing sale {sale['id']}: {e}")
        logger.info(f"  ✅ Created {commissions_count} commissions.")
        print()

        # 4. Seed Invoices
        logger.info("🧾 Seeding Invoices...")
        invoices_count = 0
        total_merchants = len(merchants)
        for i, merchant in enumerate(merchants):
            if i % 5 == 0:
                logger.info(f"  ⏳ Processing merchant {i+1}/{total_merchants}...")
            
            # Create 1-3 invoices per merchant
            for _ in range(random.randint(1, 3)):
                amount = random.choice([29.00, 99.00, 199.00])
                status = random.choice(['paid', 'paid', 'pending'])
                date = (datetime.now() - timedelta(days=random.randint(1, 90)))
                
                inv_data = {
                    "user_id": merchant['id'],
                    "amount": amount,
                    "status": status,
                    "invoice_number": f"INV-{random.randint(10000, 99999)}",
                    "due_date": (date + timedelta(days=30)).isoformat(),
                    "created_at": date.isoformat()
                }
                
                if status == 'paid':
                    inv_data['paid_at'] = (date + timedelta(days=random.randint(0, 5))).isoformat()
                
                try:
                    supabase.table("invoices").insert(inv_data).execute()
                    invoices_count += 1
                except Exception as e:
                    pass
        logger.info(f"  ✅ Created {invoices_count} invoices.")
        print()

        # 5. Seed Product Reviews
        logger.info("⭐ Seeding Product Reviews...")
        reviews_count = 0
        comments = [
            "Excellent produit !", "Je recommande vivement.", "Bon rapport qualité/prix.",
            "Livraison rapide.", "Un peu cher mais ça vaut le coup.", "Super !",
            "Pas mal.", "Très satisfait.", "Service client au top."
        ]
        
        total_products = len(products)
        for i, product in enumerate(products):
            if i % 10 == 0:
                logger.info(f"  ⏳ Processing product {i+1}/{total_products}...")
            
            # 0-5 reviews per product
            for _ in range(random.randint(0, 5)):
                reviewer = random.choice(users)
                rating = random.randint(3, 5)
                
                review_data = {
                    "product_id": product['id'],
                    "user_id": reviewer['id'],
                    "rating": rating,
                    "review": random.choice(comments), # Note: Schema said 'review' column, code sometimes uses 'comment'
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 100))).isoformat()
                }
                
                try:
                    supabase.table("product_reviews").insert(review_data).execute()
                    reviews_count += 1
                except Exception as e:
                    # Try 'comment' instead of 'review' if it fails
                    if "review" in str(e):
                        review_data['comment'] = review_data.pop('review')
                        try:
                            supabase.table("product_reviews").insert(review_data).execute()
                            reviews_count += 1
                        except Exception:
                            pass
        logger.info(f"  ✅ Created {reviews_count} reviews.")
        print()

        # 6. Seed Conversations & Messages
        logger.info("💬 Seeding Messages...")
        msgs_count = 0
        convs_count = 0
        
        # Create conversations between random merchant and influencer
        for _ in range(10):
            if not merchants or not influencers: break
            
            m = random.choice(merchants)
            i = random.choice(influencers)
            
            # Check schema for participant_ids
            # Based on check_tables_v2.py: participant_ids is the column
            
            participant_ids = [m['id'], i['id']]
            
            conv_data = {
                "participant_ids": participant_ids,
                "last_message": "Bonjour, intéressé par une collab ?",
                "last_message_at": datetime.now().isoformat()
            }
            
            try:
                res = supabase.table("conversations").insert(conv_data).execute()
                if res.data:
                    conv_id = res.data[0]['id']
                    convs_count += 1
                    
                    # Add messages
                    msgs = [
                        (m['id'], "Bonjour, intéressé par une collab ?"),
                        (i['id'], "Bonjour ! Oui, quel est le produit ?"),
                        (m['id'], "C'est notre nouveau gadget tech."),
                        (i['id'], "Super, envoyez-moi les détails !")
                    ]
                    
                    for sender_id, content in msgs:
                        msg_data = {
                            "conversation_id": conv_id,
                            "sender_id": sender_id,
                            "content": content,
                            "is_read": random.choice([True, False])
                        }
                        supabase.table("messages").insert(msg_data).execute()
                        msgs_count += 1
            except Exception as e:
                logger.error(f"  ❌ Error creating conversation: {e}")
                
        logger.info(f"  ✅ Created {convs_count} conversations and {msgs_count} messages.")
        print()

        # 7. Update Products (Featured, etc.)
        logger.info("🌟 Updating Products (Featured, Ratings)...")
        updated_count = 0
        
        for product in products:
            updates = {}
            
            # Try to set featured
            if random.random() > 0.8: # 20% featured
                updates['featured'] = True
            
            # Try to set stats
            updates['reviews_count'] = random.randint(0, 50)
            updates['rating'] = round(random.uniform(3.5, 5.0), 2)
            updates['sold_count'] = random.randint(0, 100)
            
            if updates:
                try:
                    supabase.table("products").update(updates).eq("id", product['id']).execute()
                    updated_count += 1
                except Exception as e:
                    # Likely columns missing
                    if updated_count == 0:
                        logger.warning(f"  ⚠️  Could not update product stats. Columns might be missing. Error: {e}")
                        logger.warning("  👉 Please run 'ADD_MARKETPLACE_COLUMNS.sql' in Supabase SQL Editor.")
                        break # Stop trying if it fails once
        
        if updated_count > 0:
            logger.info(f"  ✅ Updated {updated_count} products with stats.")
        
        print()
        logger.info("="*70)
        logger.info("✅ SEEDING COMPLETE!")
        logger.info("="*70)
        return True

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    seed_missing_features()
