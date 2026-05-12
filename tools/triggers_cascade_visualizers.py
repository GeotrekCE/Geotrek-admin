"""
These scripts can be used to visualize cascading SQL triggers on the core_path table and their corresponding UPDATE/INSERT events for debugging purposes.

We need to insert some execution logging into a dedicated database table, then we extract the logging information and turn it into Matploblib graphs.

Step 0 : Create two logging tables 'trigger_timeline', 'trigger_events_timeline' with SQL code given below

# Visualizing trigger cascade

Step 1 - Add logging to every trigger start, thanks to the following INSERT query (change 'trigger_name' accordingly)
         INSERT INTO trigger_timeline (trigger_id, tgr_depth, created_at) VALUES ('trigger_name', pg_trigger_depth(), clock_timestamp());
Step 2 - Run the code you need to debug, retrieve the logging information from database, and turn it into a Python list of tuples of the following format:
        [(trigger_name, pg_trigger_depth, clock_timestamp)]
Step 3 - Run plot_trigger_timeline function below


# Visualizing INSERT/UPDATE events

Step 1 - Create four triggers with the SQL code given below : 'log_before_trigger_tgr_update', 'log_before_trigger_tgr_insert', 'log_after_trigger_tgr_update', 'log_after_trigger_tgr_insert'
Step 2 - Retrieve the logging information and turn it into 4 Python lists of tuples of the following format:
         [(path_id, pg_trigger_depth, clock_timestamp)]
Step 3 - Run plot_trigger_timeline_paths function below


# Bonus : visualize precise line execution

You can use the same concept to INSERT logging at any line in your triggers, be creative with the labels and logged data.







####################################

        SQL setup : Add to file pre_10_cleanup.sql

####################################


CREATE TABLE IF NOT EXISTS trigger_timeline(
    id SERIAL PRIMARY KEY,
    trigger_id VARCHAR(100),
    tgr_depth INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

TRUNCATE trigger_count;

CREATE TABLE IF NOT EXISTS trigger_events_timeline(
    id SERIAL PRIMARY KEY,
    trigger_type VARCHAR(100),
    path_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tgr_depth INTEGER
);

TRUNCATE trigger_logs;


CREATE FUNCTION {{ schema_geotrek }}.log_after_trigger_update() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('AFTER_UPDATE', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_after_trigger_tgr_update
AFTER UPDATE OF geom ON core_path
FOR EACH ROW EXECUTE PROCEDURE log_after_trigger_update();

CREATE FUNCTION {{ schema_geotrek }}.log_before_trigger_update() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('BEFORE_UPDATE', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_before_trigger_tgr_update
BEFORE UPDATE OF geom ON core_path
FOR EACH ROW EXECUTE PROCEDURE log_before_trigger_update();

CREATE FUNCTION {{ schema_geotrek }}.log_after_trigger_insert() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('AFTER_INSERT', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_after_trigger_tgr_insert
AFTER INSERT ON core_path
FOR EACH ROW EXECUTE PROCEDURE log_after_trigger_insert();

CREATE FUNCTION {{ schema_geotrek }}.log_before_trigger_insert() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('BEFORE_INSERT', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_before_trigger_tgr_insert
BEFORE INSERT ON core_path
FOR EACH ROW EXECUTE PROCEDURE log_before_trigger_insert();










####################################

        First script : Visualizing trigger cascade

####################################

"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def plot_trigger_timeline(data):
    trigger_names = list(set(name for name, _, _ in data))
    trigger_names.sort()

    # Create color map for triggers
    colors = [plt.cm.tab20(i / (len(trigger_names) - 1)) for i in range(len(trigger_names))]
    color_map = dict(zip(trigger_names, colors))
    # Create figure and axis with larger size
    plt.figure(figsize=(15, 10))

    # Plot points for each trigger type
    for trigger in trigger_names:
        # Filter data for this trigger
        trigger_data = [(name, depth, time) for name, depth, time in data if name == trigger]

        # Extract x and y coordinates
        times = [t for _, _, t in trigger_data]
        depths = [depth for _, depth, _ in trigger_data]

        # Plot scatter points
        plt.scatter(times, depths, label=trigger, alpha=0.6, s=100, color=color_map[trigger])

    # Customize the plot
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))
    plt.gcf().autofmt_xdate()  # Rotate and align the tick labels

    # Add labels and title
    plt.xlabel('Time')
    plt.ylabel('Trigger Depth')
    plt.title('Trigger Events Timeline')

    # Add legend to the right side of the plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    return plt

# Example data:
data = [
    ('paths_snap_extremities', 1, datetime.datetime(2025, 1, 15, 9, 27, 0, 609516)),
    ('elevation_path_iu', 1, datetime.datetime(2025, 1, 15, 9, 27, 0, 611045)),
    ('paths_topology_intersect_split', 1, datetime.datetime(2025, 1, 15, 9, 27, 0, 611428)),
    ('paths_snap_extremities', 2, datetime.datetime(2025, 1, 15, 9, 27, 0, 612682)),
    ('elevation_path_iu', 2, datetime.datetime(2025, 1, 15, 9, 27, 0, 613426)),
    ('paths_topology_intersect_split', 2, datetime.datetime(2025, 1, 15, 9, 27, 0, 613676)),
    ('paths_snap_extremities', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 614584)),
    ('elevation_path_iu', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 615308)),
    ('paths_topology_intersect_split', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 615541)),
    ('update_topology_geom_when_path_changes', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 616272)),
    ('set_pgrouting_values_to_null', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 616513)),
    ('paths_snap_extremities', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 617180)),
    ('elevation_path_iu', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 617978)),
    ('paths_topology_intersect_split', 3, datetime.datetime(2025, 1, 15, 9, 27, 0, 618223)),
    ('paths_snap_extremities', 4, datetime.datetime(2025, 1, 15, 9, 27, 0, 619479)),
    ('elevation_path_iu', 4, datetime.datetime(2025, 1, 15, 9, 27, 0, 620149)),
    ('paths_topology_intersect_split', 4, datetime.datetime(2025, 1, 15, 9, 27, 0, 620365)),
]
# Create and display the plot
plt = plot_trigger_timeline(data)
plt.show()

"""










