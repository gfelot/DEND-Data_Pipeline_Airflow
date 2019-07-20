from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadDimensionOperator(BaseOperator):
    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 aws_credentials_id="",
                 create_table_sql="",
                 insert_table_sql="",
                 mode="",
                 target_table="",
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.create_table_sql = create_table_sql
        self.insert_table_sql = insert_table_sql
        self.mode = mode
        self.target_table = target_table


def execute(self):
    redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

    self.log.info("Creating the respective dimension table in redshift before insert")
    redshift.run(format(self.create_table_sql))

    self.log.info('Insert to the respective dimension table')

    if self.mode == "append":
        insert_sql = f"INSERT INTO {self.target_table} {self.insert_table_sql}"
    else:
        insert_sql = f"DELETE FROM {self.target_table}; INSERT INTO {self.target_table} {self.insert_table_sql}"
    self.log.info("Command is " + insert_sql)
    redshift.run(insert_sql)
