from datetime import datetime, timedelta
# import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'gil',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False
}

# Using the context manager allows me not to duplicate the dag parameter in each operator
with DAG('redshift_ETL_dag',
         default_args=default_args,
         description='Load and transform data in Redshift with Airflow',
         catchup=False,
         schedule_interval='0 * * * *'
         ) as dag:

    start_operator = DummyOperator(task_id='Begin_execution')

    stage_events_to_redshift = StageToRedshiftOperator(
        task_id='Stage_events',
        table="staging_events",
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        file_typ="json",
        s3_bucket="udacity-dend",
        s3_key="log_data",
        sql=SqlQueries.create_staging_events_table
    )

    stage_songs_to_redshift = StageToRedshiftOperator(
        task_id='Stage_songs',
        table="staging_songs",
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        file_typ="json",
        s3_bucket="udacity-dend",
        s3_key="song_data",
        sql=SqlQueries.create_staging_songs_table
    )

    load_songplays_table = LoadFactOperator(
        task_id='Load_songplays_fact_table',
        redshift_conn_id="redshift",
        create_table_sql=SqlQueries.create_songplays_table,
        insert_table_sql=SqlQueries.insert_songplay_table,
        mode="append",
        target_table="songplays"
    )

    load_user_dimension_table = LoadDimensionOperator(
        task_id='Load_user_dim_table',
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        create_table_sql=SqlQueries.create_users_table,
        insert_table_sql=SqlQueries.insert_user_table,
        mode="overwrite",
        target_table="users"
    )

    load_song_dimension_table = LoadDimensionOperator(
        task_id='Load_song_dim_table',
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        create_table_sql=SqlQueries.create_songs_table,
        insert_table_sql=SqlQueries.insert_song_table,
        mode="overwrite",
        target_table="songs"
    )

    load_artist_dimension_table = LoadDimensionOperator(
        task_id='Load_artist_dim_table',
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        create_table_sql=SqlQueries.create_artists_table,
        insert_table_sql=SqlQueries.insert_artist_table,
        mode="overwrite",
        target_table="artists"
    )

    load_time_dimension_table = LoadDimensionOperator(
        task_id='Load_time_dim_table',
        redshift_conn_id="redshift",
        aws_credentials_id="aws_credentials",
        create_table_sql=SqlQueries.create_times_table,
        insert_table_sql=SqlQueries.insert_time_table,
        mode="overwrite",
        target_table="time"
    )

    run_quality_checks = DataQualityOperator(
        task_id='Run_data_quality_checks',
        redshift_conn_id="redshift",
        table_name="songplays"
    )

    end_operator = DummyOperator(task_id='Stop_execution')

# Make graph
start_operator >> [stage_events_to_redshift, stage_songs_to_redshift]
[stage_events_to_redshift, stage_songs_to_redshift] >> load_songplays_table
load_songplays_table >> [load_artist_dimension_table, load_song_dimension_table, load_time_dimension_table,
                         load_user_dimension_table]
[load_artist_dimension_table, load_song_dimension_table, load_time_dimension_table,
 load_user_dimension_table] >> run_quality_checks
run_quality_checks >> end_operator
