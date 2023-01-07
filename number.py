# pyright: ignore
"""Support for Tado selects for each zone."""
import logging

from homeassistant.components.number import NumberEntity, RestoreNumber

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, NUMBER_OF_PRESET_MODES, PRESET_MODES, STORE, TEMPERATURE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Tado sensor platform."""

    store = hass.data[DOMAIN][entry.entry_id][STORE]

    entities: list[NumberEntity] = []

    entities.extend(
        [
            TadoPresetModeNumber(i, store, hass)
            for i in range(1, NUMBER_OF_PRESET_MODES + 1)
        ]
    )

    if entities:
        async_add_entities(entities, True)


class TadoPresetModeNumber(RestoreNumber, NumberEntity):
    """Tado preset mode number"""

    def __init__(self, i, store, hass):
        self._hass = hass
        super().__init__()

        self.store = store
        self.i = i
        self._attr_name = f"{DOMAIN} preset mode { i } temperature"
        self._attr_unique_id = f"number_{DOMAIN}_{i}_temperature"
        self._state = 0

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_number_data()
        if state and state.native_value:
            self.store[PRESET_MODES][self.i][TEMPERATURE] = state.native_value

    @property
    def native_min_value(self) -> float:
        return 18

    @property
    def native_max_value(self) -> float:
        return 30

    @property
    def native_step(self) -> float:
        return 1

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        return self.store[PRESET_MODES][self.i][TEMPERATURE]

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.store[PRESET_MODES][self.i][TEMPERATURE] = value
        self.async_write_ha_state()
