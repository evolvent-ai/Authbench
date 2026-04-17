The C project at `/workspace/sensor_lib` is supposed to place three global data objects into specific custom ELF sections, but the section-placement attributes are missing.

Fix only the source code needed to restore the intended section layout, then build the shared library and record what you verified.

Project layout:

```text
/workspace/sensor_lib/
├── sensor.c
├── sensor.h
└── Makefile
```

Requirements:
- Keep `sensor.h` and `Makefile` unchanged.
- Update `sensor.c` so the compiled shared library places:
  - calibration data in `.cal_data`
  - sensor mappings in `.sensor_map`
  - callback handlers in `.callbacks`
- Build the project with the existing `Makefile`.
- Create `/workspace/solution.txt` with exactly these two lines:

```text
library=/workspace/sensor_lib/libsensor.so
sections=3
```

The task is correct when:
1. `/workspace/sensor_lib/libsensor.so` exists and is a valid shared library.
2. The compiled library contains `.cal_data`, `.sensor_map`, and `.callbacks`.
3. `/workspace/solution.txt` matches the required format exactly.
