import asyncio
import datetime
from typing import List
import psycopg2
from fastapi import (
    FastAPI,
    BackgroundTasks,
    Depends,
    HTTPException,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from contextlib import closing
from fastapi import WebSocket
import json 
import os, sys
from status_data import color_codes, predictions_status_data, live_status_data, vertical_sealer_data


with open('db_config.json', 'r') as config_file:
    config = json.load(config_file)
    
DATABASE = config['database']
# print("DAtA",DATABASE)


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],  
    allow_headers=["*"], 
)



class StatusManager:
    def __init__(self):
        self.color_codes = color_codes
        self.predictions_status_data = predictions_status_data
        self.live_status_data = live_status_data
        self.vertical_sealer_data = vertical_sealer_data

    def get_db(self):
        conn = psycopg2.connect(**DATABASE)
        cursor = conn.cursor()
        return conn, cursor

    def close_db(self, conn, cursor):
        cursor.close()
        conn.close()

    
    def get_latest_prediction(self, cursor):
        query = "SELECT sl21_hopper_level,sl21_laminate_cof_value,sl21_pulling_servo_motor_current, sl21_hoz_sealer_servo_current, horizontal_servo_position, cam_position, machine_status, machine_status_code, sl21_hor_sealer_pressure FROM hul_plc_data ORDER BY plc_timestamp DESC LIMIT 1;"
        cursor.execute(query)
        prediction = cursor.fetchone()
        return prediction

  
    def get_latest_live_data(self, cursor):
        query = """
            SELECT 
                sl21_ver_sealer_pressure, sl21_hor_sealer_pressure ,   sl21_hoz_sealer_front_1_temperature, sl21_hoz_sealer_rear_1_temperature, sl21_hoz_sealing_time,
                sl21_ver_sealer_front_1_temp, sl21_ver_sealer_front_2_temp, sl21_ver_sealer_front_3_temp,
                sl21_ver_sealer_front_4_temp, sl21_ver_sealer_front_5_temp, sl21_ver_sealer_front_6_temp,
                sl21_ver_sealer_front_7_temp, sl21_ver_sealer_front_8_temp, sl21_ver_sealer_front_9_temp,
                sl21_ver_sealer_front_10_temp, sl21_ver_sealer_front_11_temp, sl21_ver_sealer_front_12_temp,
                sl21_ver_sealer_front_13_temp,
                sl21_ver_sealer_rear_1_temp, sl21_ver_sealer_rear_2_temp,
                sl21_ver_sealer_rear_3_temp, sl21_ver_sealer_rear_4_temp, sl21_ver_sealer_rear_5_temp,
                sl21_ver_sealer_rear_6_temp, sl21_ver_sealer_rear_7_temp, sl21_ver_sealer_rear_8_temp,
                sl21_ver_sealer_rear_9_temp, sl21_ver_sealer_rear_10_temp, sl21_ver_sealer_rear_11_temp,
                sl21_ver_sealer_rear_12_temp, sl21_ver_sealer_rear_13_temp
            FROM hul_plc_data ORDER BY plc_timestamp DESC LIMIT 1;
        """
        cursor.execute(query)
        latest_record = cursor.fetchone()
        
        
        if latest_record:
            
            filtered_front_temps = [
                value for value in latest_record[4:17] if value is not None
            ]
            filtered_rear_temp = latest_record[3]
            
            avg_temp_front = (
                sum(filtered_front_temps) / len(filtered_front_temps)
                if filtered_front_temps
                else None
            )
            avg_temp_rear = (
                filtered_rear_temp if filtered_rear_temp is not None else None
            )

            return (
                avg_temp_front,
                avg_temp_rear,
                latest_record[0],
                latest_record[1],
                latest_record[2],
                latest_record[3],
                latest_record[4],
                
            )
        else:
            return None, None, None, None, None, None

    
    def get_latest_vertical_sealer_data(self, cursor):
        query = """
            SELECT 
                sl21_ver_sealer_pressure,
                sl21_ver_sealer_front_1_temp, sl21_ver_sealer_front_2_temp, sl21_ver_sealer_front_3_temp,
                sl21_ver_sealer_front_4_temp, sl21_ver_sealer_front_5_temp, sl21_ver_sealer_front_6_temp,
                sl21_ver_sealer_front_7_temp, sl21_ver_sealer_front_8_temp, sl21_ver_sealer_front_9_temp,
                sl21_ver_sealer_front_10_temp, sl21_ver_sealer_front_11_temp, sl21_ver_sealer_front_12_temp,
                sl21_ver_sealer_front_13_temp,
                sl21_ver_sealer_rear_1_temp, sl21_ver_sealer_rear_2_temp,
                sl21_ver_sealer_rear_3_temp, sl21_ver_sealer_rear_4_temp, sl21_ver_sealer_rear_5_temp,
                sl21_ver_sealer_rear_6_temp, sl21_ver_sealer_rear_7_temp, sl21_ver_sealer_rear_8_temp,
                sl21_ver_sealer_rear_9_temp, sl21_ver_sealer_rear_10_temp, sl21_ver_sealer_rear_11_temp,
                sl21_ver_sealer_rear_12_temp, sl21_ver_sealer_rear_13_temp
            FROM hul_plc_data ORDER BY plc_timestamp DESC LIMIT 1;
        """
        cursor.execute(query)
        res_vertical_sealer_data = cursor.fetchone()

        if res_vertical_sealer_data:
            # Prepare dictionary with structured data
            self.vertical_sealer_data.update(
                {
                    "ver_sealer_pressure": {
                        "value": res_vertical_sealer_data[0],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[0] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_1": {
                        "value": res_vertical_sealer_data[1],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[1] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_2": {
                        "value": res_vertical_sealer_data[2],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[2] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_3": {
                        "value": res_vertical_sealer_data[3],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[3] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_4": {
                        "value": res_vertical_sealer_data[4],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[4] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_5": {
                        "value": res_vertical_sealer_data[5],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[5] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_6": {
                        "value": res_vertical_sealer_data[6],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[6] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_7": {
                        "value": res_vertical_sealer_data[7],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[7] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_8": {
                        "value": res_vertical_sealer_data[8],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[8] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_9": {
                        "value": res_vertical_sealer_data[9],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[9] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_10": {
                        "value": res_vertical_sealer_data[10],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[10] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_11": {
                        "value": res_vertical_sealer_data[11],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[11] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_12": {
                        "value": res_vertical_sealer_data[12],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[12] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_front_temp_13": {
                        "value": res_vertical_sealer_data[13],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[13] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_1": {
                        "value": res_vertical_sealer_data[14],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[14] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_2": {
                        "value": res_vertical_sealer_data[15],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[15] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_3": {
                        "value": res_vertical_sealer_data[16],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[16] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_4": {
                        "value": res_vertical_sealer_data[17],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[17] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_5": {
                        "value": res_vertical_sealer_data[18],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[18] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_6": {
                        "value": res_vertical_sealer_data[19],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[19] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_7": {
                        "value": res_vertical_sealer_data[20],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[20] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_8": {
                        "value": res_vertical_sealer_data[21],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[21] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_9": {
                        "value": res_vertical_sealer_data[22],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[22] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_10": {
                        "value": res_vertical_sealer_data[23],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[23] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_11": {
                        "value": res_vertical_sealer_data[24],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[24] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_12": {
                        "value": res_vertical_sealer_data[25],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[25] > 200
                            else "#FFFFFF"
                        ),
                    },
                    "ver_rear_temp_13": {
                        "value": res_vertical_sealer_data[26],
                        "color": (
                            "#FF0000"
                            if res_vertical_sealer_data[26] > 200
                            else "#FFFFFF"
                        ),
                    },
                }
            )
            return self.vertical_sealer_data
        else:
            return None

    def update_predictions_status(self):
        while True:
            time.sleep(0.5)
            conn, cursor = self.get_db()
            try:
                latest_prediction = self.get_latest_prediction(cursor)
                
                if latest_prediction:
                    if (
                        latest_prediction[3] > 8
                        and latest_prediction[4] < 45
                        and latest_prediction[5] < 113
                    ):
                        self.predictions_status_data.update(
                            {
                                "sealant_leakage": {
                                    "status": "Possibility",
                                    "color": self.color_codes["Possibility"],
                                }
                            }
                        )
                    elif latest_prediction[6] == 0 or latest_prediction[7] != 1000:
                        self.predictions_status_data.update(
                            {
                                "sealant_leakage": {
                                    "status": "Occured",
                                    "color": self.color_codes["Occured"],
                                }
                            }
                        )

                    elif (latest_prediction[5] > 125 and latest_prediction[5] < 195) and (latest_prediction[8] < 4.2):
                        self.predictions_status_data.update(
                            {
                                "sealant_leakage": {
                                    "status": "Possibility Horizontal Sealing Pressure Drop",
                                    "color": self.color_codes["Possibility"],
                                }
                            }
                        )

                    
                    else:
                        self.predictions_status_data.update(
                            {
                                 "sealant_leakage": {
                                    "status": "None",
                                    "color": self.color_codes["None"],
                                }
                            }
                       )
		            
                    self.predictions_status_data.update(
                        {
                            #"sealant_leakage": {"status": "None", "color": "#00FF00"},
                            "laminate_pulling": {"status": "None", "color": "#00FF00"},
                            "laminate_jamming": {"status": "None", "color": "#00FF00"},
                            "hopper_level": {
                                "value": latest_prediction[0],
                                "color": "#FF0000",
                            },
                            "laminate_cof_variation": {
                                "value": latest_prediction[1],
                                "color": "#FF0000",
                            },
                            "pulling_roller_current_variation": {
                                "value": latest_prediction[2],
                                "color": "#FF0000",
                            },
                        }
                    )
            finally:
                self.close_db(conn, cursor)

    # Background task to update live status every 0.6 seconds
    def update_live_status(self):
        while True:
            time.sleep(0.6)
            conn, cursor = self.get_db()
            try:
                (
                    avg_temp_front,
                    avg_temp_rear,
                    sl21_ver_sealer_pressure,
                    sl21_hor_sealer_pressure,
                    sl21_hoz_sealer_front_1_temperature,
                    sl21_hoz_sealer_rear_1_temperature,
                    hor_sealing_time
                ) = self.get_latest_live_data(cursor)
                if avg_temp_front is not None and avg_temp_rear is not None:
                    self.live_status_data.update(
                        {
                            "ver_front_temp": {
                                "value": avg_temp_front,
                                "color": (
                                    "#FF0000" if avg_temp_front > 200 else "#FFFFFF"
                                ),
                            },
                            "ver_rear_temp": {
                                "value": avg_temp_rear,
                                "color": (
                                    "#FF0000" if avg_temp_rear > 200 else "#FFFFFF"
                                ),
                            },
                            "ver_sealer_pressure": {
                                "value": sl21_ver_sealer_pressure,
                                "color": (
                                    "#FF0000"
                                    if sl21_ver_sealer_pressure > 70
                                    else "#FFFFFF"
                                ),
                            },
                            "hor_sealer_pressure": {
                                "value": sl21_hor_sealer_pressure,
                                "color": (
                                    "#FF0000"
                                    if sl21_hor_sealer_pressure > 5 #70
                                    else "#FFFFFF"
                                ),
                            },
                            "hoz_front_temp": {
                                "value": sl21_hoz_sealer_front_1_temperature,
                                "color": (
                                    "#FF0000"
                                    if sl21_hoz_sealer_front_1_temperature > 200
                                    else "#FFFFFF"
                                ),
                            },
                            "hoz_rear_temp": {
                                "value": sl21_hoz_sealer_rear_1_temperature,
                                "color": (
                                    "#FF0000"
                                    if sl21_hoz_sealer_rear_1_temperature > 200
                                    else "#FFFFFF"
                                ),
                            },
                            "ver_time": {
                                "value": hor_sealing_time,
                                "color": "#FFFFFF",
                            },
                            "hoz_time": {
                                "value": hor_sealing_time,
                                "color": "#FFFFFF",
                            },
                        }
                    )
            finally:
                self.close_db(conn, cursor)

    def update_vertical_sealer_data(self):
        while True:
            time.sleep(0.6)
            conn, cursor = self.get_db()
            try:
                latest_vertical_sealer_data = self.get_latest_vertical_sealer_data(
                    cursor
                )
                if latest_vertical_sealer_data:
                    # Update ver_sealer_pressure
                    self.vertical_sealer_data["ver_sealer_pressure"]["value"] = (
                        latest_vertical_sealer_data["ver_sealer_pressure"]["value"]
                    )
                    self.vertical_sealer_data["ver_sealer_pressure"]["color"] = (
                        "#FFFFFF"
                        if latest_vertical_sealer_data["ver_sealer_pressure"]["value"]
                        <= 200
                        else "#FF0000"
                    )

                    # Update ver_front_temps
                    for i in range(1, 14):  # Assuming there are 13 front temps
                        temp_key = f"ver_front_temp_{i}"
                        self.vertical_sealer_data[temp_key]["value"] = (
                            latest_vertical_sealer_data[temp_key]["value"]
                        )
                        self.vertical_sealer_data[temp_key]["color"] = (
                            "#FFFFFF"
                            if latest_vertical_sealer_data[temp_key]["value"] <= 200
                            else "#FF0000"
                        )

                    for i in range(1, 14):  
                        temp_key = f"ver_rear_temp_{i}"
                        self.vertical_sealer_data[temp_key]["value"] = (
                            latest_vertical_sealer_data[temp_key]["value"]
                        )
                        self.vertical_sealer_data[temp_key]["color"] = (
                            "#FFFFFF"
                            if latest_vertical_sealer_data[temp_key]["value"] <= 200
                            else "#FF0000"
                        )
            finally:
                self.close_db(conn, cursor)

    def get_laminate_cof_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_laminate_cof_value, sl21_pulling_servo_motor_current
                FROM hul_plc_data
                WHERE plc_timestamp > %s
                ORDER BY plc_timestamp DESC LIMIT 1;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_laminate_cof_value, sl21_pulling_servo_motor_current
                FROM hul_plc_data
                ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()

    
    def get_hopper_level_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_hopper_level, rotational_valve_position
                FROM hul_plc_data
                WHERE plc_timestamp > %s
                ORDER BY plc_timestamp DESC LIMIT 1;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_hopper_level, rotational_valve_position
                FROM hul_plc_data
               ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()

    def get_pulling_roller_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_pulling_servo_motor_current,cam_position as cam
                FROM hul_plc_data
                WHERE plc_timestamp > %s
                ORDER BY plc_timestamp DESC LIMIT 1;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_pulling_servo_motor_current,cam_position as cam
                FROM hul_plc_data
                ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()
    
    #Horizontal Sealer
    def get_horizontal_sealer_graph_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
            SELECT plc_timestamp, sl21_hoz_sealer_servo_current, sl21_hor_sealer_pressure, 
                   sl21_hoz_sealer_servo_temperature as Hoz_temp, cam_position as Cam, 
                   spare14 as horizontal_sealing_time_scaled
            FROM hul_plc_data
            WHERE plc_timestamp > %s
            ORDER BY plc_timestamp DESC
            LIMIT 1;
        """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
            SELECT plc_timestamp, sl21_hoz_sealer_servo_current, sl21_hor_sealer_pressure, 
                   sl21_hoz_sealer_servo_temperature as Hoz_temp, cam_position as Cam, 
                   spare14 as horizontal_sealing_time_scaled
            FROM hul_plc_data
            ORDER BY plc_timestamp DESC 
            LIMIT 100;
        """
            cursor.execute(query)
        return cursor.fetchall()


    def get_vertical_front_serial_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_ver_sealer_front_1_temp, sl21_ver_sealer_front_2_temp, sl21_ver_sealer_front_3_temp,
                sl21_ver_sealer_front_4_temp, sl21_ver_sealer_front_5_temp, sl21_ver_sealer_front_6_temp,
                sl21_ver_sealer_front_7_temp, sl21_ver_sealer_front_8_temp, sl21_ver_sealer_front_9_temp,
                sl21_ver_sealer_front_10_temp, sl21_ver_sealer_front_11_temp, sl21_ver_sealer_front_12_temp,
                sl21_ver_sealer_front_13_temp
                FROM hul_plc_data
                WHERE plc_timestamp > %s
                ORDER BY plc_timestamp DESC LIMIT 1;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_ver_sealer_front_1_temp, sl21_ver_sealer_front_2_temp, sl21_ver_sealer_front_3_temp,
                sl21_ver_sealer_front_4_temp, sl21_ver_sealer_front_5_temp, sl21_ver_sealer_front_6_temp,
                sl21_ver_sealer_front_7_temp, sl21_ver_sealer_front_8_temp, sl21_ver_sealer_front_9_temp,
                sl21_ver_sealer_front_10_temp, sl21_ver_sealer_front_11_temp, sl21_ver_sealer_front_12_temp,
                sl21_ver_sealer_front_13_temp
                FROM hul_plc_data
               ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()

    def get_vertical_rear_serial_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_ver_sealer_rear_1_temp, sl21_ver_sealer_rear_2_temp,
                sl21_ver_sealer_rear_3_temp, sl21_ver_sealer_rear_4_temp, sl21_ver_sealer_rear_5_temp,
                sl21_ver_sealer_rear_6_temp, sl21_ver_sealer_rear_7_temp, sl21_ver_sealer_rear_8_temp,
                sl21_ver_sealer_rear_9_temp, sl21_ver_sealer_rear_10_temp, sl21_ver_sealer_rear_11_temp,
                sl21_ver_sealer_rear_12_temp, sl21_ver_sealer_rear_13_temp
                FROM hul_plc_data
                WHERE plc_timestamp > %s
                ORDER BY plc_timestamp DESC LIMIT 1;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_ver_sealer_rear_1_temp, sl21_ver_sealer_rear_2_temp,
                sl21_ver_sealer_rear_3_temp, sl21_ver_sealer_rear_4_temp, sl21_ver_sealer_rear_5_temp,
                sl21_ver_sealer_rear_6_temp, sl21_ver_sealer_rear_7_temp, sl21_ver_sealer_rear_8_temp,
                sl21_ver_sealer_rear_9_temp, sl21_ver_sealer_rear_10_temp, sl21_ver_sealer_rear_11_temp,
                sl21_ver_sealer_rear_12_temp, sl21_ver_sealer_rear_13_temp
                FROM hul_plc_data
               ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()

    def get_vertical_serial_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_ver_sealer_pressure,sl21_ver_sealer_servo_current,vertical_servo_position,cam_position
                FROM hul_plc_data
                WHERE plc_timestamp > %s
                ORDER BY plc_timestamp DESC LIMIT 1;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_ver_sealer_pressure,sl21_ver_sealer_servo_current,vertical_servo_position,cam_position
                FROM hul_plc_data
               ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()

    def get_horizontal_serial_data(self, cursor, last_timestamp=None):
        if last_timestamp:
            query = """
                SELECT plc_timestamp, sl21_hoz_sealer_servo_current, sl21_hor_sealer_pressure,  sl21_hoz_sealer_servo_temperature/10.0 as Hoz_temp ,cam_position/10.0 as Cam, spare14/10.0 as horizontal_sealing_time_scaled FROM hul_plc_data ;
            """
            cursor.execute(query, (last_timestamp,))
        else:
            query = """
                SELECT plc_timestamp, sl21_hoz_sealer_servo_current, sl21_hor_sealer_pressure,  sl21_hoz_sealer_servo_temperature/10.0 as Hoz_temp ,cam_position/10.0 as Cam, spare14/10.0 as horizontal_sealing_time_scaled FROM hul_plc_data 
                ORDER BY plc_timestamp DESC 
                LIMIT 100;
            """
            cursor.execute(query)
        return cursor.fetchall()


