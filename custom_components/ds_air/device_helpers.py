"""Helpers for looking up devices in the Home Assistant device registry."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN


def schedule_update_if_enabled(entity) -> None:
    """Schedule a state update only when the entity is enabled.

    Service-layer status hooks run for every entity, including ones the user
    disabled. Calling schedule_update_ha_state() on a disabled entity makes HA
    log an error, so skip it while still updating the cached state.
    """
    if entity.enabled:
        entity.schedule_update_ha_state()


def find_device(
    hass: HomeAssistant, identifier: tuple[str, str], config_entry_id: str
):
    """Find a device by identifier within a config entry.

    HA 2025.7+ deprecated ``async_get_device`` because identifiers are only
    unique within a config entry. Prefer the scoped lookup and fall back to
    the legacy API for older Home Assistant versions.
    """
    registry = dr.async_get(hass)
    lookup = getattr(registry, "async_get_device_by_identifier", None)
    if lookup is not None:
        try:
            return lookup(identifier, config_entry_id)
        except (KeyError, ValueError):
            return None
    return registry.async_get_device(identifiers={identifier})


def get_device_id_by_gateway(
    hass: HomeAssistant, gateway_id: str, config_entry_id: str
) -> str | None:
    """Return the registry id of the gateway device, or None if not found."""
    device = find_device(hass, (DOMAIN, gateway_id), config_entry_id)
    return device.id if device is not None else None
