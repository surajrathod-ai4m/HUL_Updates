import psycopg2
from psycopg2 import pool
from psycopg2 import sql
import time
import logging
from io import StringIO

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection parameters
source_db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'ai4m2024',
    'host': 'localhost',
    'port': '5432'
}

target_db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'ai4m2024',
    'host': '192.168.20.135',
    'port': '5432'
}

# Table names
source_table = 'hul_plc_data'
target_table = 'hul_plc_data'

# Create connection pools
source_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **source_db_params)
target_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **target_db_params)

def format_value(value):
    if value is None:
        return r'\N'  # PostgreSQL's representation of NULL
    if isinstance(value, str):
        return value.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
    return str(value)

def transfer_data():
    start_time = time.time()
    source_conn = source_pool.getconn()
    target_conn = target_pool.getconn()
    
    try:
        with source_conn.cursor() as source_cur, target_conn.cursor() as target_cur:
            source_cur.execute("SET timezone TO 'UTC';")
            target_cur.execute("SET timezone TO 'UTC';")
            
            # Fetch data from the source database
            source_cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(source_table)))
            rows = source_cur.fetchall()
            
            if rows:
                # Prepare data for copy
                output = StringIO()
                for row in rows:
                    formatted_row = '\t'.join(format_value(item) for item in row)
                    output.write(formatted_row + '\n')
                output.seek(0)
                
                # Use COPY command for faster data insertion
                target_cur.copy_expert(f"COPY {target_table} FROM STDIN WITH NULL AS '\\N'", output)
                
                # Truncate the table in the source database
                truncate_query = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(source_table))
                source_cur.execute(truncate_query)
                
                # Commit the transactions
                target_conn.commit()
                source_conn.commit()
                
                logging.info(f"Transferred {len(rows)} rows in {time.time() - start_time:.2f} seconds")
            else:
                logging.info("No data to transfer")
    
    except Exception as error:
        logging.error(f"Error during data transfer: {error}")
        # Rollback in case of error
        source_conn.rollback()
        target_conn.rollback()
    
    finally:
        source_pool.putconn(source_conn)
        target_pool.putconn(target_conn)

def main():
    last_run = 0
    interval = 5  # Run every 5 seconds
    
    while True:
        current_time = time.time()
        if current_time - last_run >= interval:
            transfer_data()
            last_run = current_time
        
        time.sleep(0.1)  # Short sleep to prevent CPU hogging

if __name__ == "__main__":
    main()
