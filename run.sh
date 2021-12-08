#!/usr/bin/with-contenv bashio

bashio::log.info "Reading configuration..."

# Create main config
LCD_DEVICE=$(bashio::config 'lcd_device')

bashio::log.info "Starting program..."
python3 program.py "${LCD_DEVICE}"