-- Update conversions to set influencer_id from tracking_links where it is null
-- This fixes the issue where revenue was not being attributed to influencers because the direct link was missing
UPDATE conversions
SET influencer_id = tracking_links.influencer_id
FROM tracking_links
WHERE conversions.tracking_link_id = tracking_links.id
AND conversions.influencer_id IS NULL;
