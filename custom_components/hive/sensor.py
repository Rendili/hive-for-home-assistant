"""
Support for the Hive devices.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.hive/
"""

from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF, PRESET_BOOST)
from homeassistant.components.hive import DOMAIN, HiveEntity
from homeassistant.const import (STATE_OFF, STATE_ON, TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.icon import icon_for_battery_level

DEPENDENCIES = ['hive']

FRIENDLY_NAMES = {'Heating_CurrentTemperature': "Current Temperature",
                  'Heating_TargetTemperature': "Target Temperature",
                  'Heating_State': "Heating State",
                  'Heating_Mode': "Heating Mode",
                  'Heating_Boost': "Heating Boost",
                  'HotWater_State': "Hot Water State",
                  'HotWater_Mode': "Hot Water Mode",
                  'HotWater_Boost': "Hot Water Boost",
                  'Hub_OnlineStatus': 'Hive Hub Status',
                  'Hive_OutsideTemperature': 'Outside Temperature'}
DEVICETYPE_ICONS = {'Heating_CurrentTemperature': 'mdi:thermometer',
                    'Heating_TargetTemperature': 'mdi:thermometer',
                    'Heating_State': 'mdi:radiator',
                    'Heating_Mode': 'mdi:radiator',
                    'Heating_Boost': 'mdi:radiator',
                    'HotWater_State': 'mdi:water-pump',
                    'HotWater_Mode': 'mdi:water-pump',
                    'HotWater_Boost': 'mdi:water-pump',
                    'Hive_Device_Light_Mode': 'mdi:eye',
                    'Hive_Device_Plug_Mode': 'mdi:eye',
                    'Hub_OnlineStatus': 'mdi:switch',
                    'Hive_OutsideTemperature': 'mdi:thermometer'}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Hive sensor devices."""
    if discovery_info is None:
        return

    session = hass.data[DOMAIN][entry.entry_id]
    devs = []
    for dev in discovery_info:
        devs.append(HiveSensorEntity(session, dev))
    add_entities(devs)


class HiveSensorEntity(HiveEntity, Entity):
    """Hive Sensor Entity."""

    def __init__(self, hive_session, hive_device):
        """Initialize the sensor."""
        super().__init__(hive_session, hive_device)
        if self.device_type == "Hive_Device_BatteryLevel":
            self.batt_lvl = None

    @property
    def unique_id(self):
        """Return unique ID of entity."""
        return self._unique_id

    @property
    def device_info(self):
        """Return device information."""
        return {
            'identifiers': {
                (DOMAIN, self.unique_id)
            },
            'name': self.name
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        friendly_name = "Sensor"

        if self.device_type == "Hive_Device_BatteryLevel":
            if self.node_device_type == "thermostatui":
                friendly_name = "Thermostat Battery Level"
            else:
                friendly_name = "Battery Level"
        elif self.device_type == "Hive_Device_Availability":
            if self.node_device_type == "thermostatui":
                friendly_name = "Thermostat Status"
            else:
                friendly_name = " Status"
        elif self.device_type == "Hive_Device_Light_Mode":
            return self.node_name + " Mode"
        elif self.device_type == "Hive_Device_Plug_Mode":
            return self.node_name + " Mode"
        elif self.device_type == "Hive_Device_Light_Availability":
            return self.node_name + " Status"
        elif self.device_type == "Hive_Device_Plug_Availability":
            return self.node_name + " Status"
        else:
            friendly_name = FRIENDLY_NAMES.get(self.device_type)

        if self.device_type == "Hive_OutsideTemperature":
            return friendly_name
        elif self.device_type == "Hub_OnlineStatus":
            return friendly_name
        else:
            if self.node_name is not None:
                friendly_name = self.node_name + " " + friendly_name

        return friendly_name

    @property
    def force_update(self):
        """Return True if state updates should be forced."""
        if self.device_type == "Heating_TargetTemperature":
            return True
        elif self.device_type == "Hive_Device_BatteryLevel":
            return True
        elif self.device_type == "Hive_Device_Availability":
            return True
        elif self.device_type == "Hive_Device_Light_Mode":
            return True
        elif self.device_type == "Hive_Device_Plug_Mode":
            return True
        elif self.device_type == "Hive_Device_Light_Availability":
            return True
        elif self.device_type == "Hive_Device_Plug_Availability":
            return True

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.device_type == "Heating_CurrentTemperature":
            return self.session.heating.current_temperature(self.node_id)
        elif self.device_type == "Heating_TargetTemperature":
            return self.session.heating.get_target_temperature(self.node_id)
        elif self.device_type == "Heating_State":
            returnvalue = self.session.heating.get_state(self.node_id)
            return str(returnvalue).capitalize()
        elif self.device_type == "Heating_Mode":
            currentmode = self.session.heating.get_mode(self.node_id)
            if currentmode == "SCHEDULE":
                return str(HVAC_MODE_AUTO).capitalize()
            elif currentmode == "MANUAL":
                return str(HVAC_MODE_HEAT).capitalize()
            elif currentmode == "OFF":
                return str(HVAC_MODE_OFF).capitalize()
        elif self.device_type == "Heating_Boost":
            returnvalue = self.session.heating.get_boost(self.node_id)
            return str(returnvalue).capitalize()
        elif self.device_type == "HotWater_State":
            returnvalue = self.session.hotwater.get_state(self.node_id)
            return str(returnvalue).capitalize()
        elif self.device_type == "HotWater_Mode":
            currentmode = self.session.hotwater.get_mode(self.node_id)
            if currentmode == "SCHEDULE":
                return str(HVAC_MODE_AUTO).capitalize()
            elif currentmode == "ON":
                return str(STATE_ON).capitalize()
            elif currentmode == "OFF":
                return str(STATE_OFF).capitalize()
        elif self.device_type == "HotWater_Boost":
            returnvalue = self.session.hotwater.get_boost(self.node_id)
            return str(returnvalue).capitalize()
        elif self.device_type == "Hive_Device_BatteryLevel":
            self.batt_lvl = self.session.attributes.battery_level(self.node_id)
            return self.batt_lvl
        elif self.device_type == "Hive_Device_Availability":
            return self.session.attributes.online_offline(self.node_id)
        elif self.device_type == "Hive_Device_Light_Mode":
            return self.session.attributes.get_mode(self.node_id)
        elif self.device_type == "Hive_Device_Plug_Mode":
            return self.session.attributes.get_mode(self.node_id)
        elif self.device_type == "Hive_Device_Light_Availability":
            return self.session.attributes.online_offline(self.node_id)
        elif self.device_type == "Hive_Device_Plug_Availability":
            return self.session.attributes.online_offline(self.node_id)
        elif self.device_type == "Hub_OnlineStatus":
            return self.session.sensor.hub_online_status(self.node_id)
        elif self.device_type == "Hive_OutsideTemperature":
            return self.session.weather.temperature()

    @property
    def state_attributes(self):
        """Return the state attributes."""
        if self.device_type == "Heating_CurrentTemperature":
            return self.get_current_temp_sa()
        elif self.device_type == "Heating_State":
            return self.get_heating_state_sa()
        elif self.device_type == "Heating_Mode":
            return self.get_heating_state_sa()
        elif self.device_type == "Heating_Boost":
            s_a = {}
            if self.session.heating.get_boost(self.node_id) == "ON":
                minsend = self.session.heating.get_boost_time(self.node_id)
                s_a.update({"Boost ends in":
                            (str(minsend) + " minutes")})
            return s_a
        elif self.device_type == "HotWater_State":
            return self.get_hotwater_state_sa()
        elif self.device_type == "HotWater_Mode":
            return self.get_hotwater_state_sa()
        elif self.device_type == "HotWater_Boost":
            s_a = {}
            if self.session.hotwater.get_boost(self.node_id) == "ON":
                endsin = self.session.hotwater.get_boost_time(self.node_id)
                s_a.update({"Boost ends in":
                            (str(endsin) + " minutes")})
            return s_a
        else:
            return None

    def get_current_temp_sa(self):
        """Get current heating temperature state attributes."""
        s_a = {}
        temp_current = 0
        temperature_target = 0
        temperature_difference = 0

        minmax_temps = self.session.heating.minmax_temperatures(self.node_id)
        if minmax_temps is not None:
            s_a.update({"Today Min / Max":
                        str(minmax_temps['TodayMin']) + " °C" + " / "
                        + str(minmax_temps['TodayMax']) + " °C"})

            s_a.update({"Restart Min / Max":
                        str(minmax_temps['RestartMin']) + " °C" + " / "
                        + str(minmax_temps['RestartMax']) + " °C"})

        temp_current = self.session.heating.current_temperature(self.node_id)
        temperature_target = self.session.heating.\
            get_target_temperature(self.node_id)

        if temperature_target > temp_current:
            temperature_difference = temperature_target - temp_current
            temperature_difference = round(temperature_difference, 2)

            s_a.update({"Current Temperature":
                        temp_current})
            s_a.update({"Target Temperature":
                        temperature_target})
            s_a.update({"Temperature Difference":
                        temperature_difference})

        return s_a

    def get_heating_state_sa(self):
        """Get current heating state, state attributes."""
        s_a = {}

        snan = self.session.heating.get_schedule_now_next_later(self.node_id)
        if snan is not None:
            if 'now' in snan:
                if ('value' in snan["now"] and
                        'start' in snan["now"] and
                        'Start_DateTime' in snan["now"] and
                        'End_DateTime' in snan["now"] and
                        'target' in snan["now"]["value"]):
                    now_target = str(snan["now"]["value"]["target"]) + " °C"
                    nstrt = snan["now"]["Start_DateTime"].strftime("%H:%M")
                    now_end = snan["now"]["End_DateTime"].strftime("%H:%M")

                    sa_string = (now_target
                                 + " : "
                                 + nstrt
                                 + " - "
                                 + now_end)
                    s_a.update({"Now": sa_string})

            if 'next' in snan:
                if ('value' in snan["next"] and
                        'start' in snan["next"] and
                        'Start_DateTime' in snan["next"] and
                        'End_DateTime' in snan["next"] and
                        'target' in snan["next"]["value"]):
                    next_target = str(snan["next"]["value"]["target"]) + " °C"
                    nxtstrt = snan["next"]["Start_DateTime"].strftime("%H:%M")
                    next_end = snan["next"]["End_DateTime"].strftime("%H:%M")

                    sa_string = (next_target
                                 + " : "
                                 + nxtstrt
                                 + " - "
                                 + next_end)
                    s_a.update({"Next": sa_string})

            if 'later' in snan:
                if ('value' in snan["later"] and
                        'start' in snan["later"] and
                        'Start_DateTime' in snan["later"] and
                        'End_DateTime' in snan["later"] and
                        'target' in snan["later"]["value"]):
                    ltarg = str(snan["later"]["value"]["target"]) + " °C"
                    lstrt = snan["later"]["Start_DateTime"].strftime("%H:%M")
                    lend = snan["later"]["End_DateTime"].strftime("%H:%M")

                    sa_string = (ltarg
                                 + " : "
                                 + lstrt
                                 + " - "
                                 + lend)
                    s_a.update({"Later": sa_string})
        else:
            s_a.update({"Schedule not active": ""})

        return s_a

    def get_hotwater_state_sa(self):
        """Get current hotwater state, state attributes."""
        s_a = {}

        snan = self.session.hotwater.get_schedule_now_next_later(self.node_id)
        if snan is not None:
            if 'now' in snan:
                if ('value' in snan["now"] and
                        'start' in snan["now"] and
                        'Start_DateTime' in snan["now"] and
                        'End_DateTime' in snan["now"] and
                        'status' in snan["now"]["value"]):
                    now_status = snan["now"]["value"]["status"]
                    now_start = snan["now"]["Start_DateTime"].strftime("%H:%M")
                    now_end = snan["now"]["End_DateTime"].strftime("%H:%M")

                    sa_string = (now_status
                                 + " : "
                                 + now_start
                                 + " - "
                                 + now_end)
                    s_a.update({"Now": sa_string})

            if 'next' in snan:
                if ('value' in snan["next"] and
                        'start' in snan["next"] and
                        'Start_DateTime' in snan["next"] and
                        'End_DateTime' in snan["next"] and
                        'status' in snan["next"]["value"]):
                    next_status = snan["next"]["value"]["status"]
                    nxtstrt = snan["next"]["Start_DateTime"].strftime("%H:%M")
                    next_end = snan["next"]["End_DateTime"].strftime("%H:%M")

                    sa_string = (next_status
                                 + " : "
                                 + nxtstrt
                                 + " - "
                                 + next_end)
                    s_a.update({"Next": sa_string})
            if 'later' in snan:
                if ('value' in snan["later"] and
                        'start' in snan["later"] and
                        'Start_DateTime' in snan["later"] and
                        'End_DateTime' in snan["later"] and
                        'status' in snan["later"]["value"]):
                    later_status = snan["later"]["value"]["status"]
                    later_start = (snan["later"]
                                   ["Start_DateTime"].strftime("%H:%M"))
                    later_end = snan["later"]["End_DateTime"].strftime("%H:%M")

                    sa_string = (later_status
                                 + " : "
                                 + later_start
                                 + " - "
                                 + later_end)
                    s_a.update({"Later": sa_string})
        else:
            s_a.update({"Schedule not active": ""})

        return s_a

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self.device_type == "Heating_CurrentTemperature":
            return TEMP_CELSIUS
        elif self.device_type == "Heating_TargetTemperature":
            return TEMP_CELSIUS
        elif self.device_type == "Hive_OutsideTemperature":
            return TEMP_CELSIUS
        elif self.device_type == "Hive_Device_BatteryLevel":
            return "%"
        else:
            return None

    @property
    def icon(self):
        """Return the icon to use."""
        if self.device_type == "Hive_Device_BatteryLevel":
            return icon_for_battery_level(battery_level=self.batt_lvl)
        else:
            return DEVICETYPE_ICONS.get(self.device_type)

    def update(self):
        """Update all Node data frome Hive."""
        self.session.core.update_data(self.node_id)
