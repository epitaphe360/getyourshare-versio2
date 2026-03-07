# Audit Fixes Report

## Overview
This report details the fixes applied to the backend to resolve issues identified by the comprehensive audit script.

## Issues Resolved

### 1. Authentication Key Error
- **Issue**: `KeyError: 'sub'` in `backend/server.py`.
- **Cause**: The JWT payload returned by `get_current_user_from_cookie` uses `id` instead of `sub`.
- **Fix**: Replaced all occurrences of `payload["sub"]` with `payload["id"]` in `backend/server.py`.

### 2. Subscription Usage Stats Error
- **Issue**: `Failed to get usage stats` (404 Not Found).
- **Cause**: `get_usage_stats` in `backend/subscription_endpoints.py` raised a 404 if no subscription was found in the database, whereas `get_current_subscription` returned a default free plan.
- **Fix**: Updated `get_usage_stats` to return default usage limits (Freemium/Free) when no active subscription is found, consistent with other endpoints.

### 3. Messaging System Schema Mismatches
- **Issue**: `Failed to send message` and `Failed to read message details`.
- **Causes**:
    - `conversations` table uses `participant_ids` (array) instead of `user1_id`/`user2_id`.
    - `messages` table does not have a `sender_type` column.
    - `users` table does not have a `username` column (uses `full_name` and `company_name`).
- **Fixes**:
    - Updated `send_message` in `backend/server.py` to query `conversations` using `participant_ids` containment check.
    - Removed `sender_type` from the insert payload in `send_message`.
    - Updated `get_conversations` and `get_messages` to select `full_name` instead of `username` and use it for display names.

## Verification
The audit script `backend/test_comprehensive_audit.py` now passes all tests:
- ✅ Authentication (Merchant & Influencer)
- ✅ Subscriptions (Plans, Current, Usage)
- ✅ Products & Services Listing
- ✅ Messaging (Send, Inbox, Details)

## Next Steps
- Ensure frontend dashboards are updated to reflect these API changes if they were relying on the old schema (e.g. `username` field).
- Monitor `participant_ids` usage in other parts of the application if any.
