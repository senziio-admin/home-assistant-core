"""Fakes for testing."""


class FakeSenziio:
    """Fake Senziio device for testing."""

    def __init__(self, device_info: dict) -> None:
        """Initialize with expected info."""
        self._device_info = device_info

    async def get_info(self) -> dict[str, str]:
        """Get device info."""
        return self._device_info
