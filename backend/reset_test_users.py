import os
import sys
sys.path.append(os.getcwd())
from supabase_client import supabase

emails = ["boutique.maroc@getyourshare.com", "hassan.oudrhiri@getyourshare.com"]

print(f"Deleting users: {emails}")

for email in emails:
    # Get User ID
    res = supabase.table('users').select('id').eq('email', email).execute()
    if res.data:
        uid = res.data[0]['id']
        print(f"Found user {email} with ID {uid}. Cleaning up...")
        
        # Find Merchant/Influencer ID
        mid = None
        iid = None
        
        m_res = supabase.table('merchants').select('id').eq('user_id', uid).execute()
        if m_res.data: 
            mid = m_res.data[0]['id']
            print(f"Merchant ID: {mid}")
        else:
            print("Merchant ID not found for user.")
        
        i_res = supabase.table('influencers').select('id').eq('user_id', uid).execute()
        if i_res.data: 
            iid = i_res.data[0]['id']
            print(f"Influencer ID: {iid}")
        
        # Delete Commissions
        if iid:
            supabase.table('commissions').delete().eq('influencer_id', iid).execute()
        supabase.table('commissions').delete().eq('influencer_id', uid).execute()
        
        # Delete Commissions linked to sales of this merchant (if any)
        # We need to find sales first
        sales_ids = []
        s_res = supabase.table('sales').select('id').eq('merchant_id', uid).execute()
        if s_res.data: sales_ids.extend([s['id'] for s in s_res.data])
        
        if mid:
            s_res = supabase.table('sales').select('id').eq('merchant_id', mid).execute()
            if s_res.data: sales_ids.extend([s['id'] for s in s_res.data])
            
        # Also find sales where user is influencer
        s_res = supabase.table('sales').select('id').eq('influencer_id', uid).execute()
        if s_res.data: sales_ids.extend([s['id'] for s in s_res.data])
        
        if iid:
            s_res = supabase.table('sales').select('id').eq('influencer_id', iid).execute()
            if s_res.data: sales_ids.extend([s['id'] for s in s_res.data])

        if sales_ids:
            # Remove duplicates
            sales_ids = list(set(sales_ids))
            # Chunking if too many?
            supabase.table('commissions').delete().in_('sale_id', sales_ids).execute()

        # Delete Subscriptions
        supabase.table('subscriptions').delete().eq('user_id', uid).execute()
        
        # Delete Invoices
        supabase.table('invoices').delete().eq('user_id', uid).execute()
        
        # Delete Affiliate Requests
        try:
            supabase.table('affiliate_requests').delete().eq('influencer_id', uid).execute()
            supabase.table('affiliate_requests').delete().eq('merchant_id', uid).execute()
            if iid: supabase.table('affiliate_requests').delete().eq('influencer_id', iid).execute()
            if mid: supabase.table('affiliate_requests').delete().eq('merchant_id', mid).execute()
        except:
            pass
            
        try:
            supabase.table('affiliation_requests').delete().eq('influencer_id', uid).execute()
            supabase.table('affiliation_requests').delete().eq('merchant_id', uid).execute()
            if iid: supabase.table('affiliation_requests').delete().eq('influencer_id', iid).execute()
            if mid: supabase.table('affiliation_requests').delete().eq('merchant_id', mid).execute()
        except:
            pass
            
        # Delete Messages
        supabase.table('messages').delete().eq('sender_id', uid).execute()
        try:
            supabase.table('messages').delete().eq('receiver_id', uid).execute()
        except:
            pass
        try:
            supabase.table('messages').delete().eq('recipient_id', uid).execute()
        except:
            pass
        
        # Delete Conversations (participants)
        # This is harder if it's many-to-many. Assuming conversation_participants table?
        # Or conversations table has user_id?
        # Let's try deleting from conversations if user_id exists
        try:
            supabase.table('conversations').delete().eq('user1_id', uid).execute()
            supabase.table('conversations').delete().eq('user2_id', uid).execute()
        except:
            pass

        # Delete Product Reviews
        try:
            supabase.table('product_reviews').delete().eq('user_id', uid).execute()
        except:
            pass
            
        # Delete Reviews for products of this merchant
        p_ids = []
        if mid:
            # Get product IDs
            p_res = supabase.table('products').select('id').eq('merchant_id', mid).execute()
            if p_res.data:
                p_ids.extend([p['id'] for p in p_res.data])
        
        # Try with user_id as merchant_id
        p_res = supabase.table('products').select('id').eq('merchant_id', uid).execute()
        if p_res.data:
            p_ids.extend([p['id'] for p in p_res.data])
            
        if p_ids:
            p_ids = list(set(p_ids))
            print(f"Deleting reviews for products: {p_ids}")
            supabase.table('product_reviews').delete().in_('product_id', p_ids).execute()
            
            # Also delete trackable_links for these products
            supabase.table('trackable_links').delete().in_('product_id', p_ids).execute()
            
            # Also delete sales for these products (if any left)
            supabase.table('sales').delete().in_('product_id', p_ids).execute()

        # Delete Sales using User ID if schema links directly to users
        supabase.table('sales').delete().eq('merchant_id', uid).execute()
        supabase.table('sales').delete().eq('influencer_id', uid).execute()
        
        # Also try with Merchant/Influencer ID just in case
        if mid:
            supabase.table('sales').delete().eq('merchant_id', mid).execute()
            supabase.table('products').delete().eq('merchant_id', mid).execute()
        
        if iid:
            supabase.table('sales').delete().eq('influencer_id', iid).execute()
            supabase.table('trackable_links').delete().eq('influencer_id', iid).execute()

        # Try deleting user again
        try:
            supabase.table('users').delete().eq('id', uid).execute()
            print(f"Deleted {email}")
        except Exception as e:
            print(f"Error deleting {email}: {e}")
    else:
        print(f"User {email} not found.")
