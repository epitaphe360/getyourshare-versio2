# Database Migrations Guide

## 📋 Migration Files

### Migration 003 - Add Missing Features Tables
**File**: `003_add_missing_features_tables.sql`
**Status**: Initial migration (use 005 instead)
**Description**: Creates all new tables for 100% feature coverage

### Migration 004 - Fix Support Tickets Columns
**File**: `004_fix_support_tickets_columns.sql`
**Status**: Patch migration
**Description**: Adds missing columns to support_tickets table if it already exists

### Migration 005 - Ensure All Tables (RECOMMENDED)
**File**: `005_ensure_all_tables.sql`
**Status**: **✅ RECOMMENDED - Use this one**
**Description**: Idempotent migration that creates all tables with proper columns. Safe to run multiple times.

---

## 🚀 How to Apply Migrations

### Option 1: Via Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the content of `005_ensure_all_tables.sql`
4. Click **Run**
5. Check for success messages

### Option 2: Via psql Command Line

```bash
# Connect to your Supabase database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run the migration
\i backend/migrations/005_ensure_all_tables.sql

# Or run directly
psql "postgresql://..." -f backend/migrations/005_ensure_all_tables.sql
```

### Option 3: Via Python Script

```bash
cd backend/migrations
python apply_migrations.py
```

### Option 4: Via Supabase CLI

```bash
# Login to Supabase
supabase login

# Link your project
supabase link --project-ref [YOUR-PROJECT-REF]

# Apply migrations
supabase db push
```

---

## 🔍 What Gets Created

### Tables (25+)

#### Live Chat
- `chat_rooms` - Chat room management
- `chat_messages` - Message history

#### Customer Service
- `support_tickets` - Support tickets
- `support_ticket_replies` - Ticket conversations

#### AI Features
- `chatbot_history` - AI chatbot conversations

#### Gamification
- `gamification` - User points and levels
- `user_badges` - Earned badges
- `points_history` - Points transactions

#### KYC
- `kyc_verifications` - Identity verification

#### Mobile
- `whatsapp_messages` - WhatsApp Business messages
- `mobile_payments` - Morocco mobile payments

#### Social Media
- `social_media_connections` - Platform connections
- `social_media_posts` - Published posts

#### Team Management
- `team_members` - Team collaboration
- `team_invitations` - Team invitations

#### Advanced Analytics
- `ab_tests` - A/B testing framework
- `ab_test_assignments` - User assignments

#### Admin Dashboard
- `moderation_queue` - Content moderation
- `audit_logs` - System audit trail
- `system_logs` - System logs
- `error_logs` - Error tracking

#### Integrations
- `webhook_logs` - Webhook events
- `ecommerce_integrations` - E-commerce platforms
- `payment_transactions` - Payment history
- `subscriptions` - Recurring payments

### Indexes (50+)

All tables have optimized indexes for:
- Primary lookups (user_id, status)
- Date-based queries (created_at DESC)
- Foreign key relationships
- Unique constraints

---

## ⚠️ Important Notes

### Safe to Run Multiple Times

Migration 005 is **idempotent** - it uses `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`, so it's safe to run multiple times without errors.

### Foreign Key References

Some tables have foreign key references to `users(id)`. Make sure your `users` table exists before running the migration. If you get foreign key errors:

1. The migration will still create the tables
2. Foreign key constraints will be skipped for non-existent tables
3. You can add them later with `ALTER TABLE`

### Supabase Storage Bucket

For KYC documents, you need to create a storage bucket manually:

**Via Supabase Dashboard:**
1. Go to **Storage**
2. Click **New bucket**
3. Name: `kyc-documents`
4. Public: **No** (private)
5. Click **Create**

**Via SQL:**
```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('kyc-documents', 'kyc-documents', false)
ON CONFLICT (id) DO NOTHING;
```

---

## 🐛 Troubleshooting

### Error: "relation does not exist"

This means a referenced table (like `users`) doesn't exist yet. Either:
- Create the base tables first
- Remove the foreign key constraint temporarily
- The migration will create the table without constraints

### Error: "column already exists"

This is expected if you're re-running migrations. The migration will skip existing columns safely.

### Error: "permission denied"

Make sure you're connected as a user with `CREATE TABLE` permissions (usually `postgres` or admin).

### Error: "database does not exist"

Connect to the correct database. For Supabase, it's usually named `postgres`.

---

## 📊 Verification

After running the migration, verify tables were created:

```sql
-- List all new tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'chat_rooms', 'chat_messages', 'support_tickets',
    'chatbot_history', 'gamification', 'user_badges',
    'kyc_verifications', 'whatsapp_messages', 'mobile_payments',
    'social_media_connections', 'team_members', 'ab_tests',
    'moderation_queue', 'audit_logs', 'webhook_logs'
  )
ORDER BY table_name;

-- Count indexes created
SELECT COUNT(*) as total_indexes
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%';

-- Check support_tickets has all columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'support_tickets'
ORDER BY ordinal_position;
```

---

## 🔄 Rolling Back (if needed)

To remove all tables created by this migration:

```sql
-- WARNING: This will delete all data in these tables!

DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_rooms CASCADE;
DROP TABLE IF EXISTS support_ticket_replies CASCADE;
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS chatbot_history CASCADE;
DROP TABLE IF EXISTS points_history CASCADE;
DROP TABLE IF EXISTS user_badges CASCADE;
DROP TABLE IF EXISTS gamification CASCADE;
DROP TABLE IF EXISTS kyc_verifications CASCADE;
DROP TABLE IF EXISTS whatsapp_messages CASCADE;
DROP TABLE IF EXISTS mobile_payments CASCADE;
DROP TABLE IF EXISTS social_media_posts CASCADE;
DROP TABLE IF EXISTS social_media_connections CASCADE;
DROP TABLE IF EXISTS team_invitations CASCADE;
DROP TABLE IF EXISTS team_members CASCADE;
DROP TABLE IF EXISTS ab_test_assignments CASCADE;
DROP TABLE IF EXISTS ab_tests CASCADE;
DROP TABLE IF EXISTS moderation_queue CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS system_logs CASCADE;
DROP TABLE IF EXISTS error_logs CASCADE;
DROP TABLE IF EXISTS webhook_logs CASCADE;
DROP TABLE IF EXISTS ecommerce_integrations CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS payment_transactions CASCADE;
```

---

## 📝 Next Steps

After applying the migration:

1. ✅ Verify tables were created
2. ✅ Create Supabase storage bucket for KYC
3. ✅ Test API endpoints
4. ✅ Configure environment variables for integrations
5. ✅ Deploy backend to production

---

**Migration Version**: 005
**Last Updated**: 2025-12-08
**Status**: Production Ready ✅
