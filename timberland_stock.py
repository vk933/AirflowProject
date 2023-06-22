from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
#import pandas as pd


default_args={
        'owner':'Ranga',
        'start_date':datetime(2023,5,5),
        'retries':3,
        'retry_delay':timedelta(minutes=5)
        }

timberland_stock= DAG('timberland_stock',
          default_args=default_args,
          description='timberland_stock',
          schedule_interval='* * * * *',
          catchup=False,
          tags=['example,helloworld']
          )        

# Task 1: Dummy Operator to start the task
task1 = DummyOperator(task_id='start_task', dag=timberland_stock)

# Task 2: Run Spark job to read CSV and send output file
def run_spark_job():
    # Read CSV file using Spark and perform required processing
    # Save the output file to /root/airflow/outputfiles/

    # Example Spark job code:
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.appName("AirflowProject").getOrCreate()
    
    # Read CSV file
    csv_data = spark.read.option("header" , True).csv("/root/airflow/inputfiles/timberland_stock.csv")
    csv_data.createOrReplaceTempView("mytable")
    Peak_High_Price_Date = spark.sql("select Date from mytable where High = (select max(High) from mytable)")
    Mean_Of_Close_Column = spark.sql("select avg(Close) as mean_of_column from mytable")
    Max_of_Volume_Column = spark.sql("select max(Volume) as max_of_volume from mytable")
    Min_of_Volume_Column = spark.sql("select min(Volume) as min_of_volume from mytable")
    No_Of_days = spark.sql("SELECT COUNT(*) AS count_lower_than_60 FROM mytable WHERE Close < 60")
    percentage = spark.sql("SELECT (COUNT(CASE WHEN High > 80 THEN 1 END) / COUNT(*)) * 100 AS percentage_high_above_80 FROM mytable")
    Pearson_Correlation  = spark.sql("SELECT corr(High, Volume) AS correlation FROM mytable")
    Max_High_Year = spark.sql("""SELECT YEAR(Date) AS Year, MAX(CAST(High AS DOUBLE)) AS max_high FROM mytable GROUP BY Year ORDER BY Year""")
    Avg_Close_For_Each_Month = spark.sql("""SELECT YEAR(Date) AS Year, MONTH(Date) AS Month, AVG(Close) AS AvgClose FROM mytable GROUP BY Year, Month ORDER BY Year, Month""")

    # Save output file
    Peak_High_Price_Date.write.csv('/root/airflow/outputfiles/Peak_High_Price_Date.csv', mode='overwrite', header=True)

    Mean_Of_Close_Column.write.csv('/root/airflow/outputfiles/Mean_Of_Close_Column.csv', mode='overwrite', header=True)

    Max_of_Volume_Column.write.csv('/root/airflow/outputfiles/Max_of_Volume_Column.csv', mode='overwrite', header=True)

    Min_of_Volume_Column.write.csv('/root/airflow/outputfiles/Min_of_Volume_Column.csv', mode='overwrite', header=True)

    No_Of_days.write.csv('/root/airflow/outputfiles/No_Of_days.csv', mode='overwrite', header=True)

    percentage.write.csv('/root/airflow/outputfiles/percentage.csv', mode='overwrite', header=True)

    Pearson_Correlation.write.csv('/root/airflow/outputfiles/Pearson_Correlation.csv', mode='overwrite', header=True)

    Max_High_Year.write.csv('/root/airflow/outputfiles/Max_High_Year.csv', mode='overwrite', header=True)

    Avg_Close_For_Each_Month.write.csv('/root/airflow/outputfiles/Avg_Close_For_Each_Month.csv', mode='overwrite', header=True)




task2 = PythonOperator(
    task_id='run_spark_job',
    python_callable=run_spark_job,
    dag=timberland_stock
)

# Task 3: Dummy Operator to end the task
task3 = DummyOperator(task_id='end_task',dag=timberland_stock)



# Define task dependencies
task1 >> task2 >> task3
