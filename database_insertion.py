from datetime import datetime
import time
import pandas as pd
import psycopg2
from psycopg2 import sql

# Define the path to your CSV file
csv_file_path = '/home/ai4m/HUL/DB/sample.csv'  # Update with your CSV file path

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Define your PostgreSQL connection parameters
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'ai4m2024',
    'host': 'localhost',
    'port': '5432'
}

def insert_data_into_db(conn, data):
    try:
        with conn.cursor() as cur:
            insert_query = '''
                INSERT INTO hul_plc_data (timestamp, cycle_start, year, month, day, hour, minute, second, microseconds,
                sl21_hoz_sealer_front_1_temperature, sl21_hoz_sealer_rear_1_temperature,
                sl21_hor_sealer_pressure, sl21_hoz_sealing_time, sl21_hoz_sealer_strock_1,
                sl21_hoz_sealer_strock_2, sl21_ver_sealer_strock_1, sl21_ver_sealer_strock_2,
                sl21_hoz_sealer_servo_current, sl21_ver_sealer_servo_current, sl21_sealing_jaw_area_temp,
                sl21_ver_sealer_pressure, sl21_hoz_sealer_servo_temperature, sl21_ver_sealer_servo_temperature,
                sl21_laminate_cof_value, sl_21_batch_cut_on_degree, sl_21_batch_cut_off_degree,
                sl21_ver_sealer_front_1_temp, sl21_ver_sealer_front_2_temp, sl21_ver_sealer_front_3_temp,
                sl21_ver_sealer_front_4_temp, sl21_ver_sealer_front_5_temp, sl21_ver_sealer_front_6_temp,
                sl21_ver_sealer_front_7_temp, sl21_ver_sealer_front_8_temp, sl21_ver_sealer_front_9_temp,
                sl21_ver_sealer_front_10_temp, sl21_ver_sealer_front_11_temp, sl21_ver_sealer_front_12_temp,
                sl21_ver_sealer_front_13_temp, sl21_ver_sealer_rear_1_temp, sl21_ver_sealer_rear_2_temp,
                sl21_ver_sealer_rear_3_temp, sl21_ver_sealer_rear_4_temp, sl21_ver_sealer_rear_5_temp,
                sl21_ver_sealer_rear_6_temp, sl21_ver_sealer_rear_7_temp, sl21_ver_sealer_rear_8_temp,
                sl21_ver_sealer_rear_9_temp, sl21_ver_sealer_rear_10_temp, sl21_ver_sealer_rear_11_temp,
                sl21_ver_sealer_rear_12_temp, sl21_ver_sealer_rear_13_temp, sl21_hopper_level,
                sl21_piston_stroke_length, sl21_laminate_gsm, sl21_seal_init_temp, sl21_coeff_friction,
                sl21_seal_strength, sl21_pulling_servo_motor_current, machine_status_code, horizontal_servo_position, vertical_servo_position, rotational_valve_position,
                fill_piston_position, web_puller_position, cam_position, machine_status, spare9, spare10, spare11, spare12, spare13, spare14,plc_timestamp,
                cycle_time_ms

                ) VALUES (%(timestamp)s, %(cycle_start)s, %(year)s, %(month)s, %(day)s, %(hour)s, %(minute)s, %(second)s, %(microseconds)s,
                    %(sl21_hoz_sealer_front_1_temperature)s, %(sl21_hoz_sealer_rear_1_temperature)s,
                    %(sl21_hor_sealer_pressure)s, %(sl21_hoz_sealing_time)s, %(sl21_hoz_sealer_strock_1)s,
                    %(sl21_hoz_sealer_strock_2)s, %(sl21_ver_sealer_strock_1)s, %(sl21_ver_sealer_strock_2)s,
                    %(sl21_hoz_sealer_servo_current)s, %(sl21_ver_sealer_servo_current)s, %(sl21_sealing_jaw_area_temp)s,
                    %(sl21_ver_sealer_pressure)s, %(sl21_hoz_sealer_servo_temperature)s, %(sl21_ver_sealer_servo_temperature)s,
                    %(sl21_laminate_cof_value)s, %(sl_21_batch_cut_on_degree)s, %(sl_21_batch_cut_off_degree)s,
                    %(sl21_ver_sealer_front_1_temp)s, %(sl21_ver_sealer_front_2_temp)s, %(sl21_ver_sealer_front_3_temp)s,
                    %(sl21_ver_sealer_front_4_temp)s, %(sl21_ver_sealer_front_5_temp)s, %(sl21_ver_sealer_front_6_temp)s,
                    %(sl21_ver_sealer_front_7_temp)s, %(sl21_ver_sealer_front_8_temp)s, %(sl21_ver_sealer_front_9_temp)s,
                    %(sl21_ver_sealer_front_10_temp)s, %(sl21_ver_sealer_front_11_temp)s, %(sl21_ver_sealer_front_12_temp)s,
                    %(sl21_ver_sealer_front_13_temp)s, %(sl21_ver_sealer_rear_1_temp)s, %(sl21_ver_sealer_rear_2_temp)s,
                    %(sl21_ver_sealer_rear_3_temp)s, %(sl21_ver_sealer_rear_4_temp)s, %(sl21_ver_sealer_rear_5_temp)s,
                    %(sl21_ver_sealer_rear_6_temp)s, %(sl21_ver_sealer_rear_7_temp)s, %(sl21_ver_sealer_rear_8_temp)s,
                    %(sl21_ver_sealer_rear_9_temp)s, %(sl21_ver_sealer_rear_10_temp)s, %(sl21_ver_sealer_rear_11_temp)s,
                    %(sl21_ver_sealer_rear_12_temp)s, %(sl21_ver_sealer_rear_13_temp)s, %(sl21_hopper_level)s,
                    %(sl21_piston_stroke_length)s, %(sl21_laminate_gsm)s, %(sl21_seal_init_temp)s, %(sl21_coeff_friction)s,
                    %(sl21_seal_strength)s, %(sl21_pulling_servo_motor_current)s, %(machine_status_code)s, %(horizontal_servo_position)s, %(vertical_servo_position)s, %(rotational_valve_position)s,
                %(fill_piston_position)s, %(web_puller_position)s, %(cam_position)s, %(machine_status)s, %(spare9)s, %(spare10)s, %(spare11)s, %(spare12)s,
                    %(spare13)s, %(spare14)s,  %(plc_timestamp)s, %(cycle_time_ms)s  

                )
            '''
            cur.execute(insert_query, data)
            print(data)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data: {e}")

