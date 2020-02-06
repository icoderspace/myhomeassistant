from datetime import datetime, timedelta

from homeassistant.components.weather import (
    WeatherEntity, ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP, ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME)
from homeassistant.const import (TEMP_CELSIUS, TEMP_FAHRENHEIT, CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME)

import requests
import json

CONDITION_MAP = {
    'CLEAR_DAY': 'sunny',
    'CLEAR_NIGHT': 'clear-night',
    'PARTLY_CLOUDY_DAY': 'partlycloudy',
    'PARTLY_CLOUDY_NIGHT':'partlycloudy',
    'CLOUDY': 'cloudy',
    'RAIN': 'rainy',
    'SNOW': 'snowy',
    'WIND': 'windy',
    'HAZE': 'fog',
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([ColorfulCloudsWeather(api_key=config.get(CONF_API_KEY),
                                        lng=config.get(CONF_LONGITUDE, hass.config.longitude),
                                        lat=config.get(CONF_LATITUDE, hass.config.latitude),
                                        name=config.get(CONF_NAME, 'colorfulclouds'))])


class ColorfulCloudsWeather(WeatherEntity):
    """Representation of a weather condition."""

    def __init__(self, api_key: str, lng: str, lat: str, name: str):
        self._api_key = api_key
        self._lng = lng
        self._lat = lat
        self._name = name

        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        """Return the weather condition."""
        skycon = self._realtime_data['result']['skycon']
        return CONDITION_MAP[skycon]

    @property
    def temperature(self):
        return self._realtime_data['result']['temperature']

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def humidity(self):
        return float(self._realtime_data['result']['humidity']) * 100

    @property
    def wind_speed(self):
        return self._realtime_data['result']['wind']['speed']

    @property
    def wind_bearing(self):
        return self._realtime_data['result']['wind']['direction']

    @property
    def attribution(self):
        """Return the attribution."""
        return 'Powered by ColorfulClouds and China Meteorological Administration'

    @property
    def forecast(self):
        forecast_data = []
        for i in range(5):
            time_str = self._forecast_data['result']['daily']['temperature'][i]['date']
            data_dict = {
                ATTR_FORECAST_TIME: datetime.strptime(time_str, '%Y-%m-%d'),
                ATTR_FORECAST_CONDITION: CONDITION_MAP[self._forecast_data['result']['daily']['skycon'][i]['value']],
                ATTR_FORECAST_PRECIPITATION: self._forecast_data['result']['daily']['precipitation'][i]['avg'],
                ATTR_FORECAST_TEMP: self._forecast_data['result']['daily']['temperature'][i]['avg'],
                ATTR_FORECAST_TEMP_LOW: self._forecast_data['result']['daily']['temperature'][i]['min']
            }
            forecast_data.append(data_dict)

        return forecast_data

    def update(self):
        json_text = requests.get(str.format("https://api.caiyunapp.com/v2/{}/{},{}/realtime.json?unit=metric:v2", self._api_key, self._lng, self._lat)).content
        self._realtime_data = json.loads(json_text)

        json_text = requests.get(str.format("https://api.caiyunapp.com/v2/{}/{},{}/forecast.json?unit=metric:v2", self._api_key, self._lng, self._lat)).content
        self._forecast_data = json.loads(json_text)
