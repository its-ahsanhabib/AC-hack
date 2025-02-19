#!/usr/bin/python3
import paho.mqtt.client as mqtt
import json
from proto import parse_packet, init_set_cmd, set, make_packet

MQTTHOST = "116.204.142.39"

last_cmd = init_set_cmd()


def to_intlist(hex_list):
    return [
        int(hex_list[i:i + 2], 16) for i in range(len(hex_list)) if i % 2 == 0
    ]


def to_hexlist(int_list):
    hex_list = ""
    for i in int_list:
        hex_list += "{:02X}".format(i)
    return hex_list


def set_cmd(arg, val):
    global last_cmd
    print(last_cmd)
    set(last_cmd, arg, val)
    print(last_cmd)
    pkt = to_hexlist(make_packet(last_cmd))
    client.publish("cmnd/tasmota_105624/SerialSend", pkt)


def setup_mqtt(rc):

    def result_fn(_a, _b, msg):
        print(msg.payload.decode("utf-8"))
        jsn = json.loads(msg.payload.decode("utf-8"))
        if "SerialReceived" not in jsn:
            return
        state = jsn["SerialReceived"]
        state_int = [
            int(state[i:i + 2], 16) for i in range(len(state)) if i % 2 == 0
        ]
        try:
            resp = parse_packet(state_int)['Packet']
        except Exception as e:
            print(e)
            return
        if "Get" in resp:
            state_jsn = resp["Get"]
        elif "Set" in resp:
            state_jsn = resp["Set"]
        else:
            return
        print(state_jsn)
        client.publish("ac_control/state", json.dumps(state_jsn))

    client.message_callback_add("tele/AC/RESULT", result_fn)
    client.subscribe("tele/AC/RESULT")

    def set_fn(_a, _b, msg):
        args = msg.payload.decode("utf-8").strip().split(' ', 1)
        set_cmd(args[0], args[1])

    client.message_callback_add("ac_control/set", set_fn)
    client.subscribe("ac_control/set")

    def set_pwr_fn(_a, _b, msg):
        print("power cmd",msg.payload.decode("utf-8"))
        set_cmd("pwr", msg.payload.decode("utf-8"))

    client.message_callback_add("ac_control/set_pwr", set_pwr_fn)
    client.subscribe("ac_control/set_pwr")

    def get_fn(_a, _b, msg):
        pkt = to_hexlist(make_packet([4, 2, 1, 0]))
        client.publish("cmnd/tasmota_105624/SerialSend", pkt)

    client.message_callback_add("ac_control/get", get_fn)
    client.subscribe("ac_control/get")

    def custom_fn(_a, _b, msg):
        pl = msg.payload.decode("utf-8")
        if len(pl) % 2 != 0:  # todo check hex
            return
        pkt = to_hexlist(make_packet(to_intlist(pl)))
        client.publish("cmnd/tasmota_105624/SerialSend", pkt)

    client.message_callback_add("ac_control/custom", custom_fn)
    client.subscribe("ac_control/custom")

    def set_temp_fn(_a, _b, msg):
        set_cmd("temp", msg.payload.decode("utf-8")) # temp numaric

    client.message_callback_add("ac_control/set_temp", set_temp_fn)
    client.subscribe("ac_control/set_temp")

    def set_fan_fn(_a, _b, msg):
        set_cmd("fan", msg.payload.decode("utf-8"))

    client.message_callback_add("ac_control/set_fan", set_fan_fn)
    client.subscribe("ac_control/set_fan")


if __name__ == "__main__":

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.username_pw_set("ahsan","ahsan")
    client.on_connect = lambda client, userdata, flags, rc: setup_mqtt(rc)
    client.connect(MQTTHOST, 1883, 60)

    client.loop_forever()