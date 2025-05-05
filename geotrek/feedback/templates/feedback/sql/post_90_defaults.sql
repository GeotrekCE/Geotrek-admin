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
ALTER TABLE feedback_report ALTER COLUMN sync_errors SET DEFAULT 0;
ALTER TABLE feedback_report ALTER COLUMN mail_errors SET DEFAULT 0;
ALTER TABLE feedback_report ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE feedback_report ALTER COLUMN date_update SET DEFAULT now();
ALTER TABLE feedback_report ALTER COLUMN deleted SET DEFAULT False;
ALTER TABLE feedback_report ALTER COLUMN provider SET DEFAULT '';


-- ReportActivity
-----------------
-- label
-- suricate_id
ALTER TABLE feedback_reportactivity ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE feedback_reportactivity ALTER COLUMN date_update SET DEFAULT now();


-- ReportCategory
-----------------
-- label
-- suricate_id
ALTER TABLE feedback_reportcategory ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE feedback_reportcategory ALTER COLUMN date_update SET DEFAULT now();

-- ReportStatus
---------------
-- label
-- suricate_id
ALTER TABLE feedback_reportstatus ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE feedback_reportstatus ALTER COLUMN date_update SET DEFAULT now();


-- ReportProblemMagnitude
-------------------------
-- label
-- suricate_id
-- suricate_label
ALTER TABLE feedback_reportproblemmagnitude ALTER COLUMN date_insert SET DEFAULT now();
ALTER TABLE feedback_reportproblemmagnitude ALTER COLUMN date_update SET DEFAULT now();


-- AttachedMessage
------------------
ALTER TABLE feedback_attachedmessage ALTER COLUMN "date" SET DEFAULT now();
ALTER TABLE feedback_attachedmessage ALTER COLUMN author SET DEFAULT '';
ALTER TABLE feedback_attachedmessage ALTER COLUMN content SET DEFAULT '';
-- suricate_id
-- type
-- report
