import time
import psycopg2
from pycomm3 import LogixDriver
from datetime import datetime, timezone
import sys
import os


ip_address = '10.10.13.3'
port = 44818  

db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'ai4m2024',
    'host': '192.168.20.135',
    'port': '5432'
}


def insert_data_into_db(conn, data):
    with conn.cursor() as cur:
        insert_query = '''
            INSERT INTO hul_plc_data2 (
                timestamp, cycle_start, year, month, day, hour, minute, second, microseconds,
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
                cycle_time_ms, detection, detection_time ,cycle_id
            ) VALUES (
                %(timestamp)s, %(cyclestart)s, %(timestamp_year)s, %(timestamp_month)s, %(timestamp_day)s,
                %(timestamp_hour)s, %(timestamp_minute)s, %(timestamp_second)s, %(timestamp_microsecond)s,
                %(SL21_Hoz_Sealer_Front_1_Temperature)s, %(SL21_Hoz_Sealer_Rear_1_Temperature)s,
                %(SL21_Hor_Sealer_Pressure)s, %(SL21_Hoz_Sealing_Time)s, %(SL21_Hoz_Sealer_Strock_1)s,
                %(SL21_Hoz_Sealer_Strock_2)s, %(SL21_Ver_Sealer_Strock_1)s, %(SL21_Ver_Sealer_Strock_2)s,
                %(SL21_Hoz_Sealer_Servo_Current)s, %(SL21_Ver_Sealer_Servo_Current)s, %(SL21_Sealing_Jaw_Area_Temp)s,
                %(SL21_Ver_Sealer_Pressure)s, %(SL21_Hoz_Sealer_Servo_Temperature)s, %(SL21_Ver_Sealer_Servo_Temperature)s,
                %(SL21_Laminate_Cof_Value)s, %(SL_21_Batch_Cut_On_Degree)s, %(SL_21_Batch_Cut_Off_Degree)s,
                %(SL21_Ver_Sealer_Front_1_Temp)s, %(SL21_Ver_Sealer_Front_2_Temp)s, %(SL21_Ver_Sealer_Front_3_Temp)s,
                %(SL21_Ver_Sealer_Front_4_Temp)s, %(SL21_Ver_Sealer_Front_5_Temp)s, %(SL21_Ver_Sealer_Front_6_Temp)s,
                %(SL21_Ver_Sealer_Front_7_Temp)s, %(SL21_Ver_Sealer_Front_8_Temp)s, %(SL21_Ver_Sealer_Front_9_Temp)s,
                %(SL21_Ver_Sealer_Front_10_Temp)s, %(SL21_Ver_Sealer_Front_11_Temp)s, %(SL21_Ver_Sealer_Front_12_Temp)s,
                %(SL21_Ver_Sealer_Front_13_Temp)s, %(SL21_Ver_Sealer_Rear_1_Temp)s, %(SL21_Ver_Sealer_Rear_2_Temp)s,
                %(SL21_Ver_Sealer_Rear_3_Temp)s, %(SL21_Ver_Sealer_Rear_4_Temp)s, %(SL21_Ver_Sealer_Rear_5_Temp)s,
                %(SL21_Ver_Sealer_Rear_6_Temp)s, %(SL21_Ver_Sealer_Rear_7_Temp)s, %(SL21_Ver_Sealer_Rear_8_Temp)s,
                %(SL21_Ver_Sealer_Rear_9_Temp)s, %(SL21_Ver_Sealer_Rear_10_Temp)s, %(SL21_Ver_Sealer_Rear_11_Temp)s,
                %(SL21_Ver_Sealer_Rear_12_Temp)s, %(SL21_Ver_Sealer_Rear_13_Temp)s, %(SL21_Hopper_Level)s,
                %(SL21_Piston_Stroke_Length)s, %(SL21_Laminate_GSM)s, %(SL21_Seal_init_Temp)s, %(SL21_Coeff_Friction)s,
                %(SL21_Seal_Strength)s, %(SL21_Pulling_Servo_Motor_Current)s, %(machine_status_code)s, %(horizontal_servo_position)s, %(vertical_servo_position)s, %(rotational_valve_position)s,
                %(fill_piston_position)s, %(web_puller_position)s, %(cam_position)s, %(machine_status)s, %(Spare9)s, %(Spare10)s, %(Spare11)s, %(Spare12)s,
                %(Spare13)s, %(Spare14)s,  %(plc_timestamp)s, %(cycle_time_ms)s , %(detection)s, %(detection_time)s , %(cycle_id)s
            )
        '''

        cur.execute(insert_query, data)
    conn.commit()


