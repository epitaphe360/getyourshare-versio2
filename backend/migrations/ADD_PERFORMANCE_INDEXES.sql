PS C:\Users\samye\OneDrive\Desktop\getyourshare version 6\getyourshare-versio2>S
et-Content -Path "c:\Users\samye\OneDrive\Desktop\getyourshare version 6\getyour
share-versio2\backend\migrations\ADD_PERFORMANCE_INDEXES.sql" -Value @'
>> -- ============================================================
>> -- INDEX DE PERFORMANCE - GetYourShare
>> -- VERSION ROBUSTE : chaque index dans un DO block
>> -- Les colonnes/tables manquantes sont ignorees
>> -- ============================================================
>>
>> -- TRACKING EVENTS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_events_link_type    ON tr
acking_events(tracking_link_id, event_type);           EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_tracking_events_link_type: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_events_type_date    ON tr
acking_events(event_type, created_at DESC);             EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_tracking_events_type_date: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_events_campaign_date ON t
racking_events(campaign_id, created_at DESC);           EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_tracking_events_campaign_date: %', SQLERRM; END $$;        
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_events_device       ON tr
acking_events(device_type) WHERE device_type IS NOT NULL; EXCEPTION WHEN others 
THEN RAISE NOTICE 'idx_tracking_events_device: %', SQLERRM; END $$;
>>
>> -- TRACKING LINKS (influencer_id, pas user_id)
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_links_influencer    ON tr
acking_links(influencer_id);                            EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_tracking_links_influencer: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_links_short_code    ON tr
acking_links(short_code);                               EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_tracking_links_short_code: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_links_campaign      ON tr
acking_links(campaign_id) WHERE campaign_id IS NOT NULL; EXCEPTION WHEN others T
HEN RAISE NOTICE 'idx_tracking_links_campaign: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_tracking_links_merchant      ON tr
acking_links(merchant_id) WHERE merchant_id IS NOT NULL; EXCEPTION WHEN others T
HEN RAISE NOTICE 'idx_tracking_links_merchant: %', SQLERRM; END $$;
>>
>> -- CONVERSIONS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_conversions_influencer_date  ON co
nversions(influencer_id, created_at DESC);              EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_conversions_influencer_date: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_conversions_merchant_date    ON co
nversions(merchant_id, created_at DESC);                EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_conversions_merchant_date: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_conversions_status_date      ON co
nversions(status, created_at DESC);                     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_conversions_status_date: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_conversions_paid_at          ON co
nversions(paid_at DESC) WHERE paid_at IS NOT NULL;      EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_conversions_paid_at: %', SQLERRM; END $$;
>>
>> -- NOTIFICATIONS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_notifications_user_unread    ON no
tifications(user_id, is_read, created_at DESC);         EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_notifications_user_unread: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_notifications_type           ON no
tifications(type, created_at DESC);                     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_notifications_type: %', SQLERRM; END $$;
>>
>> -- PRODUCTS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_products_category_active     ON pr
oducts(category, is_active) WHERE is_active = true;     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_products_category_active: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_products_merchant_active     ON pr
oducts(merchant_id, is_active);                         EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_products_merchant_active: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_products_rating              ON pr
oducts(rating DESC) WHERE is_active = true;             EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_products_rating: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_products_created             ON pr
oducts(created_at DESC);                                EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_products_created: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_products_name_gin ON products USIN
G gin(to_tsvector('french', coalesce(name,'') || ' ' || coalesce(description,'')
)); EXCEPTION WHEN others THEN RAISE NOTICE 'idx_products_name_gin: %', SQLERRM;
 END $$;
