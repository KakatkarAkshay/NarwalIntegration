"""Constants for the Narwal vacuum integration."""

from homeassistant.const import Platform

from .narwal_client import AmbientLightCtrlType, FanLevel

DOMAIN = "narwal"
DEFAULT_PORT = 9002

MANUFACTURER = "Narwal"
MODEL = "Flow (AX12)"

# Model selector for config flow.
# Keys are user-facing labels; values are product key prefixes.
# "auto" cycles all known keys during discovery (slower, fallback).
NARWAL_MODELS: dict[str, str] = {
    "Narwal Flow": "QoEsI5qYXO",
    "Narwal Flow 2": "QxMSPG6VSO",
    "Narwal Freo Z10 Ultra": "DrzDKQ0MU8",
    # AX26 ships under two marketing names on identical firmware (v01.02.00.15):
    # "Z10 Turbo" (@romedtino, #40) and "Z10 Pro" (@shin906710, #70), same product_key.
    "Narwal Freo Z10 Pro / Turbo": "qV6BujoYLz",
    "Narwal Freo X10 Pro": "CNbforyZWI",
    "Other / Auto-detect": "auto",
}

CONF_MODEL = "model"
CONF_PRODUCT_KEY = "product_key"

PLATFORMS: list[Platform] = [
    Platform.VACUUM,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.LIGHT,
]

CONF_DOCK_LIGHT_SUPPORTED = "dock_light_supported"

DOCK_LIGHT_PRODUCT_KEYS = {"QxMSPG6VSO", "iSuVlI1If2"}


def is_dock_light_supported(data: dict, options: dict | None = None) -> bool:
    """Return whether this configured model exposes dock ambient lighting."""
    if options and CONF_DOCK_LIGHT_SUPPORTED in options:
        return bool(options[CONF_DOCK_LIGHT_SUPPORTED])
    return data.get(CONF_PRODUCT_KEY) in DOCK_LIGHT_PRODUCT_KEYS


DOCK_LIGHT_MODES: dict[str, AmbientLightCtrlType] = {
    "Off": AmbientLightCtrlType.OFF,
    "Fireplace": AmbientLightCtrlType.WINTER_WARMTH,
    "Nightlight": AmbientLightCtrlType.NIGHT_LIGHT,
    "Purple": AmbientLightCtrlType.PURPLE_LIGHT,
}
DOCK_LIGHT_MODE_NAMES: dict[int, str] = {
    int(value): key for key, value in DOCK_LIGHT_MODES.items()
}

FAN_SPEED_MAP: dict[str, FanLevel] = {
    "quiet": FanLevel.QUIET,
    "normal": FanLevel.NORMAL,
    "strong": FanLevel.STRONG,
    "max": FanLevel.MAX,
}

FAN_SPEED_LIST: list[str] = list(FAN_SPEED_MAP.keys())

# Best-effort help-center deep link for a robot error code. The app's goHelpCenterByCode
# builds <localized help base>?code=<n>&deviceId=…&lang=…; the exact base is a runtime
# i18n value we can't read, so this is inferred from the Flow's help-center family and
# should be corrected if a real error opens a different path. The raw code is the fallback.
ERROR_HELP_URL_TEMPLATE = (
    "https://help.narwal.com/helpcenter/vall/#/p2/question/all?eType=1&code={code}&lang=en-US"
)
