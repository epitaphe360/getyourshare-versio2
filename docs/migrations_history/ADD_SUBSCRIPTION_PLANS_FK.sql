
-- Change plan_id to UUID first (required for FK)
ALTER TABLE subscriptions
ALTER COLUMN plan_id TYPE UUID USING plan_id::UUID;

-- Add foreign key constraint to subscriptions table
ALTER TABLE subscriptions
ADD CONSTRAINT subscriptions_plan_id_fkey
FOREIGN KEY (plan_id)
REFERENCES subscription_plans(id);