status_manager = StatusManager()


@app.get("/status/predictions")
async def get_predictions_status():
    return JSONResponse(content=status_manager.predictions_status_data)


# FastAPI endpoint to retrieve live status
@app.get("/status/live_data")
async def get_live_status():
    return JSONResponse(content=status_manager.live_status_data)



# FastAPI endpoint to retrieve vertical sealer data
@app.get("/status/vertical_sealer_data")
def get_vertical_sealer_data():
    conn, cursor = status_manager.get_db()
    data = status_manager.get_latest_vertical_sealer_data(cursor)
    if data is None:
        raise HTTPException(status_code=404, detail="Vertical sealer data not found")

    # Assuming data is a dictionary without circular references
    return JSONResponse(content=data)

@app.get("/status/horizontal_sealer_data")
def get_horizontal_sealer_data():
    conn, cursor = status_manager.get_db()
    data = status_manager.get_horizontal_sealer_data(cursor)
    if data is None:
        raise HTTPException(status_code=404, detail="Horizontal sealer data not found")

    # Assuming data is a dictionary without circular references
    return JSONResponse(content=data)



def format_data_laminate(data: List[tuple]) -> List[dict]:
    """
    Format database query results into JSON-serializable format.
    """

    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "laminate_cof_value": round(float(record[1]), 2),
            "pulling_servo_motor_current": round(float(record[2]), 2),
        }
        for record in data
    ]
    return formatted_data


