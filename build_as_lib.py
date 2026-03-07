from os.path import realpath
import subprocess
import json

Import("env") # type: ignore
menv=env # type: ignore

src_filter = [
  '+<*.cpp>',
  '+<helpers/*.cpp>',
  '+<helpers/sensors>',
  '+<helpers/radiolib/*.cpp>',
  '+<helpers/ui/MomentaryButton.cpp>',
  '+<helpers/ui/buzzer.cpp>',
]

# add build and include dirs according to CPPDEFINES
for item in menv.get("CPPDEFINES", []):
 
    # PLATFORM HANDLING
    if item == "STM32_PLATFORM":
        src_filter.append("+<helpers/stm32/*>")
    elif item == "ESP32":
        src_filter.append("+<helpers/esp32/*>")
    elif item == "NRF52_PLATFORM":
        src_filter.append("+<helpers/nrf52/*>")
    elif item == "RP2040_PLATFORM":
        src_filter.append("+<helpers/rp2040/*>")
    
    # DISPLAY HANDLING
    elif isinstance(item, tuple) and item[0] == "DISPLAY_CLASS":
        display_class = item[1]
        src_filter.append(f"+<helpers/ui/{display_class}.cpp>")
        if (display_class == "ST7789Display") :
            src_filter.append(f"+<helpers/ui/OLEDDisplay.cpp>")
            src_filter.append(f"+<helpers/ui/OLEDDisplayFonts.cpp>")

    # VARIANTS HANDLING
    elif isinstance(item, tuple) and item[0] == "MC_VARIANT":
        variant_name = item[1]
        command = ["pio", "project", "config", "--json-output"]
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        project_config = json.loads(output.stdout)

        variant_config_block = next((item for item in project_config if item[0] == variant_name), None)
        if variant_config_block:
            variant_config = dict(variant_config_block[1])
            build_flags = variant_config.get("build_flags", [])
            menv.Append(BUILD_FLAGS=build_flags)
            build_src_filter = variant_config.get("build_src_filter", [])
            src_filter.append(build_src_filter)
            #lib_deps = variant_config.get("lib_deps", [])
            #menv.Append(LIB_DEPS=lib_deps)


        src_filter.append(f"+<../variants/{variant_name}>")
    
    # INCLUDE EXAMPLE CODE IN BUILD (to provide your own support files without touching the tree)
    elif isinstance(item, tuple) and item[0] == "BUILD_EXAMPLE":
        example_name = item[1]
        src_filter.append(f"+<../examples/{example_name}/*.cpp>")

    # EXCLUDE A SOURCE FILE FROM AN EXAMPLE (must be placed after example name or boom)
    elif isinstance(item, tuple) and item[0] == "EXCLUDE_FROM_EXAMPLE":
        exclude_name = item[1]
        if example_name is None:
            print("***** PLEASE DEFINE EXAMPLE FIRST *****")
            break
        src_filter.append(f"-<../examples/{example_name}/{exclude_name}>")

    # DEAL WITH UI VARIANT FOR AN EXAMPLE
    elif isinstance(item, tuple) and item[0] == "MC_UI_FLAVOR":
        ui_flavor = item[1]
        if example_name is None:
            print("***** PLEASE DEFINE EXAMPLE FIRST *****")
            break
        src_filter.append(f"+<../examples/{example_name}/{ui_flavor}/*.cpp>")
        
menv.Replace(SRC_FILTER=src_filter)

#print (menv.Dump())