# Create a connection to the PostgreSQL database
try:
    conn = psycopg2.connect(**conn_params)
    print("Database connection established")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    conn = None

if conn:
    # Prepare data dictionary for each row and insert into the database
    for row in df.itertuples(index=False, name=None):
       # Assuming row[0] is a string representing a timestamp in the format "%Y-%m-%d %H:%M:%S.%f"
        now = datetime.now()
         # Generate a timestamp
                 
        timestamp_value = time.time()
        time_struct = time.localtime(timestamp_value)

        # Extract individual components
        year = time.strftime("%Y", time_struct)
        month = time.strftime("%m", time_struct)
        day = time.strftime("%d", time_struct)
        hour = time.strftime("%H", time_struct)
        minute = time.strftime("%M", time_struct)
        second = time.strftime("%S", time_struct)
        microsecond = int((timestamp_value - int(timestamp_value)) * 1_000_000)
        data_dict = {
            'timestamp': now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 10:05d}Z",
            'cycle_start': row[1],
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute':minute,
            'second': second,
            'microseconds': microsecond,
            'sl21_hoz_sealer_front_1_temperature': row[9],
            'sl21_hoz_sealer_rear_1_temperature': row[10],
            'sl21_hor_sealer_pressure': row[11],
            'sl21_hoz_sealing_time': row[12],
            'sl21_hoz_sealer_strock_1': row[13],
            'sl21_hoz_sealer_strock_2': row[14],
            'sl21_ver_sealer_strock_1': row[15],
            'sl21_ver_sealer_strock_2': row[16],
            'sl21_hoz_sealer_servo_current': row[17],
            'sl21_ver_sealer_servo_current': row[18],
            'sl21_sealing_jaw_area_temp': row[19],
            'sl21_ver_sealer_pressure': row[20],
            'sl21_hoz_sealer_servo_temperature': row[21],
            'sl21_ver_sealer_servo_temperature': row[22],
            'sl21_laminate_cof_value': row[23],
            'sl_21_batch_cut_on_degree': row[24],
            'sl_21_batch_cut_off_degree': row[25],
            'sl21_ver_sealer_front_1_temp': row[26],
            'sl21_ver_sealer_front_2_temp': row[27],
            'sl21_ver_sealer_front_3_temp': row[28],
            'sl21_ver_sealer_front_4_temp': row[29],
            'sl21_ver_sealer_front_5_temp': row[30],
            'sl21_ver_sealer_front_6_temp': row[31],
            'sl21_ver_sealer_front_7_temp': row[32],
            'sl21_ver_sealer_front_8_temp': row[33],
            'sl21_ver_sealer_front_9_temp': row[34],
            'sl21_ver_sealer_front_10_temp': row[35],
            'sl21_ver_sealer_front_11_temp': row[36],
            'sl21_ver_sealer_front_12_temp': row[37],
            'sl21_ver_sealer_front_13_temp': row[38],
            'sl21_ver_sealer_rear_1_temp': row[39],
            'sl21_ver_sealer_rear_2_temp': row[40],
            'sl21_ver_sealer_rear_3_temp': row[41],
            'sl21_ver_sealer_rear_4_temp': row[42],
            'sl21_ver_sealer_rear_5_temp': row[43],
            'sl21_ver_sealer_rear_6_temp': row[44],
            'sl21_ver_sealer_rear_7_temp': row[45],
            'sl21_ver_sealer_rear_8_temp': row[46],
            'sl21_ver_sealer_rear_9_temp': row[47],
            'sl21_ver_sealer_rear_10_temp': row[48],
            'sl21_ver_sealer_rear_11_temp': row[49],
            'sl21_ver_sealer_rear_12_temp': row[50],
            'sl21_ver_sealer_rear_13_temp': row[51],
            'sl21_hopper_level': row[52],
            'sl21_piston_stroke_length': row[53],
            'sl21_laminate_gsm': row[54],
            'sl21_seal_init_temp': row[55],
            'sl21_coeff_friction': row[56],
            'sl21_seal_strength': row[57],
            'sl21_pulling_servo_motor_current': row[58],
            'machine_status_code': row[59],
            'horizontal_servo_position': row[60],
            'vertical_servo_position': row[61],
            'rotational_valve_position': row[62],
            'fill_piston_position': row[63],
            'web_puller_position': row[64],
            'cam_position': row[65],
            'machine_status': row[66],
            'spare9': row[67],
            'spare10': row[68],
            'spare11': row[69],
            'spare12': row[70],
            'spare13': row[71],
            'spare14': row[72],
            'plc_timestamp':now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 10:05d}Z",
            'cycle_time_ms': row[74],
        }
        try:
            insert_data_into_db(conn, data_dict)
        except Exception as e:
            print(f"Error processing row: {e}")

    # Close the connection
    try:
        conn.close()
        print("Database connection closed")
    except Exception as e:
        print(f"Error closing the database connection: {e}")
else:
    print("Connection not established, skipping data insertion.")
