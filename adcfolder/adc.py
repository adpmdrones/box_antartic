#!/usr/bin/python
# -*- coding:utf-8 -*-


import time
import ADS1263
import RPi.GPIO as GPIO

REF = 5.08          # Modify according to actual voltage external AVDD and AVSS(Default), or internal 2.5V
ADC = ADS1263.ADS1263()
if (ADC.ADS1263_init() == -1):
    exit()


def read_adc():
    ADC_final = [0,0,0,0,0,0,0,0,0,0]
    try:
        ADC_Value = ADC.ADS1263_GetAll()    # get ADC1 value
        for i in range(0, 10):
            if(ADC_Value[i]>>31 ==1):
                ADC_final[i] = REF*2 - ADC_Value[i] * REF / 0x80000000
            else:
                ADC_final[i] = ADC_Value[i] * REF / 0x7fffffff

    except:
        print("ADC error")

    return ADC_final
