from eseries import find_nearest, E24
import sys

#Equations for Component Values

#Global Setting
V_adc_max = 1.8 #Max voltage the ADC can read
ADC_resolution = 4096 #Resolution of ADC

V_op = 2.0 #Supply voltage of OP-AMPs and analog circuitry, sets LDO output voltage

V_solar_max = 3.0 #Max voltage of the solar panels
I_solar_max = 1 #Max amperage the solar panels can source
#I_solar_min = 0 #solar can not sink current

V_battery_max = 4.5 #Max voltage of the battery
I_battery_max = 1 #Max amperage the battery can source
I_battery_min = -1 #Max amperage the batteyr can sink

I_over_current = 0.25 #Over current set point (amps)
I_trickle_current = 0.05 #Trickle current set point (amps)

V_boost = 4.2 #Boost converter volatage set point


V_pwm_max = 1.8
V_pwm_min = 0

V_solar_mppt = 2.7 #Mppt voltage set point
V_mppt_max = 2.95  #MPPT highest adjustment voltage
V_mppt_min = 1.5   #MPPT lowerest adjustment voltage 

### LDO
print("\nldo")

Vout = V_op #volts
Vref_ldo = 1.25
R28 = 1e4

def ldo_divider():
    R27 = R28 * Vref_ldo / (Vout - Vref_ldo) 
    R27 = find_nearest(E24, R27)
    print("R27 = " + str(R27))
    return R27

R27 = ldo_divider()

### SOLAR
print("\nsolar")

#Calculate solar resistor divider

R14 = 1e4 #ohms

def solar_voltage_divider():
    R13 = R14 * ((V_solar_max / V_adc_max) - 1.0)
    R13 = find_nearest(E24, R13)
    print("R13 = " + str(R13))
    return R13

R13 = solar_voltage_divider()

#Calculate solar ADC scaling factor

def adc_solar_scaling_factor():
    ADC_solar_scaling_factor = (V_adc_max / ADC_resolution) * ((R13 + R14) / R14)
    print("ADC solar scaling factor: " + str(ADC_solar_scaling_factor))
    return ADC_solar_scaling_factor

ADC_solar_scaling_factor = adc_solar_scaling_factor()

# Calculate current bias resistors

I_solar = I_solar_max

R1 = 0.1
R4 = 1e4

#resistor values for 
def solar_current_bias():
    R5 = (V_op * R4) / (I_solar_max * R1) - 2 * R4
    R5 = find_nearest(E24, R5)
    print("R5 = " + str(R5))
    return R5

R5 = solar_current_bias()

# Calculate current gain resistors

R6 = 1e4
I_solar_min = 0

#resistor values for 
def solar_current_gain():
    V_a_plus = (V_op - (I_solar_min * R1)) * (R4 / (R4 + R5)) - I_solar_min * R1
    R9 = R6 * (V_adc_max / V_a_plus - 1)
    R9 = find_nearest(E24, R9)
    print("R9 = " + str(R9))
    return R9

R9 = solar_current_gain()

def solar_current_adc_reading_conversion(ADC_reading):
    I_sol = V_op * (R4 / (2 * R4 + R5)) - ADC_reading * (V_adc_max / ADC_resolution) * (1 / ((R9 /R6 + 1) * ((R4 / (R4 + R5) + 1))))
    return I_sol

### BATTERY 
print("\nbattery")

#Calculate solar resistor divider

R12 = 1e4 #ohms

def battery_voltage_divider():
    R11 = R12 * ((V_battery_max / V_adc_max) - 1.0)
    R11 = find_nearest(E24, R11)
    print("R11 = " + str(R11))
    return R11

R11 = battery_voltage_divider()

#Calculate solar ADC scaling factor

def adc_battery_scaling_factor():
    ADC_battery_scaling_factor = (V_adc_max / ADC_resolution) * ((R11 + R12) / R12)
    print("ADC battery scaling factor: " + str(ADC_battery_scaling_factor))
    return ADC_battery_scaling_factor

ADC_battery_scaling_factor = adc_solar_scaling_factor()


# Calculate current bias resistors

I_battery = I_battery_max

R2 = 0.1
R3 = 1e4

#resistor values for 
def battery_current_bias():
    R7 = (V_op * R3) / (I_solar_max * R2) - 2 * R3
    R7 = find_nearest(E24, R7)
    print("R7 = " + str(R7))
    return R7

R7 = battery_current_bias()

# Calculate current gain resistors

R8 = 1e4

#resistor values for 
def battery_current_gain():
    V_b_plus = (V_op - (I_battery_min * R2)) * (R3 / (R3 + R7)) - I_battery_min * R2
    #print("v_b+ = " + str(V_b_plus))
    R10 = R8 * (V_adc_max / V_b_plus - 1)
    R10 = find_nearest(E24, R10)
    print("R10 = " + str(R10))
    return R10

R10 = battery_current_gain()