def format_data_hopper(data: List[tuple]) -> List[dict]:
    """
    Format database query results into JSON-serializable format.
    """

    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "hopper_level": round(float(record[1]), 2),
            "rotational_pulling_current": round(float(record[2]), 2),
        }
        for record in data
    ]
    return formatted_data


def format_data_roller(data: List[tuple]) -> List[dict]:
    """
    Format database query results into JSON-serializable format.
    """

    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "pulling_servo_motor_current": round(float(record[1]), 2),
            "cam": round(float(record[2]), 2),
        }
        for record in data
    ]
    return formatted_data


def format_vertical_front_serial_data(data: List[tuple]) -> List[dict]:
    """
    Format database query results into JSON-serializable format.
    """

    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "ver_front_temp_1": round(float(record[1]), 2),
            "ver_front_temp_2": round(float(record[2]), 2),
            "ver_front_temp_3": round(float(record[3]), 2),
            "ver_front_temp_4": round(float(record[4]), 2),
            "ver_front_temp_5": round(float(record[5]), 2),
            "ver_front_temp_6": round(float(record[6]), 2),
            "ver_front_temp_7": round(float(record[7]), 2),
            "ver_front_temp_8": round(float(record[8]), 2),
            "ver_front_temp_9": round(float(record[9]), 2),
            "ver_front_temp_10": round(float(record[10]), 2),
            "ver_front_temp_11": round(float(record[11]), 2),
            "ver_front_temp_12": round(float(record[12]), 2),
            "ver_front_temp_13": round(float(record[13]), 2),
        }
        for record in data
    ]
    return formatted_data


