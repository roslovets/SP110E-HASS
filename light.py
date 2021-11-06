"""Platform for light integration."""
from __future__ import annotations
import logging
import asyncio
from datetime import timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_RGBW_COLOR, ATTR_EFFECT, PLATFORM_SCHEMA, LightEntity,
                                            COLOR_MODE_ONOFF, COLOR_MODE_BRIGHTNESS, COLOR_MODE_RGB, COLOR_MODE_RGBW,
                                            SUPPORT_EFFECT)
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.device_registry import format_mac
from homeassistant.util import Throttle
from SP110E.Controller import Controller

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
})
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up SP110E platform."""
    # Assign configuration variables
    mac = config[CONF_MAC]
    # Initialize device driver
    device = Controller(mac)
    # Add device
    entity = SP110E(device)
    add_entities([entity])
    try:
        await entity.async_update()
    except:
        pass


class SP110E(LightEntity):
    """Representation of an SP110E device."""

    def __init__(self, device) -> None:
        """Initialize object."""
        self._device = device
        self._name = 'SP110E'
        self._state = False
        self._brightness = 0
        self._rgbw = (0, 0, 0, 0)

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def unique_id(self) -> str:
        return format_mac(self._device.get_mac_address())

    @property
    def supported_color_modes(self):
        return [COLOR_MODE_RGBW]

    @property
    def supported_features(self):
        return SUPPORT_EFFECT

    @property
    def effect_list(self):
        modes = self._device.get_modes()
        return [str(mode) for mode in modes]

    @property
    def effect(self):
        mode = self._device.get_mode()
        return str(mode)

    @property
    def color_mode(self):
        return COLOR_MODE_RGBW

    @property
    def name(self) -> str:
        """Return the display name of device."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def rgbw_color(self):
        return self._rgbw

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    @Throttle(timedelta(seconds=0.1))
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        if not self._device.is_on():
            await self._device.switch_on()
        brightness = kwargs.get(ATTR_BRIGHTNESS, None)
        rgbw_color = kwargs.get(ATTR_RGBW_COLOR, None)
        effect = kwargs.get(ATTR_EFFECT, None)
        if brightness is not None and brightness != self._device.get_brightness():
            await self._device.set_brightness(brightness)
        if rgbw_color is not None:
            color = [rgbw_color[0], rgbw_color[1], rgbw_color[2]]
            white = rgbw_color[3]
            if color != self._device.get_color():
                await self._device.set_color(color)
            if white != self._device.get_white():
                await self._device.set_white(white)
        if effect is not None and int(effect) != self._device.get_mode():
            await self._device.set_mode(int(effect))
        self.__get_parameters()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self._device.switch_off()
        self.__get_parameters()

    @Throttle(timedelta(seconds=1))
    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        self._device.update()
        self.__get_parameters()

    def __get_parameters(self):
        """Get parameters from device."""
        self._state = self._device.is_on()
        self._brightness = self._device.get_brightness()
        color = self._device.get_color()
        white = self._device.get_white()
        self._rgbw = (color[0], color[1], color[2], white)
