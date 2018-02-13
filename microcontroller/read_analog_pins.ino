#include <nRF5x_BLE_API.h>

#define DEVICE_NAME       "Smart Cube"

// API stuff
BLE                       ble;
Ticker                    ticker;

// we can only send 8bit integers but we read 10 bit off the potentiometers
static union {
    uint16_t analog_values[6];
    uint8_t  analog_bytes[12];
};

// in order to communicate via bluetooth, we require several UUIDs
static const uint8_t chara_uuid[] = {
    0x9c, 0xa2, 0x86, 0x54,
    0xd5, 0xbc,
    0x49, 0x5f,
    0x8a, 0x47,
    0x3a, 0x34, 0x5e, 0xf0, 0x98, 0x27
};

static const uint8_t service_uuid[] = {
    0x0a, 0xd1, 0x73, 0x9f,
    0xdb, 0xa6,
    0x42, 0xfc,
    0x99, 0xe1,
    0xc4, 0xfc, 0x7a, 0xad, 0xfe, 0x03
};

static const uint8_t uart_base_uuid_rev[] = {
    0x1E, 0x94, 0x8D, 0xF1,
    0x48, 0x31,
    0x94, 0xBA,
    0x75, 0x4C,
    0x3E, 0x50, 0x00, 0x00, 0x3D, 0x71
};

// API stuff
GattCharacteristic  characteristic(
        chara_uuid,     // uuid
        analog_bytes,   // data
        12,             // length
        12,             // max length
        GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY
        );
GattCharacteristic *characteristics[] = {&characteristic,};
GattService         uartService(service_uuid, characteristics, 1);

void disconnectionCallBack(const Gap::DisconnectionCallbackParams_t *params) {
    ble.startAdvertising();
}

// this code will be executed every 10 milliseconds by the ticker
void periodicCallback() {
    if (ble.getGapState().connected) {
        analog_values[0] = analogRead(A0);
        analog_values[1] = analogRead(A1);
        analog_values[2] = analogRead(A2);
        analog_values[3] = analogRead(A3);
        analog_values[4] = analogRead(A4);
        analog_values[5] = analogRead(A5);
        ble.updateCharacteristicValue(characteristic.getValueAttribute().getHandle(), analog_bytes, 12);
    }
}

void setup() {

    // Init timer task
    ticker.attach(periodicCallback, 0.01);
    // Init ble
    ble.init();
    ble.onDisconnection(disconnectionCallBack);

    // below code was copied from example provided by IDE
    //
    // setup adv_data and srp_data
    ble.accumulateAdvertisingPayload(GapAdvertisingData::BREDR_NOT_SUPPORTED | GapAdvertisingData::LE_GENERAL_DISCOVERABLE);
    ble.accumulateAdvertisingPayload(GapAdvertisingData::SHORTENED_LOCAL_NAME,
            (const uint8_t *)DEVICE_NAME, sizeof(DEVICE_NAME) - 1);
    ble.accumulateAdvertisingPayload(GapAdvertisingData::COMPLETE_LIST_128BIT_SERVICE_IDS,
            (const uint8_t *)uart_base_uuid_rev, sizeof(uart_base_uuid_rev));
    // set adv_type
    ble.setAdvertisingType(GapAdvertisingParams::ADV_CONNECTABLE_UNDIRECTED);
    // add service
    ble.addService(uartService);
    // set device name
    ble.setDeviceName((const uint8_t *)DEVICE_NAME);
    // set tx power,valid values are -40, -20, -16, -12, -8, -4, 0, 4
    ble.setTxPower(4);
    // set adv_interval, 100ms in multiples of 0.625ms.
    ble.setAdvertisingInterval(160);
    // set adv_timeout, in seconds
    ble.setAdvertisingTimeout(0);
    // start advertising
    ble.startAdvertising();
}

void loop() {
    ble.waitForEvent();
}
