import argparse
import uvicorn
from fastapi import FastAPI
import minimalmodbus

api = FastAPI()


@api.get('/status/evse')
def get_status_evse():
    """
    @brief Get the current status of the EVSE
    """
    evse_statuses = {
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
    return {'evse_status': data, 'description': evse_statuses[data]}

@api.get('/status/authorization')
def get_status_authorization():
    """
    @brief Get the current authorization status
    """
    authorization_statuses = {
        0: 'Authorization not required',
        1: 'Authorized',
        2: 'Not authorized',
    }
    data = api.state.charger.read_register(0x0101)
    return {'authorization_status': data, 'description': authorization_statuses[data]}

@api.get('/settings/current-limit')
def get_settings_current_limit():
    """
    @brief Get the maximal current (amperage) limit per phase
    """
    return {'current_limit': api.state.charger.read_float(0x0302)}

@api.put('/settings/current-limit')
def set_settings_current_limit(current_limit: float):
    """
    @brief Set the maximal current (amperage) limit per phase
    """
    api.state.charger.write_float(0x0302, current_limit)
    return get_settings_current_limit()

@api.get('/sessions/current/power')
def get_sessions_current_power():
    """
    @brief Get the power of the current charging session
    """
    return {'current_power': api.state.charger.read_float(0x0512)}

@api.get('/sessions/current/energy')
def get_sessions_current_energy():
    """
    @brief Get the total energy transferred during the current charging session
    """
    return {'current_energy': api.state.charger.read_float(0x0B02)}

@api.get('/sessions/current/duration')
def get_sessions_current_duration():
    """
    @brief Get the duration of the current charging session
    """
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
