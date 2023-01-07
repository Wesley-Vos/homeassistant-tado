# pyright: ignore
"""Support for Tado selects for each zone."""
import logging

from homeassistant.components.select import SelectEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    NUMBER_OF_PRESET_MODES,
    STORE,
    FANSPEED,
    PRESET_MODES,
    VERTICAL_SWING_MODE,
    HORIZONTAL_SWING_MODE,
)

_LOGGER = logging.getLogger(__name__)

MODE_TO_OPTIONS_MAPPING = {
    HORIZONTAL_SWING_MODE: [
        "LEFT",
        "MID_LEFT",
        "MID",
        "MID_RIGHT",
        "RIGHT",
        "ON",
        "OFF",
    ],
    VERTICAL_SWING_MODE: ["UP", "MID_UP", "MID", "MID_DOWN", "DOWN", "ON", "OFF"],
    FANSPEED: ["auto", "Level 1", "Level 2", "Level 3", "Level 4"],
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Tado sensor platform."""
    store = hass.data[DOMAIN][entry.entry_id][STORE]

    entities: list[SelectEntity] = []

    for i in range(1, NUMBER_OF_PRESET_MODES + 1):
        entities.extend(
            [
                TadoPresetModeSelect(i, mode, store, hass)
                for mode in MODE_TO_OPTIONS_MAPPING
            ]
        )

    if entities:
        async_add_entities(entities, True)


class TadoPresetModeSelect(SelectEntity, RestoreEntity):
    """Preset mode selects for swing and fan speed"""

    def __init__(self, i, mode, store, hass):
        self._hass = hass
        super().__init__()

        self.store = store
        self.i = i
        self.mode = mode

        # self.zone_variable = zone_variable
        self._attr_name = f"{DOMAIN} preset mode { i } { mode }"
        self._attr_unique_id = f"select_{DOMAIN}_{i}_{mode}"

        # self._current_option = None

        self._options = MODE_TO_OPTIONS_MAPPING[mode]

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state and state.state in self._options:
            self.store[PRESET_MODES][self.i][self.mode] = state.state

    @property
    def options(self) -> list[str]:
        """Return the available options."""
        return self._options

    @property
    def current_option(self) -> str:
        """Return current options."""
        return self.store[PRESET_MODES][self.i][self.mode]

    async def async_select_option(self, option: str) -> None:
        """Select new (option)."""
        self.store[PRESET_MODES][self.i][self.mode] = option
        self.async_write_ha_state()
