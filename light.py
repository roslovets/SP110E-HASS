"""Platform for light integration."""
from __future__ import annotations
import logging
import asyncio
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity)
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from SP110E.Controller import Controller

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
})


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
    add_entities([SP110E(device)])


class SP110E(LightEntity):
    """Representation of an SP110E device."""

    def __init__(self, device) -> None:
        """Initialize object."""
        self._device = device
        self._name = 'SP110E'
        self._state = False
        self._brightness = 0

    @property
    def name(self) -> str:
        """Return the display name of device."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        await self._device.connect()
        await self._device.switch_on()
        await self._device.set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))
        self._state = self._device.is_on()
        self._brightness = self._device.get_brightness()
        await self._device.disconnect()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self._device.connect()
        await self._device.switch_off()
        self._state = self._device.is_on()
        self._brightness = self._device.get_brightness()
        await self._device.disconnect()

    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        pass
