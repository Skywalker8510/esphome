import sys

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number
from esphome.const import (
    CONF_ID,
    CONF_VALUE,
)
from . import (
    lvgl_ns,
    LVGL_SCHEMA,
    lv_arc_t,
    lv_slider_t,
    CONF_LVGL_ID,
    add_init_lambda,
    CONF_ANIMATED,
    lv_animated,
    set_event_cb,
    CONF_SLIDER,
    CONF_ARC,
)

LVGLNumber = lvgl_ns.class_("LVGLNumber", number.Number)

CONFIG_SCHEMA = (
    number.number_schema(LVGLNumber)
    .extend(LVGL_SCHEMA)
    .extend(
        {
            cv.Exclusive(CONF_ARC, CONF_VALUE): cv.use_id(lv_arc_t),
            cv.Exclusive(CONF_SLIDER, CONF_VALUE): cv.use_id(lv_slider_t),
            cv.Optional(CONF_ANIMATED, default=True): lv_animated,
        }
    )
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await number.register_number(
        var, config, max_value=sys.maxsize, min_value=-sys.maxsize, step=1
    )

    animated = config[CONF_ANIMATED]
    paren = await cg.get_variable(config[CONF_LVGL_ID])
    if arc := config.get(CONF_ARC):
        obj = await cg.get_variable(arc)
        lv_type = "arc"
    elif slider := config.get(CONF_SLIDER):
        obj = await cg.get_variable(slider)
        lv_type = "slider"
    else:
        return
    init = set_event_cb(
        obj,
        f"   {var}->publish_state(lv_{lv_type}_get_value({obj}));\n",
        "LV_EVENT_VALUE_CHANGED",
        f"{paren}->get_custom_change_event()",
    ) + [
        f"{var}->set_control_lambda([] (float v) {{\n"
        f"  lv_{lv_type}_set_value({obj}, v, {animated});\n"
        "})"
    ]
    init.extend(
        [
            f"{var}->traits.set_max_value(lv_{lv_type}_get_max_value({obj}))",
            f"{var}->traits.set_min_value(lv_{lv_type}_get_min_value({obj}))",
        ]
    )
    await add_init_lambda(paren, init)
