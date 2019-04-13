from custom_components.china_holiday.binary_sensor import IsWorkdaySensor

sensor = IsWorkdaySensor("abc", 10003, "b59bc3ef6191eb9f747dd4e83c99f2a4")
sensor.update()
print(sensor.is_on)