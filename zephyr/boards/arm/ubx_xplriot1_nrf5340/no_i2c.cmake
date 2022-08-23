
# Setup to disable I2C
# Needed when both Sara and Nina shall be used together

list(APPEND CONF_FILE ${CMAKE_CURRENT_LIST_DIR}/no_i2c.conf)
list(APPEND DTC_OVERLAY_FILE  ${CMAKE_CURRENT_LIST_DIR}/no_i2c.overlay)