def battery_current_adc_reading_conversion(ADC_reading):
    I_batt = V_op * (R3 / (2 * R3 + R7)) - ADC_reading * (V_adc_max / ADC_resolution) * (1 / ((R10 /R8 + 1) * ((R3 / (R3 + R7) + 1))))
    return I_batt


### Over Current
print("\ncurrent")

R19 = 1e4

#determine resistor for
def over_current():
    V_b_plus = (V_op + (I_over_current * R2)) * (R3 / (R3 + R7)) + I_over_current * R2
    print("v_b+ = " + str(V_b_plus))
    V_b_out = (R10 / R8 + 1) * V_b_plus
    print("V_b_out = " + str(V_b_out))
    R18 = R19 * V_op / V_b_out - R19
    R18 = find_nearest(E24, R18)
    print("R18 = " + str(R18))
    return R18

R18 = over_current()


### Trickle current
def trickle_current():
    V_b_plus = (V_op + (I_trickle_current * R2)) * (R3 / (R3 + R7)) + I_trickle_current * R2
    print("v_b+ = " + str(V_b_plus))
    V_b_out = (R10 / R8 + 1) * V_b_plus
    print("V_b_out = " + str(V_b_out))
    R17 = (V_b_out * R18 * R19) / ((V_op - V_b_out) * R19 - V_b_out * R18)
    R17 = find_nearest(E24, R17)
    print("R17 = " + str(R17))
    return R17

R17 = trickle_current()

print("\nboost")

### BOOST SET VOLTAGE

V_ref_boost = 1.212
R25 = 20e3

def boost_resistor_divider():
    R26 = R25 * V_ref_boost / (V_boost - V_ref_boost)
    R26 = find_nearest(E24, R26)
    print("R26 = " + str(R26))
    return R26

R26 = boost_resistor_divider()

### MPPT SET VOLTAGE

R23 = 1e4

def mppt_resistor_divider():
    R22 = R23 * ((R14 + R13) * V_op / (R14 * V_solar_mppt) - 1)
    R22 = find_nearest(E24, R22)
    print("R22 = " + str(R22))
    return R22

R22 = mppt_resistor_divider()

### MPPT 

V_pwm = V_pwm_max
V_sol = V_mppt_max

def mppt_pwm_resistor():
    Vset = V_sol * (R14 / (R13 + R14))
    R20 = (V_pwm - Vset) * (R22 * R23) / ((Vset * (R22 + R23) - V_op * R23))
    R20 = find_nearest(E24, R20)
    print("R20 = " + str(R20))
    return R20

R20_max = mppt_pwm_resistor()

V_pwm = V_pwm_min
V_sol = V_mppt_min

R20_min = mppt_pwm_resistor()

R20 = min(R20_min, R20_max)

#Update Resistor Values
components = {
    'R28' : R28,
    'R27' : R27,
    'R13' : R13,
    'R14' : R14,
    'R1'  : R1,
    'R5'  : R5,
    'R4'  : R4,
    'R6'  : R6,
    'R9'  : R9,
    'R11' : R11,
    'R12' : R12,
    'R2'  : R2,
    'R3'  : R3,
    'R7'  : R7,
    'R8'  : R8,
    'R10' : R10,
    'R17' : R17,
    'R18' : R18,
    'R19' : R19,
    'R25' : R25,
    'R26' : R26,
    'R22' : R22,
    'R23' : R23,
    'R20' : R20
}

print("\n\nUpdate Kicad")

def format_resistor_value(enumber):
    #enumber = find_nearest(E24, val)
    formatter = lambda n, suffix: str(n).rstrip('0').rstrip('.') + suffix

    if enumber >= 1e9:
        enumber /= 1e9
        return str(enumber).rstrip('0').rstrip('.') + "G 1%"
    elif enumber >= 1e6:
        enumber /= 1e6
        return str(enumber).rstrip('0').rstrip('.') + "M 1%"
    elif enumber >= 1e3:
        enumber /= 1e3
        return str(enumber).rstrip('0').rstrip('.') + "K 1%"
    else:
        return str(enumber).rstrip('0').rstrip('.') + " 1%"

def change_component_value(ref, val, sch_lines):
    n = 0
    for line in sch_lines:
        n += 1
        searchStr = "F 0 \"" + ref + "\""
        if searchStr in line:
            replaceStr = sch_lines[n].split('"')
            replaceStr = replaceStr[0] + '"' + format_resistor_value(val) + '"' + replaceStr[2]
            replaceStr.join('')
            print(ref + ": " + replaceStr)
            sch_lines[n] = replaceStr

def main():
    if(len(sys.argv) < 2):
        print("please enter schematic location")
        sys.exit(2)
    
    lines = ""

    with open(sys.argv[1], 'r') as logfile:
        schematic = logfile.read()
        with open('backup.sch','w') as backup:
            backup.write(schematic)
        lines = schematic.splitlines()
        for ref,val in components.items():
            change_component_value(ref, val, lines)
    
    with open(sys.argv[1], 'w') as logfile:
        logfile.write('\n'.join(lines))

#F 0 "R28"
    
if __name__ == "__main__":
    main()
