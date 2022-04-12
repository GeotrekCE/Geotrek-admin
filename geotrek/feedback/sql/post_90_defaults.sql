-- Report
---------
-- email
ALTER TABLE feedback_report ALTER COLUMN comment SET DEFAULT '';
-- activity
-- category
-- problem_magnitude
-- status
-- geom
-- related_trek
-- created_in_suricate
ALTER TABLE feedback_report ALTER COLUMN uid SET DEFAULT gen_random_uuid();
ALTER TABLE feedback_report ALTER COLUMN locked SET DEFAULT False;
ALTER TABLE feedback_report ALTER COLUMN origin SET DEFAULT 'unknown';
-- last_updated_in_suricate
ALTER TABLE feedback_report ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE feedback_report ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE feedback_report ALTER COLUMN deleted SET DEFAULT False;


-- ReportActivity
-----------------
-- label
-- suricate_id


-- ReportCategory
-----------------
-- label
-- suricate_id


-- ReportStatus
---------------
-- label
-- suricate_id


-- ReportProblemMagnitude
-------------------------
-- label
-- suricate_id
-- suricate_label


-- AttachedMessage
------------------
ALTER TABLE feedback_attachedmessage ALTER COLUMN "date" SET DEFAULT now();
ALTER TABLE feedback_attachedmessage ALTER COLUMN author SET DEFAULT '';
ALTER TABLE feedback_attachedmessage ALTER COLUMN content SET DEFAULT '';
-- suricate_id
-- type
-- report
