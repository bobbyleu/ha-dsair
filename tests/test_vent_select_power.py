"""Tests for DS-AIR ventilation select entities power-on behavior.

Regression: switching ventilation mode / air flow while the device is off
only sent the mode/flow field, so the fan kept running off. Select now also
carries switch=ON. select.py is loaded under the same lightweight stub env
used by test_fan_vent_power.py to avoid unavailable cloud dependencies.
"""
from pathlib import Path
import select as _stdlib_select  # noqa: F401 — preload stdlib select
import sys
import types
import unittest
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "custom_components" / "ds_air"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PKG_DIR))

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
ha_entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
ha_entity_platform.AddEntitiesCallback = object
sys.modules["homeassistant.helpers.entity_platform"] = ha_entity_platform
ha_entity = types.ModuleType("homeassistant.helpers.entity")
ha_entity.DeviceInfo = dict
sys.modules["homeassistant.helpers.entity"] = ha_entity

ha_select = types.ModuleType("homeassistant.components.select")
ha_select.SelectEntity = object
sys.modules["homeassistant.components.select"] = ha_select

pkg = types.ModuleType("ds_air_select_under_test")
pkg.__path__ = [str(PKG_DIR)]
sys.modules["ds_air_select_under_test"] = pkg
const_stub = types.ModuleType("ds_air_select_under_test.const")
const_stub.DOMAIN = "ds_air"
const_stub.MANUFACTURER = "Daikin Industries, Ltd."
sys.modules["ds_air_select_under_test.const"] = const_stub
dh_stub = types.ModuleType("ds_air_select_under_test.device_helpers")
dh_stub.get_device_id_by_gateway = lambda *a, **k: None
dh_stub.schedule_update_if_enabled = lambda entity: None
sys.modules["ds_air_select_under_test.device_helpers"] = dh_stub

import ds_air_service  # noqa: E402
sys.modules["ds_air_select_under_test.ds_air_service"] = ds_air_service
sys.modules["ds_air_select_under_test.ds_air_service.dao"] = ds_air_service.dao

spec = importlib.util.spec_from_file_location(
    "ds_air_select_under_test.select", PKG_DIR / "select.py"
)
select_mod = importlib.util.module_from_spec(spec)
sys.modules["ds_air_select_under_test.select"] = select_mod
spec.loader.exec_module(select_mod)

from ds_air_service.ctrl_enum import EnumControl  # noqa: E402
from ds_air_service.dao import Ventilation  # noqa: E402


class FakeService:
    def __init__(self):
        self.calls = []

    def control_vent(self, vent, status):
        self.calls.append(status)

    def register_vent_hook(self, vent, hook):
        pass


class VentSelectPowerTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.vent = Ventilation()
        self.vent.alias = "新风"
        self.vent.is_small_vam = True
        self.vent.room_id = 1
        self.vent.unit_id = 1
        self.vent.gateway_id = "gw"
        self.vent.status.switch = EnumControl.Switch.OFF
        self.vent.status.mode = EnumControl.Mode(0)
        self.vent.status.air_flow = EnumControl.AirFlow.WEAK

    def test_mode_select_turns_on_off_device(self):
        entity = select_mod.DsVentModeSelect(self.vent, self.service, "entry")
        entity.select_option("自动")
        sent = self.service.calls[-1]
        self.assertEqual(sent.switch, EnumControl.Switch.ON)
        self.assertEqual(sent.mode, EnumControl.Mode(2))

    def test_airflow_select_turns_on_off_device(self):
        entity = select_mod.DsVentAirFlowSelect(self.vent, self.service, "entry")
        entity.select_option("高速")
        sent = self.service.calls[-1]
        self.assertEqual(sent.switch, EnumControl.Switch.ON)
        self.assertEqual(sent.air_flow, EnumControl.AirFlow.STRONG)

    def test_mode_select_on_device_keeps_switch_untouched(self):
        self.vent.status.switch = EnumControl.Switch.ON
        entity = select_mod.DsVentModeSelect(self.vent, self.service, "entry")
        entity.select_option("热交换")
        sent = self.service.calls[-1]
        self.assertIsNone(sent.switch)


if __name__ == "__main__":
    unittest.main()
