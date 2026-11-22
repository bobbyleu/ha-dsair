"""Tests for DS-AIR ventilation fan power handling via set_percentage/preset_mode.

Regression: HomeKit sends Active=1 together with Rotation Speed, and HA's
HomeKit bridge only calls fan.set_percentage in that case. For small VAM the
old set_percentage never set switch=ON, so the fan only changed speed and
did not start. These tests make sure the switch is always carried.

fan.py is loaded under a lightweight fake package so we get the real
const/device_helpers/ds_air_service modules without importing the integration
__init__.py (which pulls cloud/energy dependencies not installed in test env).
"""
from pathlib import Path
import select  # noqa: F401 — preload stdlib select before ds_air/select.py
import sys
import types
import unittest
from enum import IntFlag
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "custom_components" / "ds_air"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PKG_DIR))

# ---- minimal Home Assistant mocks ----
ha = types.ModuleType("homeassistant")
ha.__path__ = []
sys.modules.setdefault("homeassistant", ha)

ha_components = types.ModuleType("homeassistant.components")
ha_components.__path__ = []
sys.modules.setdefault("homeassistant.components", ha_components)

ha_const = types.ModuleType("homeassistant.const")
ha_const.MAJOR_VERSION = 2026
ha_const.MINOR_VERSION = 10
sys.modules["homeassistant.const"] = ha_const

ha_config_entries = types.ModuleType("homeassistant.config_entries")
ha_config_entries.ConfigEntry = types.SimpleNamespace
sys.modules["homeassistant.config_entries"] = ha_config_entries

ha_core = types.ModuleType("homeassistant.core")
ha_core.HomeAssistant = types.SimpleNamespace
sys.modules["homeassistant.core"] = ha_core

ha_helpers = types.ModuleType("homeassistant.helpers")
ha_helpers.__path__ = []
sys.modules.setdefault("homeassistant.helpers", ha_helpers)
ha_dr = types.ModuleType("homeassistant.helpers.device_registry")
ha_dr.async_get = lambda hass: types.SimpleNamespace()
sys.modules["homeassistant.helpers.device_registry"] = ha_dr

ha_entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
ha_entity_platform.AddEntitiesCallback = object
sys.modules["homeassistant.helpers.entity_platform"] = ha_entity_platform

ha_entity = types.ModuleType("homeassistant.helpers.entity")
ha_entity.DeviceInfo = dict
sys.modules["homeassistant.helpers.entity"] = ha_entity


class MockFanEntityFeature(IntFlag):
    SET_SPEED = 1
    TURN_ON = 2
    TURN_OFF = 4
    PRESET_MODE = 64


class MockFanEntity:
    enabled = False

    def schedule_update_ha_state(self):
        pass

    @property
    def percentage_step(self) -> float:
        return 100 / getattr(self, "_attr_speed_count", 100)


ha_fan = types.ModuleType("homeassistant.components.fan")
ha_fan.FanEntity = MockFanEntity
ha_fan.FanEntityFeature = MockFanEntityFeature
sys.modules["homeassistant.components.fan"] = ha_fan

# Load fan.py under a fake package, stubbing its light-weight relative
# dependencies so we don't import const.py (which needs climate) or the
# integration __init__.py (which needs cryptography/aiohttp).
pkg = types.ModuleType("ds_air_under_test")
pkg.__path__ = [str(PKG_DIR)]
sys.modules["ds_air_under_test"] = pkg

const_stub = types.ModuleType("ds_air_under_test.const")
const_stub.DOMAIN = "ds_air"
sys.modules["ds_air_under_test.const"] = const_stub

dh_stub = types.ModuleType("ds_air_under_test.device_helpers")
dh_stub.schedule_update_if_enabled = lambda entity: None
sys.modules["ds_air_under_test.device_helpers"] = dh_stub

import ds_air_service  # noqa: E402  (real package, resolves via PKG_DIR)
sys.modules["ds_air_under_test.ds_air_service"] = ds_air_service
sys.modules["ds_air_under_test.ds_air_service.dao"] = ds_air_service.dao

