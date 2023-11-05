import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import spi, power_supply
from esphome.const import (
    CONF_BACKLIGHT_PIN,
    CONF_DC_PIN,
    CONF_HEIGHT,
    CONF_ID,
    CONF_RESET_PIN,
    CONF_WIDTH,
    CONF_POWER_SUPPLY,
    CONF_OUTPUT,
)

from .init_sequences import ST7701S_INITS

st7701s_ns = cg.esphome_ns.namespace("st7701s")

CONF_INIT_SEQUENCE = "init_sequence"
CONF_OFFSET_HEIGHT = "offset_height"
CONF_OFFSET_WIDTH = "offset_width"
CONF_DATA_PINS = "data_pins"
CONF_DE_PIN = "de_pin"
CONF_PCLK_PIN = "pclk_pin"
CONF_HSYNC_PIN = "hsync_pin"
CONF_VSYNC_PIN = "vsync_pin"

CONF_HSYNC_PULSE_WIDTH = "hsync_pulse_width"
CONF_HSYNC_BACK_PORCH = "hsync_back_porch"
CONF_HSYNC_FRONT_PORCH = "hsync_front_porch"
CONF_VSYNC_PULSE_WIDTH = "vsync_pulse_width"
CONF_VSYNC_BACK_PORCH = "vsync_back_porch"
CONF_VSYNC_FRONT_PORCH = "vsync_front_porch"

CODEOWNERS = ["@clydebarrow"]

DEPENDENCIES = ["spi"]

ST7701S = st7701s_ns.class_("ST7701S", cg.PollingComponent, spi.SPIDevice)

DATA_PIN_SCHEMA = pins.gpio_pin_schema(
    {
        CONF_OUTPUT: True,
    },
    internal=True,
)


def map_sequence(value):
    """
    An initialisation sequence can be selected from one of the pre-defined sequences in init_sequences.py,
    or can be a literal array of data bytes.
    The format is a repeated sequence of [CMD, LEN, <data>] where <data> is LEN bytes.
    """
    if not isinstance(value, list):
        value = cv.int_(value)
        value = cv.one_of(*ST7701S_INITS)(value)
        value = ST7701S_INITS[value]
    value = cv.ensure_list(cv.uint8_t)(value)
    data_length = len(value)
    i = 0
    while i < data_length:
        remaining = data_length - i
        # Command byte is at value[i], length of data at value[i+1]
        if remaining < 2 or value[i + 1] > remaining - 2:
            raise cv.Invalid(f"Malformed initialisation sequence at index {i}")
        i += 2 + value[i + 1]
    return value


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(ST7701S),
            cv.Required(CONF_DATA_PINS): cv.All(
                [DATA_PIN_SCHEMA],
                cv.Length(min=16, max=16, msg="Exactly 16 data pins required"),
            ),
            cv.Optional(CONF_INIT_SEQUENCE, default=7): map_sequence,
            cv.Required(CONF_DE_PIN): pins.internal_gpio_output_pin_schema,
            cv.Required(CONF_PCLK_PIN): pins.internal_gpio_output_pin_schema,
            cv.Required(CONF_HSYNC_PIN): pins.internal_gpio_output_pin_schema,
            cv.Required(CONF_VSYNC_PIN): pins.internal_gpio_output_pin_schema,
            cv.Optional(CONF_RESET_PIN): pins.gpio_output_pin_schema,
            cv.Optional(CONF_DC_PIN): pins.gpio_output_pin_schema,
            cv.Optional(CONF_BACKLIGHT_PIN): cv.Any(
                cv.boolean,
                pins.gpio_output_pin_schema,
            ),
            cv.Optional(CONF_HSYNC_PULSE_WIDTH, default=8): cv.int_,
            cv.Optional(CONF_HSYNC_BACK_PORCH, default=50): cv.int_,
            cv.Optional(CONF_HSYNC_FRONT_PORCH, default=10): cv.int_,
            cv.Optional(CONF_VSYNC_PULSE_WIDTH, default=8): cv.int_,
            cv.Optional(CONF_VSYNC_BACK_PORCH, default=20): cv.int_,
            cv.Optional(CONF_VSYNC_FRONT_PORCH, default=10): cv.int_,
            cv.Optional(CONF_POWER_SUPPLY): cv.use_id(power_supply.PowerSupply),
            cv.Required(CONF_HEIGHT): cv.int_,
            cv.Required(CONF_WIDTH): cv.int_,
        }
    )
    .extend(cv.polling_component_schema("5s"))
    .extend(spi.spi_device_schema(cs_pin_required=False)),
    cv.only_with_esp_idf,
)


async def to_code(config):
    # cg.add_library("esp_lcd")
    print(config[CONF_INIT_SEQUENCE])
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await spi.register_spi_device(var, config)

    cg.add(var.set_init_sequence(config[CONF_INIT_SEQUENCE]))
    cg.add(var.set_height(config[CONF_HEIGHT]))
    cg.add(var.set_width(config[CONF_WIDTH]))
    index = 0
    for pin in config[CONF_DATA_PINS]:
        data_pin = await cg.gpio_pin_expression(pin)
        cg.add(var.add_data_pin(data_pin, index))
        index += 1

    if CONF_DC_PIN in config:
        dc = await cg.gpio_pin_expression(config[CONF_DC_PIN])
        cg.add(var.set_dc_pin(dc))

    if CONF_RESET_PIN in config:
        reset = await cg.gpio_pin_expression(config[CONF_RESET_PIN])
        cg.add(var.set_reset_pin(reset))

    if CONF_BACKLIGHT_PIN in config and config[CONF_BACKLIGHT_PIN]:
        bl = await cg.gpio_pin_expression(config[CONF_BACKLIGHT_PIN])
        cg.add(var.set_backlight_pin(bl))

    if CONF_POWER_SUPPLY in config:
        ps = await cg.get_variable(config[CONF_POWER_SUPPLY])
        cg.add(var.set_power_supply(ps))
    pin = await cg.gpio_pin_expression(config[CONF_DE_PIN])
    cg.add(var.set_de_pin(pin))
    pin = await cg.gpio_pin_expression(config[CONF_PCLK_PIN])
    cg.add(var.set_pclk_pin(pin))
    pin = await cg.gpio_pin_expression(config[CONF_HSYNC_PIN])
    cg.add(var.set_hsync_pin(pin))
    pin = await cg.gpio_pin_expression(config[CONF_VSYNC_PIN])
    cg.add(var.set_vsync_pin(pin))
