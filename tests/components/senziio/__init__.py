"""Tests for the Senziio integration."""

from ipaddress import ip_address

from homeassistant.components import zeroconf

A_DEVICE_ID = "theia-pro-2F3D56AA1234"
A_DEVICE_MODEL = "Theia Pro"
A_FRIENDLY_NAME = "A Friendly Name"
ANOTHER_DEVICE_ID = "theia-pro-AD2BF63DF999"

DEVICE_INFO = {
    "model": "Theia Pro",
    "fw-version": "1.2.3",
    "hw-version": "1.0.0",
    "mac-address": "1A:2B:3C:4D:5E:6F",
    "serial-number": "theia-pro-2F3D56AA1234",
}

ZEROCONF_DISCOVERY_INFO = zeroconf.ZeroconfServiceInfo(
    ip_address=ip_address("1.1.1.1"),
    ip_addresses=[ip_address("1.1.1.1")],
    hostname=f"senziio-{A_DEVICE_ID}.local.",
    name=f"senziio-{A_DEVICE_ID}._http._tcp.local.",
    port=0,
    properties={
        "device_id": A_DEVICE_ID,
        "device_model": A_DEVICE_MODEL,
    },
    type="_http._tcp.local.",
)


class FakeSenziio:
    """Fake Senziio device for testing."""

    def __init__(self, device_info: dict) -> None:
        """Initialize with expected info."""
        self._device_info = device_info

    async def get_info(self) -> dict[str, str]:
        """Get device info."""
        return self._device_info