>>
>> -- CAMPAIGNS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_campaigns_merchant_status    ON ca
mpaigns(merchant_id, status);                           EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_campaigns_merchant_status: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_campaigns_status_dates       ON ca
mpaigns(status, start_date, end_date);                  EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_campaigns_status_dates: %', SQLERRM; END $$;
>>
>> -- SALES_LEADS (sales_rep_id, pas commercial_id)
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_sales_leads_rep_status       ON sa
les_leads(sales_rep_id, status);                        EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_sales_leads_rep_status: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_sales_leads_status_date      ON sa
les_leads(status, created_at DESC);                     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_sales_leads_status_date: %', SQLERRM; END $$;
>>
>> -- USERS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_users_email                  ON us
ers(email);                                             EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_users_email: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_users_role_active            ON us
ers(role, is_active) WHERE is_active = true;            EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_users_role_active: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_users_username               ON us
ers(username) WHERE username IS NOT NULL;               EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_users_username: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_users_last_login             ON us
ers(last_login DESC) WHERE last_login IS NOT NULL;      EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_users_last_login: %', SQLERRM; END $$;
>>
>> -- MERCHANTS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_merchants_user               ON me
rchants(user_id);                                       EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_merchants_user: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_merchants_verified           ON me
rchants(is_verified) WHERE is_verified = true;          EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_merchants_verified: %', SQLERRM; END $$;
>>
>> -- INFLUENCERS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_influencers_user             ON in
fluencers(user_id);                                     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_influencers_user: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_influencers_audience         ON in
fluencers(audience_size DESC) WHERE audience_size IS NOT NULL; EXCEPTION WHEN ot
hers THEN RAISE NOTICE 'idx_influencers_audience: %', SQLERRM; END $$;
>>
>> -- AFFILIATE_REQUESTS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_affiliate_requests_influencer ON a
ffiliate_requests(influencer_id, status);              EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_affiliate_requests_influencer: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_affiliate_requests_merchant   ON a
ffiliate_requests(merchant_id, status);                EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_affiliate_requests_merchant: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_affiliate_requests_created    ON a
ffiliate_requests(created_at DESC);                    EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_affiliate_requests_created: %', SQLERRM; END $$;
>>
>> -- INVOICES
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_invoices_user_date           ON in
voices(user_id, created_at DESC);                       EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_invoices_user_date: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_invoices_status              ON in
voices(status, created_at DESC);                        EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_invoices_status: %', SQLERRM; END $$;
>>
>> -- PAYOUTS (influencer_id, pas user_id)
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_payouts_influencer_status    ON pa
youts(influencer_id, status);                           EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_payouts_influencer_status: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_payouts_created              ON pa
youts(created_at DESC);                                 EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_payouts_created: %', SQLERRM; END $$;
>>
>> -- SUBSCRIPTIONS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status    ON su
bscriptions(user_id, status);                          EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_subscriptions_user_status: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_subscriptions_expires        ON su
bscriptions(current_period_end) WHERE status = 'active'; EXCEPTION WHEN others T
HEN RAISE NOTICE 'idx_subscriptions_expires: %', SQLERRM; END $$;
>>
>> -- CONVERSATIONS (participant_ids UUID[], pas participant1_id)
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_conversations_updated        ON co
nversations(last_message_at DESC);                      EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_conversations_updated: %', SQLERRM; END $$;
>>
>> -- MESSAGES
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_messages_conversation_date   ON me
ssages(conversation_id, created_at DESC);               EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_messages_conversation_date: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_messages_sender              ON me
ssages(sender_id, created_at DESC);                     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_messages_sender: %', SQLERRM; END $$;
>>
>> -- API_KEYS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_api_keys_key_active          ON ap
i_keys(key) WHERE is_active = true;                     EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_api_keys_key_active: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_api_keys_user                ON ap
i_keys(user_id);                                        EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_api_keys_user: %', SQLERRM; END $$;
>>
>> -- TOKENS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_password_reset_email         ON pa
ssword_reset_tokens(email) WHERE used = false;         EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_password_reset_email: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_email_verification_email     ON em
ail_verification_tokens(email) WHERE used = false;     EXCEPTION WHEN others THE
N RAISE NOTICE 'idx_email_verification_email: %', SQLERRM; END $$;
>>
>> -- WEBHOOK_LOGS
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_webhook_logs_created         ON we
bhook_logs(created_at DESC);                            EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_webhook_logs_created: %', SQLERRM; END $$;
>> DO $$ BEGIN CREATE INDEX IF NOT EXISTS idx_webhook_logs_source          ON we
bhook_logs(source, created_at DESC);                    EXCEPTION WHEN others TH
EN RAISE NOTICE 'idx_webhook_logs_source: %', SQLERRM; END $$;
>>
>> -- ============================================================
>> -- VUES MATERIALISEES ANALYTICS
>> -- ============================================================
>> DO $$ BEGIN
>>   CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_conversion_stats AS        
>>   SELECT
>>       DATE(created_at)              AS day,
>>       COUNT(*)                      AS total_conversions,
>>       SUM(amount)                   AS total_revenue,
>>       AVG(amount)                   AS avg_amount,
>>       COUNT(DISTINCT influencer_id) AS active_influencers,
>>       COUNT(DISTINCT merchant_id)   AS active_merchants
>>   FROM conversions
>>   WHERE created_at >= NOW() - INTERVAL '90 days'
>>   GROUP BY DATE(created_at)
>>   ORDER BY day DESC;
>> EXCEPTION WHEN others THEN RAISE NOTICE 'mv_daily_conversion_stats: %', SQLER
RM; END $$;
>>
>> DO $$ BEGIN
>>   CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_conversion_stats_day        
>>     ON mv_daily_conversion_stats(day);
>> EXCEPTION WHEN others THEN RAISE NOTICE 'idx_mv_daily_conversion_stats_day: %
', SQLERRM; END $$;
>>
>> DO $$ BEGIN
>>   CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_products AS
>>   SELECT
>>       p.id,
>>       p.name,
>>       p.merchant_id,
>>       COUNT(DISTINCT tl.id)      AS link_count,
>>       COUNT(DISTINCT te.id)      AS click_count,
>>       COUNT(DISTINCT c.id)       AS conversion_count,
>>       COALESCE(SUM(c.amount), 0) AS total_revenue
>>   FROM products p
>>   LEFT JOIN tracking_links tl  ON tl.product_id = p.id
>>   LEFT JOIN tracking_events te ON te.tracking_link_id = tl.id AND te.event_ty
pe = 'click'
>>   LEFT JOIN conversions c      ON c.product_id = p.id
>>   WHERE p.is_active = true
>>   GROUP BY p.id, p.name, p.merchant_id
>>   ORDER BY total_revenue DESC
>>   LIMIT 100;
>> EXCEPTION WHEN others THEN RAISE NOTICE 'mv_top_products: %', SQLERRM; END $$
;
>>
>> DO $$ BEGIN
>>   CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_products_id ON mv_top_products
(id);
>> EXCEPTION WHEN others THEN RAISE NOTICE 'idx_mv_top_products_id: %', SQLERRM;
 END $$;
>>
>> CREATE OR REPLACE FUNCTION refresh_analytics_views()
>> RETURNS VOID AS $$
>> BEGIN
>>     REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_conversion_stats;        
>>     REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_products;
>> END;
>> $$ LANGUAGE plpgsql SECURITY DEFINER;
>>
>> -- Verification
>> SELECT COUNT(*) AS nb_index_crees FROM pg_indexes WHERE schemaname = 'public'
;
>> '@
PS C:\Users\samye\OneDrive\Desktop\getyourshare version 6\getyourshare-versio2> 