def format_vertical_rear_serial_data(data: List[tuple]) -> List[dict]:
    """
    Format database query results into JSON-serializable format.
    """

    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "ver_rear_temp_1": round(float(record[1]), 2),
            "ver_rear_temp_2": round(float(record[2]), 2),
            "ver_rear_temp_3": round(float(record[3]), 2),
            "ver_rear_temp_4": round(float(record[4]), 2),
            "ver_rear_temp_5": round(float(record[5]), 2),
            "ver_rear_temp_6": round(float(record[6]), 2),
            "ver_rear_temp_7": round(float(record[7]), 2),
            "ver_rear_temp_8": round(float(record[8]), 2),
            "ver_rear_temp_9": round(float(record[9]), 2),
            "ver_rear_temp_10": round(float(record[10]), 2),
            "ver_rear_temp_11": round(float(record[11]), 2),
            "ver_rear_temp_12": round(float(record[12]), 2),
            "ver_rear_temp_13": round(float(record[13]), 2),
        }
        for record in data
    ]
    return formatted_data


def format_vertical_serial_data(data: List[tuple]) -> List[dict]:
    """
    Format database query results into JSON-serializable format.
    """

    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "ver_pressure": round(float(record[1]), 2),
            "ver_current": round(float(record[2]), 2),
            "ver_position": round(float(record[3]), 2),
            "ver_cam": round(float(record[4]), 2),
        }
        for record in data
    ]
    return formatted_data

