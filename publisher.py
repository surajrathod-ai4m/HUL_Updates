import zmq
import time
import json
import random

def zmq_publisher():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://localhost:5555")
    
    statuses = ["Occured", "None", "Possibility"]
    color_codes = {
        "Occured": "#FF0000",    # Red
        "None": "#00FF00",       # Green
        "Possibility": "#FFBF00", # Amber
    }
    
    prediction_interval = 1  # 1 second for predictions
    live_data_interval = 0.6  # 600 milliseconds for live_data
    
    last_prediction_time = 0
    last_live_data_time = 0
    
    while True:
        current_time = time.time()
        
        if current_time - last_prediction_time >= prediction_interval:
            # Publish predictions topic
            predictions_status = {
                "sealant_leakage": random.choice(statuses),
                "laminate_pulling": random.choice(statuses),
                "laminate_jamming": random.choice(statuses)
            }
            
            predictions_status_with_color = {
                "sealant_leakage": {
                    "status": predictions_status["sealant_leakage"],
                    "color": color_codes[predictions_status["sealant_leakage"]]
                },
                "laminate_pulling": {
                    "status": predictions_status["laminate_pulling"],
                    "color": color_codes[predictions_status["laminate_pulling"]]
                },
                "laminate_jamming": {
                    "status": predictions_status["laminate_jamming"],
                    "color": color_codes[predictions_status["laminate_jamming"]]
                }
            }
            
            predictions_message = json.dumps(predictions_status_with_color)
            socket.send_string(f"predictions {predictions_message}")
            print(f"Published on predictions: {predictions_message}")
            
            last_prediction_time = current_time
        
        if current_time - last_live_data_time >= live_data_interval:
            # Publish live_data topic
            vertical_sealer_pressure_value = random.uniform(50, 100)  # Logical range for pressure (e.g., 50-100 psi)
            horizontal_sealer_pressure_value = random.uniform(50, 100)  # Logical range for pressure (e.g., 50-100 psi)
            horizontal_sealer_front_temp_value = random.uniform(150, 250)  # Logical range for temp (e.g., 150-250 °C)
            horizontal_sealer_rear_temp_value = random.uniform(150, 250)  # Logical range for temp (e.g., 150-250 °C)
            live_data_status = {
                "vertical_sealer_pressure": {
                    "value": vertical_sealer_pressure_value,
                    "color": "#FF0000" if vertical_sealer_pressure_value > 70 else "#FFFFFF"
                },
                "horizontal_sealer_pressure": {
                    "value": horizontal_sealer_pressure_value,
                    "color": "#FF0000" if horizontal_sealer_pressure_value > 70 else "#FFFFFF"
                },
                "horizontal_sealer_front_temp": {
                    "value": horizontal_sealer_front_temp_value,
                    "color": "#FF0000" if horizontal_sealer_front_temp_value > 200 else "#FFFFFF"
                },
                "horizontal_sealer_rear_temp": {
                    "value": horizontal_sealer_rear_temp_value,
                    "color": "#FF0000" if horizontal_sealer_rear_temp_value > 200 else "#FFFFFF"
                }
            }
            
            live_data_message = json.dumps(live_data_status)
            socket.send_string(f"live_data {live_data_message}")
            print(f"Published on live_data: {live_data_message}")
            
            last_live_data_time = current_time

        time.sleep(0.1)  # Sleep briefly to prevent tight loop

if __name__ == "__main__":
    zmq_publisher()
