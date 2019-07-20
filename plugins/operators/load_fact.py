from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 create_table_sql="",
                 insert_table_sql="",
                 mode="",
                 target_table="",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.create_table_sql = create_table_sql
        self.insert_table_sql = insert_table_sql
        self.mode = mode
        self.target_table = target_table

    def execute(self):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Create fact table")
        redshift.run(format(self.create_table_sql))

        self.log.info('Insert fact table')

        if self.mode == "append":
            insert_sql = f"INSERT INTO {self.target_table} {self.insert_table_sql}"
        else:
            insert_sql = f"DELETE FROM {self.target_table}; INSERT INTO {self.target_table} {self.insert_table_sql}"
        self.log.info("Command is " + insert_sql)
        redshift.run(insert_sql)