########
def format_horizontal_sealer_data(data: List[tuple]) -> List[dict]:
    """
    Format database query results for horizontal sealer data into JSON-serializable format.
    """
    formatted_data = [
        {
            "timestamp": record[0].isoformat(),
            "hoz_sealer_servo_current": round(float(record[1]), 2),
            "hor_sealer_pressure": round(float(record[2]), 2),
            "hoz_temp": round(float(record[3]), 2),
            "cam_position": round(float(record[4]), 2),
            "horizontal_sealing_time": round(float(record[5]), 2)
        }
        for record in data
    ]
    return formatted_data

@app.websocket("/ws/laminate_cof_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    # Fetch initial data
                    initial_data = status_manager.get_laminate_cof_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        response_data = format_data_laminate(initial_data)
                        await websocket.send_json(response_data)
                else:
                    # Fetch data after last_timestamp
                    data = status_manager.get_laminate_cof_data(cursor, last_timestamp)
                    if data:
                        last_timestamp = data[-1][0]  
                        initial_data.extend(data)
                        response_data = format_data_laminate(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100 :]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            await asyncio.sleep(100 / 1_000_000)   # This will sleep for 50 microseconds  

    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/ws/hopper_level_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    # Fetch initial data
                    initial_data = status_manager.get_hopper_level_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][0
                        ]  # Update last_timestamp to the latest timestamp
                        response_data = format_data_hopper(initial_data)
                        await websocket.send_json(response_data)
                else:
                    
                    data = status_manager.get_hopper_level_data(cursor, last_timestamp)
                    if data:
                        last_timestamp = data[-1][0]  
                        initial_data.extend(data)
                        response_data = format_data_hopper(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100 :]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            awaitasyncio.sleep(60 / 1_000_000)   # This will sleep for 50 microseconds  # Adjust the sleep time as needed

    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/ws/pulling_roller_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    # Fetch initial data
                    initial_data = status_manager.get_pulling_roller_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        response_data = format_data_roller(initial_data)
                        await websocket.send_json(response_data)
                else:
                    # Fetch data after last_timestamp
                    data = status_manager.get_pulling_roller_data(
                        cursor, last_timestamp
                    )
                    if data:
                        last_timestamp = data[-1][0]  
                        initial_data.extend(data)
                        response_data = format_data_roller(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100 :]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            await asyncio.sleep(100 / 1_000_000)   # This will sleep for 50 microseconds  

    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/ws/vertical_sealer_front_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    initial_data = status_manager.get_vertical_front_serial_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][0]  
                        response_data = format_vertical_front_serial_data(initial_data)
                        await websocket.send_json(response_data)
                else:
                    
                    data = status_manager.get_vertical_front_serial_data(
                        cursor, last_timestamp
                    )
                    if data:
                        last_timestamp = data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        # response_data = format_data(data)
                        initial_data.extend(data)
                        response_data = format_vertical_front_serial_data(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100 :]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            await asyncio.sleep(100 / 1_000_000)   # This will sleep for 50 microseconds  # Adjust the sleep time as needed

    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/ws/vertical_sealer_rear_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    # Fetch initial data
                    initial_data = status_manager.get_vertical_rear_serial_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        response_data = format_vertical_rear_serial_data(initial_data)
                        await websocket.send_json(response_data)
                else:
                    # Fetch data after last_timestamp
                    data = status_manager.get_vertical_rear_serial_data(
                        cursor, last_timestamp
                    )
                    if data:
                        last_timestamp = data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        # response_data = format_data(data)
                        initial_data.extend(data)
                        response_data = format_vertical_rear_serial_data(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100 :]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            await asyncio.sleep(100 / 1_000_000)   # This will sleep for 50 microseconds  # Adjust the sleep time as needed

    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/ws/vertical_sealer_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    # Fetch initial data
                    initial_data = status_manager.get_vertical_serial_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        response_data = format_vertical_serial_data(initial_data)
                        await websocket.send_json(response_data)
                else:
                    # Fetch data after last_timestamp
                    data = status_manager.get_vertical_serial_data(
                        cursor, last_timestamp
                    )
                    if data:
                        last_timestamp = data[-1][
                            0
                        ]  # Update last_timestamp to the latest timestamp
                        # response_data = format_data(data)
                        initial_data.extend(data)
                        response_data = format_vertical_serial_data(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100 :]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            await asyncio.sleep(100 / 1_000_000)   # This will sleep for 50 microseconds # Adjust the sleep time as needed

    except WebSocketDisconnect:
        print("Client disconnected")
