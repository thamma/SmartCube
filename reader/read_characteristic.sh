#!/bin/bash
# 
gatttool \
    -t random \ # whyever this was neccessary
    -b C6:ED:66:65:06:AF \ # the MAC adress of our microcontroller
    --char-write-req --handle=0x000f --value=0100 \ # enables notifications
    --listen
