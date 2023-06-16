class StrDef:
    # TODO - reduce size by 1 char/int identifiers

    SEN_TEMPERATURE = "temp"
    SEN_HUMIDITY = "humidity"
    SEN_PRESSURE = "pressure"
    SEN_AIR_QUALITY = "air_quality"
    SEN_LIGHT_LOW = "light_low"
    SEN_LIGHT_HIGH1 = "light_h1"
    SEN_LIGHT_HIGH2 = "light_h2"

    ST_TEMPERATURE_AVG = "temp_avg"
    ST_TEMPERATURE_SDV = "temp_std"
    ST_TEMPERATURE_MAX = "temp_max"
    ST_AIR_QUALITY_AVG = "aq_avg"
    ST_AIR_QUALITY_SDV = "aq_std"
    ST_AIR_QUALITY_WORST = "aq_worst"  # max co2
    ST_LIGHT_AVG = "light_avg"
    ST_LIGHT_SDV = "light_std"
    ST_ARR_WINDOW_STATUS = "window_status"
    ST_ARTIFICIAL_LIGHT_STATUS = "art_light_status"

    # WirelessIQ Parameters
    CONST_SLEEP_TIMER = 2
    CONST_STAT_TIME = 3600  # 3600