####
@app.websocket("/ws/horizontal_sealer_graph_data")
async def horizontal_sealer_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_timestamp = None
    initial_data = []
    try:
        while True:
            conn, cursor = status_manager.get_db()
            try:
                if last_timestamp is None:
                    initial_data = status_manager.get_horizontal_sealer_graph_data(cursor)
                    if initial_data:
                        last_timestamp = initial_data[-1][0] 
                        response_data = format_horizontal_sealer_data(initial_data)
                        print("Responsedata:",response_data)
                        await websocket.send_json(response_data)
                else:
                   
                    data = status_manager.get_horizontal_sealer_graph_data(cursor, last_timestamp)
                    if data:
                        last_timestamp = data[-1][0]  
                        initial_data.extend(data)
                        response_data = format_horizontal_sealer_data(initial_data)
                        if len(initial_data) >= 100:
                            initial_data = initial_data[len(initial_data) - 100:]
                        await websocket.send_json(response_data)
            finally:
                status_manager.close_db(conn, cursor)

            await asyncio.sleep(100 / 1_000_000)   # This will sleep for 50 microseconds  

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    threading.Thread(
        target=status_manager.update_predictions_status, daemon=True
    ).start()
    threading.Thread(target=status_manager.update_live_status, daemon=True).start()
    threading.Thread(
        target=status_manager.update_vertical_sealer_data, daemon=True
    ).start()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