B=1
previous_A=None
C=0
#data_list = []
with LogixDriver(f'{ip_address}:{port}') as plc, psycopg2.connect(**db_params) as conn:
    while True:
        start_time = time.time()
        #now = datetime.now()
        #timestamp_value = time.time()
        #time_struct = time.localtime(timestamp_value)
        
        
        cycle_start_value = '' # plc.read('CycleStart').value
       # sachet_count = plc.read('SM21_SACHECOUNT').value

        
        timestamp_value = plc.read('TimeStamp').value
        #print("this is time stamp tag value :",timestamp_value)
        
        year = timestamp_value.get('Year')
        month = timestamp_value.get('Month')
        day = timestamp_value.get('Day')
        hour = timestamp_value.get('Hour')
        minute = timestamp_value.get('Min')
        second = timestamp_value.get('Sec')
        microsecond = timestamp_value.get('Microseconds')

        new_timestamp =datetime(year,month,day,hour,minute,second,microsecond)
#	print(new_timestamp) 
        rotational_valve_position = timestamp_value.get('Spare4')
        print(rotational_valve_position)

        # Create variable A
        A = f"{day:02d}{month:02d}{year % 100:02d}"

        # Check if A has changed, if so, reset B
        if A != previous_A:
            B = 1
            previous_A = A

        # Increment B if rotational_valve_position reaches 0
        if rotational_valve_position is not None and rotational_valve_position <= 5:
            B += 1

        # Combine A, B, and C to form cycle_id
        cycle_id = f"{A}-{B}-{C}"
        end_time = time.time()
        cycle_time_ms = (end_time - start_time) * 1000  

        
        data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'cyclestart': cycle_start_value,
            'timestamp_year': year,
            'timestamp_month': month,
            'timestamp_day': day,
            'timestamp_hour': hour,
            'timestamp_minute': minute,
            'timestamp_second': second,
            'timestamp_microsecond': microsecond,
            'SL21_Hoz_Sealer_Front_1_Temperature': timestamp_value.get('SL21_Hoz_Sealer_Front_1_Temperature'),
            'SL21_Hoz_Sealer_Rear_1_Temperature': timestamp_value.get('SL21_Hoz_Sealer_Rear_1_Temperature'),
            'SL21_Hor_Sealer_Pressure': timestamp_value.get('SL21_Hor_Sealer_Pressure'),
            'SL21_Hoz_Sealing_Time': timestamp_value.get('SL21_Hoz_Sealing_Time'),
            'SL21_Hoz_Sealer_Strock_1': timestamp_value.get('SL21_Hoz_Sealer_Strock_1'),
            'SL21_Hoz_Sealer_Strock_2': timestamp_value.get('SL21_Hoz_Sealer_Strock_2'),
            'SL21_Ver_Sealer_Strock_1': timestamp_value.get('SL21_Ver_Sealer_Strock_1'),
            'SL21_Ver_Sealer_Strock_2': timestamp_value.get('SL21_Ver_Sealer_Strock_2'),
            'SL21_Hoz_Sealer_Servo_Current': timestamp_value.get('SL21_Hoz_Sealer_Servo_Current'),
            'SL21_Ver_Sealer_Servo_Current': timestamp_value.get('SL21_Ver_Sealer_Servo_Current'),
            'SL21_Sealing_Jaw_Area_Temp': timestamp_value.get('SL21_Sealing_Jaw_Area_Temp'),
            'SL21_Ver_Sealer_Pressure': timestamp_value.get('SL21_Ver_Sealer_Pressure'),
            'SL21_Hoz_Sealer_Servo_Temperature': timestamp_value.get('SL21_Hoz_Sealer_Servo_Temperature'),
            'SL21_Ver_Sealer_Servo_Temperature': timestamp_value.get('SL21_Ver_Sealer_Servo_Temperature'),
            'SL21_Laminate_Cof_Value': timestamp_value.get('SL21_Laminate_Cof_Value'),
            'SL_21_Batch_Cut_On_Degree': timestamp_value.get('SL_21_Batch_Cut_On_Degree'),
            'SL_21_Batch_Cut_Off_Degree': timestamp_value.get('SL_21_Batch_Cut_Off_Degree'),
            'SL21_Ver_Sealer_Front_1_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_1_Temp'),
            'SL21_Ver_Sealer_Front_2_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_2_Temp'),
            'SL21_Ver_Sealer_Front_3_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_3_Temp'),
            'SL21_Ver_Sealer_Front_4_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_4_Temp'),
            'SL21_Ver_Sealer_Front_5_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_5_Temp'),
            'SL21_Ver_Sealer_Front_6_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_6_Temp'),
            'SL21_Ver_Sealer_Front_7_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_7_Temp'),
            'SL21_Ver_Sealer_Front_8_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_8_Temp'),
            'SL21_Ver_Sealer_Front_9_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_9_Temp'),
            'SL21_Ver_Sealer_Front_10_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_10_Temp'),
            'SL21_Ver_Sealer_Front_11_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_11_Temp'),
            'SL21_Ver_Sealer_Front_12_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_12_Temp'),
            'SL21_Ver_Sealer_Front_13_Temp': timestamp_value.get('SL21_Ver_Sealer_Front_13_Temp'),
            'SL21_Ver_Sealer_Rear_1_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_1_Temp'),
            'SL21_Ver_Sealer_Rear_2_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_2_Temp'),
            'SL21_Ver_Sealer_Rear_3_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_3_Temp'),
            'SL21_Ver_Sealer_Rear_4_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_4_Temp'),
            'SL21_Ver_Sealer_Rear_5_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_5_Temp'),
            'SL21_Ver_Sealer_Rear_6_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_6_Temp'),
            'SL21_Ver_Sealer_Rear_7_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_7_Temp'),
            'SL21_Ver_Sealer_Rear_8_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_8_Temp'),
            'SL21_Ver_Sealer_Rear_9_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_9_Temp'),
            'SL21_Ver_Sealer_Rear_10_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_10_Temp'),
            'SL21_Ver_Sealer_Rear_11_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_11_Temp'),
            'SL21_Ver_Sealer_Rear_12_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_12_Temp'),
            'SL21_Ver_Sealer_Rear_13_Temp': timestamp_value.get('SL21_Ver_Sealer_Rear_13_Temp'),
            'SL21_Hopper_Level': timestamp_value.get('SL21_Hopper_Level'),
            'SL21_Piston_Stroke_Length': timestamp_value.get('SL21_Piston_Stroke_Length'),
            'SL21_Laminate_GSM': timestamp_value.get('SL21_Laminate_GSM'),
            'SL21_Seal_init_Temp': timestamp_value.get('SL21_Seal_init_Temp'),
            'SL21_Coeff_Friction': timestamp_value.get('SL21_Coeff_Friction'),
            'SL21_Seal_Strength': timestamp_value.get('SL21_Seal_Strength'),
            'SL21_Pulling_Servo_Motor_Current': timestamp_value.get('SL21_Pulling_Servo_Motor_Current'),
            'machine_status_code': timestamp_value.get('Spare1'),
            'horizontal_servo_position': timestamp_value.get('Spare2'),
            'vertical_servo_position': timestamp_value.get('Spare3'),
            'rotational_valve_position': timestamp_value.get('Spare4'),
            'fill_piston_position': timestamp_value.get('Spare5'),
            'web_puller_position': timestamp_value.get('Spare6'),
            'cam_position': timestamp_value.get('Spare7'),
            'machine_status': timestamp_value.get('Spare8'),
            'Spare9': timestamp_value.get('Spare9'),
            'Spare10': timestamp_value.get('Spare10'),
            'Spare11': timestamp_value.get('Spare11'),
            'Spare12': timestamp_value.get('Spare12'),
            'Spare13': timestamp_value.get('Spare13'),
            'Spare14': timestamp_value.get('SL21_Hoz_Sealing_Time'),
            #'Spare15': timestamp_value.get('Spare15'),
            #'plc_timestamp': f"{year}-{month}-{day} {hour}:{minute}:{second}.{microsecond //10:07d}",
            'plc_timestamp':new_timestamp,	
            'cycle_time_ms': cycle_time_ms ,
            'detection': 0,
            'detection_time': None,
            'cycle_id' : cycle_id
        }

       # data_list.append(data)

        #data_list.sort(key=lambda x: (x['timestamp_year'], x['timestamp_month'], x['timestamp_day'], x['timestamp_hour'], x['timestamp_minute'], x['timestamp_second'], x['timestamp_microsecond']))

        
        #for data in data_list:
         #   insert_data_into_db(conn, data)

      
        #data_list.clear()

        try:
            insert_data_into_db(conn, data)
            print("Data inserted successfully into PostgreSQL.")
        except Exception as e:
            print(f"Error inserting data into PostgreSQL: {e}")


        print(f"Time taken for this read cycle: {cycle_time_ms:.4f} milliseconds")

        
        #time.sleep(1)  # Adjust as needed
