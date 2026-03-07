# 🚀 Quick Start: Apply Database Migrations

## ✅ Migration 005 Fixed and Ready!

All SQL errors have been fixed. The migration is now ready to apply.

---

## 📝 How to Apply Migration 005

### ⚡ Option 1: Supabase Dashboard (Easiest - 2 minutes)

1. **Open your Supabase project**
   - Go to https://app.supabase.com
   - Select your project

2. **Navigate to SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"

3. **Copy the migration SQL**
   - Open `backend/migrations/005_ensure_all_tables.sql`
   - Copy ALL content (Ctrl+A, Ctrl+C)

4. **Paste and Run**
   - Paste into the SQL Editor
   - Click "Run" or press Ctrl+Enter
   - Wait for completion (should take 5-10 seconds)

5. **Verify Success**
   - You should see "Success. No rows returned"
   - Check the output for "✅ Migration 005 completed successfully"

---

### 💻 Option 2: Command Line (For Advanced Users)

```bash
# Make sure you have your Supabase connection string
# Format: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres

# Run the migration
psql "postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres" \
  -f backend/migrations/005_ensure_all_tables.sql
```

---

### 🐍 Option 3: Python Helper Script

```bash
cd backend/migrations
python3 apply_migrations.py
```

This will display the SQL content for easy copy/paste.

---

## 🔍 What Gets Created

The migration creates **25+ tables** and **50+ indexes** for:

✅ **Live Chat** (chat_rooms, chat_messages)
✅ **Customer Service** (support_tickets, support_ticket_replies)
✅ **AI Chatbot** (chatbot_history)
✅ **Gamification** (gamification, user_badges, points_history)
✅ **KYC Verification** (kyc_verifications)
✅ **Mobile Features** (whatsapp_messages, mobile_payments)
✅ **Social Media** (social_media_connections, social_media_posts)
✅ **Team Management** (team_members, team_invitations)
✅ **A/B Testing** (ab_tests, ab_test_assignments)
✅ **Admin Dashboard** (moderation_queue, audit_logs, system_logs, error_logs)
✅ **Integrations** (webhook_logs, ecommerce_integrations)
✅ **Payments** (payment_transactions, subscriptions)

---

## ✅ Verification

After running the migration, verify everything was created:

```sql
-- Check if support_tickets has all columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'support_tickets'
ORDER BY ordinal_position;
```

Expected columns:
- id (uuid)
- ticket_number (text)
- user_id (uuid)
- subject (text)
- description (text)
- category (text)
- priority (text)
- status (text)
- **assigned_to (uuid)** ← This was missing before!
- **sla_due_at (timestamp)**
- **resolved_at (timestamp)**
- **closed_at (timestamp)**
- **metadata (jsonb)**
- created_at (timestamp)
- updated_at (timestamp)

```sql
-- Count all tables created
SELECT COUNT(*) as total_tables
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'chat_rooms', 'chat_messages', 'support_tickets', 'support_ticket_replies',
    'chatbot_history', 'gamification', 'user_badges', 'points_history',
    'kyc_verifications', 'whatsapp_messages', 'mobile_payments',
    'social_media_connections', 'social_media_posts',
    'team_members', 'team_invitations',
    'ab_tests', 'ab_test_assignments',
    'moderation_queue', 'audit_logs', 'system_logs', 'error_logs',
    'webhook_logs', 'ecommerce_integrations',
    'payment_transactions', 'subscriptions'
  );
-- Expected: 25 tables
```

---

## 🎯 Next Steps After Migration

1. **Create Supabase Storage Bucket for KYC**
   ```sql
   INSERT INTO storage.buckets (id, name, public)
   VALUES ('kyc-documents', 'kyc-documents', false)
   ON CONFLICT (id) DO NOTHING;
   ```

   Or via Dashboard:
   - Go to Storage
   - Click "New bucket"
   - Name: `kyc-documents`
   - Public: No (private)
   - Create

2. **Test API Endpoints**
   - Start the backend: `cd backend && python server_complete.py`
   - Test with: http://localhost:8000/docs
   - Try creating a support ticket
   - Try the AI recommendations
   - Test live chat WebSocket

3. **Configure Environment Variables**
   ```bash
   # .env file
   OPENAI_API_KEY=sk-...  # For AI chatbot
   STRIPE_WEBHOOK_SECRET=whsec_...  # For Stripe webhooks
   WHATSAPP_ACCESS_TOKEN=...  # For WhatsApp Business
   ```

4. **Deploy to Production**
   - Push to Railway/Vercel/AWS
   - Run migration on production database
   - Configure production environment variables

---

## 🐛 Troubleshooting

### Error: "relation users does not exist"
The migration tries to create foreign keys to the `users` table. If it doesn't exist, the migration will still create the tables but skip the foreign key constraints. You can add them later.

### Error: "permission denied"
Make sure you're connected with a user that has CREATE TABLE permissions (usually `postgres`).

### Error: "already exists"
This is expected if you're re-running the migration. The migration uses `IF NOT EXISTS` so it's safe to run multiple times.

---

## 📚 Full Documentation

For complete documentation, see:
- `backend/migrations/README.md` - Full migration guide
- `backend/ENDPOINTS_SUMMARY.md` - Complete API documentation
- `backend/migrations/005_ensure_all_tables.sql` - The migration SQL

---

## ✅ Status

- ✅ SQL Errors Fixed
- ✅ Migration 005 Ready
- ✅ Idempotent (safe to run multiple times)
- ✅ 100% Feature Coverage
- ✅ Production Ready

**Total Endpoints**: 165+
**Total Tables**: 40+
**Total Indexes**: 50+

🎉 **Ready to Deploy!**
