from api.video_stats import get_playlist_id, get_video_id, get_videos_details, save_to_json
from datawarehouse.dwh import staging_table, core_table
from airflow import DAG
import pendulum
from datetime import datetime, timedelta

local_tz = pendulum.timezone("Europe/Budapest")

#default args
default_args = {

    "owner" : "Engineer_Eyad",
    "depends_on_past" : False,
    "email_on_failure" : False,
    "email_on_retry" : False,
    "email" : "Engineer_Eyad@eng.com",
    "max_active_runs" : 1,
    "dagrun_timeout" : timedelta(hours=1),
    "start_date" : datetime(2026, 1, 1, tzinfo=local_tz),


}

with DAG(
    dag_id="produce_json",
    default_args=default_args,
    description="DAG to extract the raw data from youtube API and produce a JSON file with it",
    schedule='0 14 * * *',
    catchup=False,

) as dag:
    
    #Define the tasks
    playlist_id = get_playlist_id()
    video_ids = get_video_id(playlist_id)
    extract_data = get_videos_details(video_ids)
    save_to_json_task = save_to_json(extract_data)

    #Define the dependencies
    playlist_id >> video_ids >> extract_data >> save_to_json_task


with DAG(
    dag_id="Updating_Database",
    default_args=default_args,
    description="Process the JSON file and insert the data into staging schema then convert into the core schema",
    schedule='0 15 * * *',
    catchup=False,

) as dag:
    
    #Define the tasks
    update_staging = staging_table()
    update_core = core_table()

    #Define the dependencies
    update_staging >> update_core

