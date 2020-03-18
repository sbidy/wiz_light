# wiz_light
A WiZ Light integration for Home Assistant.

## Next improvement:
- deterministic selection of following bulb types: Only dimmable, dimmable + white color temprature (kelvin) and full RGB support also with white color temperatur. Maybe with an auto detect feature, try and error testing or via configuration YAML.
- Prepare for hacs.xyz

Working features 
 - Brigtness
 - Color (RGB)
 - White Color Temprature
 - On/Off
 - Effects
 - Setting a rhythm as a scene

 Next up:
  - Some improvements and bugfixes to create a more stable integration
  - testing with other hardware -- **Contribution required !!**

## Install for testing 
If you want to try the integration please clone this repo to `<confdir>/custom_components/`.

Run `git clone https://github.com/sbidy/wiz_light` within the `<confdir>/custom_components/`.

You also have to install the `pywizlight` and `asyncio_dgram` packages (`pip install -r requirements.txt`). Questions? Check out the github project [pywizlight](https://github.com/sbidy/pywizlight)

## HA config
To enable the platform integration add 
```
light:
  - platform: wiz_light
    name: <Name of the device>
    host: <IP of the bulb>
```