####################################

        Second script : Visualizing INSERT/UPDATE events

####################################
"""

import matplotlib.pyplot as plt
import datetime


def plot_trigger_timeline_paths(data, legend, ytext, color, create_new_figure=True):
    # Extract data for plotting
    identifiers = [item[0] for item in data]
    depths = [item[1] for item in data]
    timestamps = [item[2] for item in data]

    # Create the plot only if it's the first dataset
    if create_new_figure:
        plt.figure(figsize=(10, 6))

    # Plot points
    plt.scatter(timestamps, depths, color=color, label=legend)

    # Add labels for each point
    for i, txt in enumerate(identifiers):
        plt.annotate(txt, (timestamps[i], depths[i]),
                     xytext=(5, ytext), textcoords='offset points')

    # Customize the plot (only needed once)
    if create_new_figure:
        plt.xlabel('Timestamp')
        plt.ylabel('PG Depth')
        plt.title('PG Depth vs Timestamp')
        # Format x-axis to show time nicely
        plt.gcf().autofmt_xdate()
        # Add grid for better readability
        plt.grid(True, linestyle='--', alpha=0.7)

    return plt

# Example data
before_update = [
    ('207', 2, datetime.datetime(2025, 1, 21, 13, 23, 42, 254063)),
    ('211', 3, datetime.datetime(2025, 1, 21, 13, 23, 42, 256176)),
    ('208', 4, datetime.datetime(2025, 1, 21, 13, 23, 42, 260836)),
    ('212', 5, datetime.datetime(2025, 1, 21, 13, 23, 42, 263313)),
    ('210', 6, datetime.datetime(2025, 1, 21, 13, 23, 42, 266196)),
    ('213', 7, datetime.datetime(2025, 1, 21, 13, 23, 42, 267283))
]
after_update = [
    ('207', 2, datetime.datetime(2025, 1, 21, 13, 23, 42, 255288)),
    ('211', 3, datetime.datetime(2025, 1, 21, 13, 23, 42, 257131)),
    ('208', 4, datetime.datetime(2025, 1, 21, 13, 23, 42, 262106)),
    ('212', 5, datetime.datetime(2025, 1, 21, 13, 23, 42, 264357)),
    ('210', 6, datetime.datetime(2025, 1, 21, 13, 23, 42, 266676)),
    ('213', 7, datetime.datetime(2025, 1, 21, 13, 23, 42, 267818))
]
before_insert = [
    ('211', 1, datetime.datetime(2025, 1, 21, 13, 23, 42, 250029)),
    ('217', 2, datetime.datetime(2025, 1, 21, 13, 23, 42, 284971)),
    ('212', 3, datetime.datetime(2025, 1, 21, 13, 23, 42, 258557)),
    ('216', 4, datetime.datetime(2025, 1, 21, 13, 23, 42, 277235)),
    ('213', 5, datetime.datetime(2025, 1, 21, 13, 23, 42, 265357)),
    ('215', 6, datetime.datetime(2025, 1, 21, 13, 23, 42, 271298)),
]
after_insert = [
    ('211', 1, datetime.datetime(2025, 1, 21, 13, 23, 42, 252373)),
    ('217', 2, datetime.datetime(2025, 1, 21, 13, 23, 42, 285437)),
    ('212', 3, datetime.datetime(2025, 1, 21, 13, 23, 42, 259562)),
    ('216', 4, datetime.datetime(2025, 1, 21, 13, 23, 42, 277671)),
    ('213', 5, datetime.datetime(2025, 1, 21, 13, 23, 42, 265752)),
    ('215', 6, datetime.datetime(2025, 1, 21, 13, 23, 42, 271726)),
]

# Plot the first dataset (creates the figure)
plt = plot_trigger_timeline_paths(before_update, 'before_update', 5, 'pink', create_new_figure=True)

# Plot the second dataset (adds to existing figure)
plt = plot_trigger_timeline_paths(before_insert, 'before_insert', 5, 'green', create_new_figure=False)
plt = plot_trigger_timeline_paths(after_insert, 'after_insert', -15, 'blue', create_new_figure=False)
plt = plot_trigger_timeline_paths(after_update, 'after_update', -15, 'red', create_new_figure=False)
# Add legend
plt.legend()

# Adjust layout to prevent label cutoff (do this only once at the end)
plt.tight_layout()

# Show the plot
plt.show()
