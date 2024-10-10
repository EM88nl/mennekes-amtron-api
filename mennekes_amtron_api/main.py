import argparse
import uvicorn
from fastapi import FastAPI, HTTPException
import minimalmodbus

api = FastAPI()


@api.get('/status/evse')
def get_status_evse():
    """
    Get the current status of the EVSE
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
    return {'status': data, 'description': evse_statuses[data]}

@api.get('/status/authorization')
def get_status_authorization():
    """
    Get the current authorization status
    """
    authorization_statuses = {
        0: 'Authorization not required',
        1: 'Authorized',
        2: 'Not authorized',
    }
    data = api.state.charger.read_register(0x0101)
    return {'status': data, 'description': authorization_statuses[data]}

@api.get('/settings/current-limit')
def get_settings_current_limit():
    """
    Get the maximal current (amperage) limit per phase
    """
    return {'current': api.state.charger.read_float(0x0302)}

@api.put('/settings/current-limit')
def set_settings_current_limit(current_limit: float):
    """
    Set the maximal current (amperage) limit per phase
    """
    ipsilon = 0.1
    if current_limit < 0 or (current_limit > 0 and current_limit < 6) or current_limit > 16:
        raise HTTPException(status_code=400, detail='Current limit must be between 6 and 16 A, or 0 to disable current limiting')
    api.state.charger.write_float(0x0302, current_limit)
    return get_settings_current_limit()

@api.get('/settings/charging-release')
def get_settings_charging_release():
    """
    Get the charging release mode
    """
    charging_release_modes = {
        0: 'Charging not allowed',
        1: 'Charging allowed',
    }
    data = api.state.charger.read_register(0x0D05)
    return {'mode': data, 'description': charging_release_modes[data]}

@api.put('/settings/charging-release')
def set_settings_charging_release(charging_release: int):
    """
    Set the charging release mode.
    0: Charging not allowed
    1: Charging allowed
    """
    if charging_release not in [0, 1]:
        raise HTTPException(status_code=400, detail='Charging release mode must be 0 or 1')
    api.state.charger.write_register(0x0D05, charging_release)
    return get_settings_charging_release()

@api.get('/sessions/current/power')
def get_sessions_current_power():
    """
    Get the power of the current charging session
    """
    return {'power': api.state.charger.read_float(0x0512)}

@api.get('/sessions/current/energy')
def get_sessions_current_energy():
    """
    Get the total energy transferred during the current charging session
    """
    return {'energy': api.state.charger.read_float(0x0B02)}

@api.get('/sessions/current/duration')
def get_sessions_current_duration():
    """
    Get the duration of the current charging session
    """
    return {'duration': api.state.charger.read_float(0x0B04)}

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
