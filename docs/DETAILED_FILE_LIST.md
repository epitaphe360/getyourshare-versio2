
════════════════════════════════════════════════════════════════════════════════════
LISTE DÉTAILLÉE DES FICHIERS PROBLÉMATIQUES
════════════════════════════════════════════════════════════════════════════════════

GROUPE 1: PII EXPOSURE EN LOGS (8 fichiers)
════════════════════════════════════════════════════════════════════════════════════

Ces fichiers exposent potentiellement des informations sensibles en logs:

1. backend/celery_tasks.py
   Problème: Email/password logging probable
   Action: Audit des log statements pour PII
   
2. backend/social_media_endpoints.py
   Problème: User tokens en logs
   Action: Masquer tokens, utiliser user_id seulement
   
3. backend/payment_gateways.py
   Problème: Credit card info en logs
   Action: Masquer données de paiement
   
4. backend/webhook_service.py
   Problème: Tokens en logs
   Action: Loguer user_id au lieu de tokens
   
5. backend/services/email_service.py
   Problème: Emails en logs
   Action: Utiliser hash ou mask d'email
   
6. backend/twofa_endpoints.py
   Problème: 2FA codes en logs
   Action: Loguer seulement "2fa_attempt" sans code
   
7. backend/affiliation_requests_endpoints.py
   Problème: Potentielle données utilisateur en logs
   Action: Utiliser user_id au lieu de full user data
   
8. backend/invoicing_service.py
   Problème: Informations de facturation sensibles
   Action: Loguer seulement invoice_id, pas montants


GROUPE 2: SQL INJECTION VIA F-STRINGS (7 fichiers)
════════════════════════════════════════════════════════════════════════════════════

Ces fichiers utilisent f-strings avec requêtes database:

1. backend/admin_social_endpoints.py
   Problème: f"SELECT ... WHERE id = {id}"
   Fix: Utiliser supabase.table().eq()
   
2. backend/advanced_helpers.py
   Problème: Plusieurs f-strings avec queries
   Fix: Remplacer par parameterized queries
   
3. backend/affiliate_links_endpoints.py
   Problème: f-string database queries
   Fix: Utiliser supabase client
   
4. backend/affiliation_requests_endpoints.py
   Problème: f-string SQL patterns
   Fix: Parameterized queries
   
5. backend/ai_assistant_endpoints.py
   Problème: f"SELECT" patterns
   Fix: Supabase select().eq() methods


GROUPE 3: MISSING LOGGING (112 fichiers)
════════════════════════════════════════════════════════════════════════════════════

Top 10 problématiques:

1. backend/db_helpers.py
   Type: Helper functions
   Size: Large file (utility functions)
   Action: Add structlog logger
   
2. backend/advanced_helpers.py
   Type: Helper/utility
   Issues: Has 18 print() statements instead
   Action: Add logging, replace print with logger
   
3. backend/auto_payment_service.py
   Type: Service
   Size: Large file
   Action: Add comprehensive logging
   
4. backend/repositories/user_repository.py
   Type: Repository pattern
   Action: Add logging to DB operations
   
5. backend/payment_service.py
   Type: Payment service
   Issues: Critical service without logging
   Action: Add structured logging
   
6. backend/utils/supabase_client.py
   Type: Client wrapper
   Action: Add logging for connection issues
   
7. backend/services/notification_service.py
   Type: Service
   Action: Add event logging
   
8. backend/services/analytics_service.py
   Type: Service
   Action: Add analytics logging
   
9. backend/services/local_content_generator.py
   Type: Service
   Action: Add operation logging
   
10. backend/services/report_generator.py
    Type: Service
    Action: Add generation logging
    
...Plus 102 autres fichiers sans logging


GROUPE 4: BARE EXCEPT CLAUSES (3 fichiers)
════════════════════════════════════════════════════════════════════════════════════

1. backend/apply_subscription_system.py
   Line: (À identifier par grep)
   Issue: except: without exception type
   Fix: except (SpecificException1, SpecificException2) as e:
   
2. backend/auth.py
   Line: 41-45
   Code: 
       except Exception:
           raise HTTPException(...)
   Issue: Trop générique
   Fix: 
       except jwt.ExpiredSignatureError:
           raise HTTPException(status_code=401, detail="Token expired")
       except jwt.InvalidTokenError:
           raise HTTPException(status_code=401, detail="Token invalid")


GROUPE 5: MISSING TIMEOUTS (5-7 fichiers)
════════════════════════════════════════════════════════════════════════════════════

Endpoints qui font des requêtes sans timeout:

1. backend/admin_social_endpoints.py
   Issue: No asyncio.wait_for() with timeout
   Action: Wrap DB operations in timeout
   
2. backend/advanced_endpoints.py
   Issue: Missing timeout configuration
   Action: Add 30s timeout
   
3. backend/affiliate_links_endpoints.py
   Issue: DB operations without timeout
   Action: asyncio.wait_for(operation, timeout=30)
   
4. backend/affiliation_requests_endpoints.py
   Issue: No timeout config
   Action: Add timeout to DB ops
   
5. backend/test_login.py
   Issue: requests.get/post without timeout
   Action: requests.get(url, timeout=30)
   
6. backend/test_endpoints.py
   Issue: HTTP requests without timeout
   Action: Add timeout=30 parameter


GROUPE 6: PRINT STATEMENTS (18 instances en advanced_helpers.py)
════════════════════════════════════════════════════════════════════════════════════

Pattern à remplacer dans advanced_helpers.py:

❌ print(f"...")
✓ logger.info("event_name", key=value)

❌ print("Error:", error)
✓ logger.error("error_event", error=str(error))

❌ print("DEBUG:", variable)
✓ logger.debug("debug_info", variable=variable)


GROUPE 7: JWT SECRET FALLBACK (1 fichier)
════════════════════════════════════════════════════════════════════════════════════

backend/auth.py - Line 18
Current:
    JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-please-set-env-variable")

Problem:
    - Fallback est trivial et hardcodé
    - Permet démarrage sans secret configuré
    - Token forgery possible avec fallback

Fix:
    import sys
    JWT_SECRET = os.getenv("JWT_SECRET")
    if not JWT_SECRET:
        print("ERROR: JWT_SECRET environment variable is required")
        sys.exit(1)
    
    if len(JWT_SECRET) < 32:
        print("ERROR: JWT_SECRET must be at least 32 characters")
        sys.exit(1)


════════════════════════════════════════════════════════════════════════════════════
SUMMARY BY CATEGORY
════════════════════════════════════════════════════════════════════════════════════

Category                          Files   Severity    Effort
────────────────────────────────────────────────────────────
PII Exposure                      8       🔴 CRITICAL 2-3h
SQL Injection (f-strings)         7       🔴 CRITICAL 3-4h
JWT Secret Fallback               1       🔴 CRITICAL 15min
Bare Except Clauses               3       🟠 HIGH     1h
Missing Logging                   112     🟡 MEDIUM   4-5h
Missing Timeouts                  5-7     🟡 MEDIUM   1h
Print Statements                  ~15     🟡 MEDIUM   1h
Missing Auth Checks               3       🟡 MEDIUM   1h
────────────────────────────────────────────────────────────

════════════════════════════════════════════════════════════════════════════════════