spec = importlib.util.spec_from_file_location("ds_air_under_test.fan", PKG_DIR / "fan.py")
fan_mod = importlib.util.module_from_spec(spec)
sys.modules["ds_air_under_test.fan"] = fan_mod
spec.loader.exec_module(fan_mod)

DsVent = fan_mod.DsVent

from ds_air_service.ctrl_enum import EnumControl  # noqa: E402
from ds_air_service.dao import Ventilation  # noqa: E402


class FakeService:
    def __init__(self):
        self.calls = []

    def control_vent(self, vent, status):
        self.calls.append(status)

    def register_vent_hook(self, vent, hook):
        pass


class VentPowerTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.vent = Ventilation()
        self.vent.alias = "新风"
        self.vent.is_small_vam = True
        self.vent.room_id = 1
        self.vent.unit_id = 1
        self.vent.status.switch = EnumControl.Switch.OFF
        self.vent.status.air_flow = EnumControl.AirFlow.WEAK
        self.fan = DsVent(self.vent, self.service)

    def last(self):
        return self.service.calls[-1]

    def test_small_vam_set_percentage_turns_on_off_device(self):
        """Off device + set speed must send switch=ON (HomeKit automation path)."""
        self.fan.set_percentage(25)

        sent = self.last()
        self.assertEqual(sent.switch, EnumControl.Switch.ON)
        self.assertEqual(sent.air_flow, EnumControl.AirFlow.WEAK)
        self.assertEqual(self.vent.status.switch, EnumControl.Switch.ON)

    def test_small_vam_set_percentage_zero_turns_off(self):
        """Speed 0 must send switch=OFF so the fan can be stopped by speed."""
        self.vent.status.switch = EnumControl.Switch.ON
        self.fan.set_percentage(0)

        sent = self.last()
        self.assertEqual(sent.switch, EnumControl.Switch.OFF)
        self.assertEqual(self.vent.status.switch, EnumControl.Switch.OFF)

    def test_small_vam_set_percentage_on_device_keeps_switch_untouched(self):
        """Already-on device: no redundant switch command, only speed."""
        self.vent.status.switch = EnumControl.Switch.ON
        self.fan.set_percentage(50)

        sent = self.last()
        self.assertIsNone(sent.switch)
        self.assertEqual(sent.air_flow, EnumControl.AirFlow.MIDDLE)

    def test_small_vam_set_preset_mode_turns_on_off_device(self):
        """HomeKit preset switch only calls set_preset_mode; must also power on."""
        self.fan.set_preset_mode("自动")

        sent = self.last()
        self.assertEqual(sent.switch, EnumControl.Switch.ON)
        self.assertEqual(sent.mode, EnumControl.Mode(2))
        self.assertEqual(self.vent.status.switch, EnumControl.Switch.ON)

    def test_small_vam_set_preset_mode_on_device_keeps_switch_untouched(self):
        self.vent.status.switch = EnumControl.Switch.ON
        self.fan.set_preset_mode("自动")

        sent = self.last()
        self.assertIsNone(sent.switch)
        self.assertEqual(sent.mode, EnumControl.Mode(2))


class StandardVamPowerTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.vent = Ventilation()
        self.vent.alias = "新风"
        self.vent.is_small_vam = False
        self.vent.room_id = 2
        self.vent.unit_id = 1
        self.vent.status.switch = EnumControl.Switch.OFF
        self.vent.status.air_flow = EnumControl.AirFlow.WEAK
        self.fan = DsVent(self.vent, self.service)

    def test_standard_vam_set_percentage_turns_on(self):
        self.fan.set_percentage(20)
        sent = self.service.calls[-1]
        self.assertEqual(sent.switch, EnumControl.Switch.ON)
        self.assertEqual(sent.air_flow, EnumControl.AirFlow.WEAK)

    def test_standard_vam_set_percentage_zero_turns_off(self):
        self.vent.status.switch = EnumControl.Switch.ON
        self.fan.set_percentage(0)
        sent = self.service.calls[-1]
        self.assertEqual(sent.switch, EnumControl.Switch.OFF)


if __name__ == "__main__":
    unittest.main()
