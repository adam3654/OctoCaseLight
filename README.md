# OctoCaseLight
A simple plugin that adds a button to the navigation bar for toggling the case light using M355 commands.

![WebUI interface](img/screenshoot.png)

## Setup
Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

	https://github.com/adam3654/OctoCaseLight/archive/master.zip

## Configuration
![Settings panel](img/settings.png)

Curently, you can configure three settings:
- `Light On GCODE Command`: Turns the Case Light On
	- Default value: M355 S1
	
- `Light Off GCODE Command`: Turns the Case Light Off
	- Default value: M355 S0

- `Light State GCODE Command`: Returns the current state of the light
	- Default value: M355
## API
Base API URL : `GET http://YOUR_OCTOPRINT_SERVER/api/plugin/octocaselight?action=ACTION_NAME`

This API always returns updated light state in JSON: `{state: true}`

_(if the action parameter not given, the action toggle will be used by default)_
#### Actions
- **toggle** (default action): Toggle light switch on/off.
- **turnOn**: Turn on light.
- **turnOff**: Turn off light.
- **getState**: Get current light switch state.

