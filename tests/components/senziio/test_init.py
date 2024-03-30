"""Test for Senziio device entry registration."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.senziio import (
    DOMAIN,
    PLATFORMS,
    async_setup_entry,
    async_unload_entry,
)
from homeassistant.components.senziio.const import MANUFACTURER
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from . import (
    A_DEVICE_ID,
    A_DEVICE_MODEL,
    A_FRIENDLY_NAME,
    CONFIG_ENTRY,
    DEVICE_INFO,
    FakeSenziio,
)


async def test_async_setup_entry(hass: HomeAssistant):
    """Test registering a Senziio device."""
    CONFIG_ENTRY.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.mqtt.async_wait_for_mqtt_client",
            return_value=True,
        ),
        patch(
            "homeassistant.components.senziio.senziio_api.Senziio",
            return_value=FakeSenziio(DEVICE_INFO),
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", return_value=AsyncMock()
        ) as forward_entry_mock,
    ):
        # verify entry is forwarded to platforms
        assert await async_setup_entry(hass, CONFIG_ENTRY) is True
        forward_entry_mock.assert_awaited_once_with(CONFIG_ENTRY, PLATFORMS)

    # verify device registry data
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, A_DEVICE_ID)})

    assert device is not None
    assert device.manufacturer == MANUFACTURER
    assert device.model == A_DEVICE_MODEL
    assert device.name == A_FRIENDLY_NAME
    assert device.sw_version == "1.2.3"
    assert device.hw_version == "1.0.0"
    assert device.serial_number == "theia-pro-2F3D56AA1234"
    assert device.connections == {("mac", "1a:2b:3c:4d:5e:6f")}


async def test_do_not_setup_entry_if_mqtt_is_not_available(hass: HomeAssistant):
    """Test behavior without MQTT integration enabled."""
    CONFIG_ENTRY.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.mqtt.async_wait_for_mqtt_client",
            return_value=False,
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", return_value=AsyncMock()
        ) as forward_entry_mock,
    ):
        assert await async_setup_entry(hass, CONFIG_ENTRY) is False
        forward_entry_mock.assert_not_awaited()


async def test_async_unload_entry(hass: HomeAssistant):
    """Test unloading a Senziio entry."""
    CONFIG_ENTRY.add_to_hass(hass)

    with (
        patch(
            "homeassistant.components.mqtt.async_wait_for_mqtt_client",
            return_value=True,
        ),
        patch(
            "homeassistant.components.senziio.senziio_api.Senziio",
            return_value=FakeSenziio(DEVICE_INFO),
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", return_value=AsyncMock()
        ),
        patch.object(
            hass.config_entries, "async_unload_platforms", return_value=True
        ) as unload_platforms_mock,
    ):
        await async_setup_entry(hass, CONFIG_ENTRY)
        assert CONFIG_ENTRY.entry_id in hass.data[DOMAIN]

        # verify entry is correctly unloaded
        assert await async_unload_entry(hass, CONFIG_ENTRY) is True
        assert CONFIG_ENTRY.entry_id not in hass.data[DOMAIN]
        unload_platforms_mock.assert_called_once_with(CONFIG_ENTRY, PLATFORMS)
