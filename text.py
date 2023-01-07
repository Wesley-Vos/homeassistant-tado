# pyright: ignore
"""Support for Tado selects for each zone."""
import logging

from homeassistant.components.text import TextEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, NAME, PRESET_MODES, STORE, NUMBER_OF_PRESET_MODES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Tado sensor platform."""

    store = hass.data[DOMAIN][entry.entry_id][STORE]

    entities: list[TextEntity] = []

    entities.extend(
        [
            TadoPresetModeText(i, store, hass)
            for i in range(1, NUMBER_OF_PRESET_MODES + 1)
        ]
    )

    if entities:
        async_add_entities(entities, True)


class TadoPresetModeText(TextEntity, RestoreEntity):
    """Tado preset mode text"""

    def __init__(self, i, store, hass):
        self._hass = hass
        super().__init__()

        self.i = i
        self.store = store
        self._attr_name = f"{DOMAIN} preset mode {i} name"
        self._attr_unique_id = f"text_{DOMAIN}_{i}_name"
        self._state = 0

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if state and state.state:
            self.store[PRESET_MODES][self.i][NAME] = state.state

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        return self.store[PRESET_MODES][self.i][NAME]

    async def async_set_value(self, value: str) -> None:
        """Update the current value."""
        self.store[PRESET_MODES][self.i][NAME] = value
        self.async_write_ha_state()
