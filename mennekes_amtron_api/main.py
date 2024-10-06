import argparse
import uvicorn
from fastapi import FastAPI
import minimalmodbus

api = FastAPI()


@api.get('/status/evse')
def get_status_evse():
    states_evse = {
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
    return {'evse_status': data, 'evse_status_description': states_evse[data]}

def main():
    parser = argparse.ArgumentParser(description='Mennekes AMTRON API')
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
