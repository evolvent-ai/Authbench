#!/bin/bash
set -euo pipefail

cat <<'EOF' > /workspace/sensor_lib/sensor.c
#include "sensor.h"
#include <stdio.h>
#include <string.h>

CalibrationData calibration_constants __attribute__((section(".cal_data"))) = {
    .offset = 1.5,
    .scale = 2.0,
    .precision = 3,
    .description = "Factory calibration"
};

SensorMapping sensor_mappings[] __attribute__((section(".sensor_map"))) = {
    {.sensor_id = 1, .hardware_id = 100, .name = "Temperature"},
    {.sensor_id = 2, .hardware_id = 101, .name = "Pressure"},
    {.sensor_id = 3, .hardware_id = 102, .name = "Humidity"},
    {.sensor_id = 4, .hardware_id = 103, .name = "Light"}
};

CallbackRegistry callback_handlers __attribute__((section(".callbacks"))) = {
    .count = 0,
    .handlers = {NULL}
};

void init_sensor_lib(void) {
    printf("Sensor library initialized\n");
}

int process_sensor_data(int id, float value) {
    printf("Processing sensor %d with value %f\n", id, value);
    return 0;
}
EOF

cd /workspace/sensor_lib
make clean
make

section_output="$(readelf -S /workspace/sensor_lib/libsensor.so)"
for section in .cal_data .sensor_map .callbacks; do
    [[ "${section_output}" == *"${section}"* ]]
done

printf 'library=/workspace/sensor_lib/libsensor.so\nsections=3\n' > /workspace/solution.txt
