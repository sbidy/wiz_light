![Lint](https://github.com/sbidy/wiz_light/workflows/Lint/badge.svg) ![Pylint](https://github.com/sbidy/wiz_light/workflows/Pylint/badge.svg)

# :bulb: wiz_light - V 0.3

## :muscle: Change Log
This version represents the current pull from HASS core with some additional improvements.

- Working ConfigFlow: Now the bulbs can be configured via UI
- Devices Registration: The Bulb now shows up as "Light" device
- [BETA] The colors now "correct" regarding the HS to RGB-CW conversation in the WiZ app. Thanks to @brettonw for incredible work!(should be tested with non-RGB and non-Kelvin bulbs!! )
- Poll Service: Now it is possible to trigger a status update from the bulb via HASS service. This can be helpful for automations (e.g. motion detectors).
- DNS and IPs Support: The bulbs can now be added with an DNS name or ip.
- Bulb Library Moved: The "YAML" file was removed (because of a policy from HASS dev) and moved to the `pywizlight` repo..
- Tones of other fixes, improvement and removed typos :wink:

### Still missing but "Work in Progress":

- Automatic detection for the supported kelvin range of the bulb. This should reduce the static overhead.
- Registration of the bulb to HASS via UDP API. There are features to register the HASS to the bulb to send UDP packages to the HASS if the state of the bulb was changed. This will made the Poll Service obsolete.
- A User Documentaion based on HASS Docs. (with screen shots etc.) will be added (soon :wink:)

### What is declined or rejected:

- Change of the speed of the transition from on to off and off->on. This is not supported via the UDP API and can only be configured via WiZ App.
- Custom Effekts will not be implemented in the HASS integration becaus of missing feature in HASS.

## :information_source: [Development Log](https://github.com/sbidy/wiz_light/discussions/78)

Here you can found some news and updates!!
I try to create a kind of Development Log to trace changes/decissions and made the current overall development status transparent to you!!

## :warning: Discussions

If you have questions or other comments please use the **new** [Discussions Board](https://github.com/sbidy/wiz_light/discussions).

## :blue_heart: Kudos and contributions

Thank you [@angadsingh](https://github.com/angadsingh) for make such incredible improvements!

Thanks to [@simora](https://github.com/simora) for create a HA Switch <-> WiZ Plug integration!

Thanks to [@jarpatus](https://github.com/jarpatus) for the feedback and enhancements!

Thanks to [@ChrisLizon](https://github.com/ChrisLizon) for the review, feedbacks and improvements!

Thanks to [@brettonw](https://github.com/brettonw) for improveing the RGB-CW to HU tranistion!

Thanks to [@vodovozovge](https://github.com/vodovozovge) for the "insider support" for the community!

## :flight_departure: Dependencies

This component has a dependency on `pywizlight` which will be installed automatically by Home Assistant.

## :zap: Bulbs - the library was moved to the [pywizlight](https://github.com/sbidy/pywizlight)
 project!

| Bulb Type          | Dimmer | Color Temp | Effects | RGB | Tested? | Example Product                                                                                                  |
| ------------------ | ------ | ---------- | ------- | --- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| ESP01_SHDW_01      | ✔️     |            |         |     |         |                                                                                                                  |
| ESP01_SHRGB1C_31   | ✔️     | ✔️         | ✔️      | ✔️  | ✔️      | • Philips 555623 recessed <br /> • Philips 556167 A19 Frosted Full Colour and Tunable White                      |
| ESP01_SHTW1C_31    | ✔️     | ✔️         |         |     | ✔️      | • Philips 555599 recessed                                                                                        |
| ESP56_SHTW3_01     | ✔️     | ✔️         | ✔️      |     | ✔️      |                                                                                                                  |
| ESP01_SHRGB_03     | ✔️     | ✔️         | ✔️      | ✔️  | ✔️      |                                                                                                                  |
| ESP01_SHDW1_31     | ✔️     |            |         |     |         |                                                                                                                  |
| ESP06_SHDW1_01     | ✔️     |            |         |     |         |                                                                                                                  |
| ESP15_SHTW1_01I    | ✔️     | ✔️         |         |     |         |
| ESP03_SHRGB1C_01   | ✔️     | ✔️         | ✔️      | ✔️  | ✔️      | • Philips Color &. Tunable-White A19 <br />• WiZ A60 E27 EAN 8718699787059 <br />• WiZ G95 E27 EAN 8718699786359 |
| ESP03_SHRGB1W_01   | ✔️     | ✔️         | ✔️      | ✔️  | ✔️      | • Philips Color &. Tunable-White A21 <br />• WiZ A67 E27 EAN 8718699786199                                       |
| ESP06_SHDW9_01     | ✔️     |            |         |     | ✔️      | • Philips Soft White A19                                                                                         |
| ESP03_SHRGBP_31    | ✔️     | ✔️         | ✔️      | ✔️  | ✔️      | • Trio Leuchten WiZ LED                                                                                          |
| ESP17_SHTW9_01     | ✔️     | ✔️         |         |     | ✔️      | • WiZ Filament Bulb EAN 8718699786793                                                                            |
| ESP03_SHRGB3_01ABI | ✔️     | ✔️         | ✔️      | ✔️  | ✔️      |


## Pull request in HA core

https://github.com/home-assistant/core/pull/44779

## Install for testing

1. Loggon to your HA or HASS with SSH
2. Got to the HA `custom_components` directory within the HA installation path (if this is not available - create this directory).
3. Run `cd custom_components`
4. Run `git clone https://github.com/sbidy/wiz_light` within the `custom_components` directory
5. Run `mv wiz_light/custom_components/wiz_light/* wiz_light/` to move the files in the correct diretory
6. Restart your HA/HASS service in the UI with `<your-URL>/config/server_control`
7. Add the bulbs to your `configuration.yaml` - You can not add the bulbs in the HA UI!! (configFlow is missing)

Questions? Check out the github project [pywizlight](https://github.com/sbidy/pywizlight)

## HA config

## You can now use the HASS UI to add the devices/integration.

To enable the platform integration after installation add

```
light:
  - platform: wiz_light
    name: <Name of the device>
    host: <IP of the bulb>
  - platform: wiz_light
    name: <Name of the device#2>
    host: <IP of the bulb#2>
```

If you want to use the integration as switch

```
switch:
  - platform: wiz_light
    name: <Name of the device>
    host: <IP of the socket>
```
