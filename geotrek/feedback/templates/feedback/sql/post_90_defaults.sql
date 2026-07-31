-- Report
---------
ALTER TABLE feedback_report ALTER COLUMN email SET DEFAULT '';
ALTER TABLE feedback_report ALTER COLUMN comment SET DEFAULT '';
-- activity
-- category
-- problem_magnitude
-- status
-- geom
-- related_trek
-- created_in_suricate
-- external_uuid
ALTER TABLE feedback_report ALTER COLUMN uuid SET DEFAULT gen_random_uuid();
ALTER TABLE feedback_report ALTER COLUMN eid SET DEFAULT '';
ALTER TABLE feedback_report ALTER COLUMN locked SET DEFAULT False;
ALTER TABLE feedback_report ALTER COLUMN origin SET DEFAULT 'unknown';
-- last_updated_in_suricate
-- current_user
-- assigned_handler
ALTER TABLE feedback_report ALTER COLUMN sync_errors SET DEFAULT 0;
ALTER TABLE feedback_report ALTER COLUMN mail_errors SET DEFAULT 0;
ALTER TABLE feedback_report ALTER COLUMN deleted SET DEFAULT False;

-- AttachedMessage
------------------
ALTER TABLE feedback_attachedmessage ALTER COLUMN author SET DEFAULT '';
ALTER TABLE feedback_attachedmessage ALTER COLUMN content SET DEFAULT '';
-- suricate_id
-- type
-- report
