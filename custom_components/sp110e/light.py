"""Platform for light integration."""
from __future__ import annotations
from typing import Any, Union
import logging
from datetime import timedelta
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.components.light import (LightEntity, ATTR_BRIGHTNESS, ATTR_RGBW_COLOR, ATTR_EFFECT, PLATFORM_SCHEMA,
                                            COLOR_MODE_RGBW, SUPPORT_EFFECT)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.device_registry import format_mac
from homeassistant.util import Throttle
from sp110e.controller import Controller

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration

ADD_EFFECTS_SCHEMA = vol.Schema([{
    vol.Required('name'): cv.string,
    vol.Optional('state', default=True): bool,
    vol.Optional('mode', default=None): vol.Any(cv.positive_int, None),
    vol.Optional('speed', default=None): vol.Any(cv.positive_int, None),
    vol.Optional('brightness', default=None): vol.Any(cv.positive_int, None),
    vol.Optional('color', default=None): vol.Any(list, None),
    vol.Optional('white', default=None): vol.Any(cv.positive_int, None)
}])

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required('mac'): cv.string,
    vol.Optional('name', default='SP110E'): cv.string,
    vol.Optional('ic_model', default=''): cv.string,
    vol.Optional('sequence', default=''): cv.string,
    vol.Optional('pixels', default=0): cv.positive_int,
    vol.Optional('speed', default=256): cv.positive_int,
    vol.Optional('strict', default=False): cv.boolean,
    vol.Optional('add_effects', default=[]): ADD_EFFECTS_SCHEMA
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
    mac = config['mac']
    name = config['name']
    ic_model = config['ic_model']
    sequence = config['sequence']
    pixels = config['pixels']
    speed = config['speed']
    strict = config['strict']
    add_effects = config['add_effects']
    # Initialize device driver
    device = Controller(mac)
    # Add device
    sp110e_entity = SP110EEntity(
        device,
        name=name,
        ic_model=ic_model,
        sequence=sequence,
        pixels=pixels,
        speed=speed,
        strict=strict,
        add_effects=add_effects
    )
    add_entities([sp110e_entity])
    try:
        await sp110e_entity.async_update()
    except:
        pass


class SP110EEntity(LightEntity):
    """Representation of an SP110E device."""

    def __init__(
            self,
            device: Controller,
            name: str,
            ic_model: str,
            sequence: str,
            pixels: int,
            speed: int,
            strict: bool,
            add_effects: Union[list, None]
    ) -> None:
        """Initialize object."""
        self._device = device
        self._name = name
        self._ic_model = ic_model
        self._sequence = sequence
        self._pixels = pixels
        self._speed = speed
        self._strict = strict
        self._state = False
        self._brightness = 0
        self._rgbw = (0, 0, 0, 0)
        self._configured = False
        if add_effects:
            effects = add_effects
        else:
            effects = []
        modes: [int] = self._device.get_modes()
        for mode in modes:
            effects.append({'name': str(mode), 'mode': mode})
        for effect in effects:
            preset = {'name': effect.get('name'), 'state': bool(effect.get('state', True))}
            mode = effect.get('mode', None)
            preset['mode'] = int(mode) if mode is not None else None
            speed = effect.get('speed', None)
            preset['speed'] = int(speed) if speed is not None else None
            brightness = effect.get('brightness', None)
            preset['brightness'] = int(brightness) if brightness is not None else None
            color = effect.get('color', None)
            preset['color'] = list(color) if color is not None else None
            white = effect.get('white', None)
            preset['white'] = int(white) if white is not None else None
            self._device.add_preset(preset)
        self._effect = None

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def unique_id(self) -> str:
        return format_mac(self._device.get_mac_address())

    @property
    def supported_color_modes(self) -> list:
        return [COLOR_MODE_RGBW]

    @property
    def supported_features(self) -> str:
        return SUPPORT_EFFECT

    @property
    def effect_list(self) -> [str]:
        presets = self._device.get_presets()
        if presets:
            effects = [preset['name'] for preset in presets]
        else:
            effects = []
        return effects

    @property
    def effect(self) -> str:
        if self._effect is None:
            self._effect = str(self._device.get_mode())
        return self._effect

    @property
    def color_mode(self):
        return COLOR_MODE_RGBW

    @property
    def name(self) -> str:
        """Return the display name of device."""
        return self._name

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self._brightness

    @property
    def rgbw_color(self) -> (int, int, int, int):
        return self._rgbw

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    @Throttle(timedelta(seconds=0.1))
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, None)
        rgbw_color = kwargs.get(ATTR_RGBW_COLOR, None)
        effect = kwargs.get(ATTR_EFFECT, None)
        try:
            await self._configure()
            await self._device.switch_on()
            if brightness is not None:
                await self._device.set_brightness(brightness)
            if rgbw_color is not None:
                color = [rgbw_color[0], rgbw_color[1], rgbw_color[2]]
                white = rgbw_color[3]
                await self._device.set_color(color)
                await self._device.set_white(white)
            if effect is not None:
                await self._device.set_preset(effect)
                self._effect = effect
            self._get_parameters()
        except Exception as exception:
            self._handle_exception(exception)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        try:
            await self._device.switch_off(force=True)
            self._get_parameters()
        except Exception as exception:
            self._handle_exception(exception)

    @Throttle(timedelta(seconds=1))
    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        try:
            await self._device.update()
            self._get_parameters()
        except Exception as exception:
            self._handle_exception(exception)

    def _get_parameters(self):
        """Get parameters from device."""
        self._state = self._device.get_state()
        self._brightness = self._device.get_brightness()
        color = self._device.get_color()
        white = self._device.get_white()
        self._rgbw = (color[0], color[1], color[2], white)

    async def _configure(self):
        """Configure device."""
        if not self._configured:
            if self._ic_model:
                await self._device.set_ic_model(self._ic_model)
            if self._sequence:
                await self._device.set_sequence(self._sequence)
            if self._pixels:
                await self._device.set_pixels(self._pixels)
            if self._speed < 256:
                await self._device.set_speed(self._speed)
            self._configured = True

    def _handle_exception(self, exception):
        """Handle device exception."""
        if self._strict:
            raise exception
        else:
            pass
