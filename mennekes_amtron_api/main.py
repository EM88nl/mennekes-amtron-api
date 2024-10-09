import argparse
import uvicorn
from fastapi import FastAPI
import minimalmodbus

api = FastAPI()


@api.get('/status/evse')
def get_status_evse():
    map = {
        0: 'Not initialized',
        1: 'Idle',
        2: 'EV connected',
        3: 'Preconditions valid but not charging yet',
        4: 'Ready to charge',
        5: 'Charging',
        6: 'Error',
        7: 'Service mode',
    }
    data = api.state.charger.read_register(0x0100)
    return {'evse_status': data, 'description': map[data]}

@api.get('/status/authorization')
def get_status_authorization():
    map = {
        0: 'Authorization not required',
        1: 'Authorized',
        2: 'Not authorized',
    }
    data = api.state.charger.read_register(0x0101)
    return {'authorization_status': data, 'description': map[data]}

@api.get('/setting/current/limit')
def get_setting_current_limit():
    data = api.state.charger.read_float(0x0302)
    return {'setting_current_limit': data}

@api.put('/setting/current/limit')
def set_setting_current_limit(current_limit: float):
    api.state.charger.write_float(0x0302, current_limit)
    return get_setting_current_limit()

@api.get('/actual/power/overall')
def get_actual_power_overall():
    return {'actual_power_overall': api.state.charger.read_float(0x0512)}

@api.get('/session/current/limit')
def get_session_current_limit():
    return {'session_current_limit': api.state.charger.read_float(0x0B00)}

@api.get('/session/energy')
def get_session_energy():
    return {'session_energy': api.state.charger.read_float(0x0B02)}

@api.get('/session/duration')
def get_session_duration():
    return {'session_duration': api.state.charger.read_float(0x0B04)}

def main():
    parser = argparse.ArgumentParser(description='Unofficial Mennekes AMTRON API')
    parser.add_argument('--serial', type=str, required=True, help='Path to the serial RS-485 adapter')
    parser.add_argument('--slave-address', type=int, default=1, help='Modbus slave address of the charger')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the API on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the API on')
    args = parser.parse_args()

    api.state.charger = minimalmodbus.Instrument(args.serial, args.slave_address)
    api.state.charger.serial.baudrate = 57600
    api.state.charger.serial.stopbits = 2

    uvicorn.run(api, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
