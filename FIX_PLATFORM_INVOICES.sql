-- Create platform_invoices table if not exists
CREATE TABLE IF NOT EXISTS public.platform_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES public.merchants(id),
    invoice_number TEXT UNIQUE NOT NULL,
    invoice_date DATE,
    due_date DATE,
    period_start DATE,
    period_end DATE,
    total_sales_amount DECIMAL(10, 2),
    platform_commission DECIMAL(10, 2),
    tax_amount DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    currency TEXT DEFAULT 'MAD',
    status TEXT DEFAULT 'pending', -- pending, sent, paid, overdue, cancelled
    payment_method TEXT,
    payment_reference TEXT,
    paid_at TIMESTAMP WITH TIME ZONE,
    pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create invoice_line_items table if not exists
CREATE TABLE IF NOT EXISTS public.invoice_line_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES public.platform_invoices(id) ON DELETE CASCADE,
    sale_id UUID REFERENCES public.sales(id),
    description TEXT,
    sale_date DATE,
    sale_amount DECIMAL(10, 2),
    commission_rate DECIMAL(5, 2),
    commission_amount DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create refresh_materialized_view function
CREATE OR REPLACE FUNCTION public.refresh_materialized_view(view_name text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('REFRESH MATERIALIZED VIEW public.%I', view_name);
EXCEPTION
    WHEN OTHERS THEN
        -- If it's not a materialized view, try to refresh it as a regular view (no-op)
        NULL;
END;
$$;

-- Create gateway_statistics materialized view if not exists (mock for now)
CREATE TABLE IF NOT EXISTS public.gateway_statistics (
    gateway TEXT,
    total_transactions INTEGER,
    successful_transactions INTEGER,
    failed_transactions INTEGER,
    success_rate DECIMAL(5, 2),
    total_amount_processed DECIMAL(15, 2),
    total_fees_paid DECIMAL(15, 2),
    avg_completion_time_seconds DECIMAL(5, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Note: Real materialized view would depend on transaction tables

-- Fix missing columns in platform_invoices if table exists but columns missing
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'platform_invoices' AND column_name = 'invoice_date') THEN
        ALTER TABLE public.platform_invoices ADD COLUMN invoice_date DATE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'platform_invoices' AND column_name = 'due_date') THEN
        ALTER TABLE public.platform_invoices ADD COLUMN due_date DATE;
    END IF;
END $$;
