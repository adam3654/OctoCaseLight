# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import octoprint.control

from octoprint.events import Events
import flask

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class OctoLightPlugin(
		octoprint.plugin.AssetPlugin,
		octoprint.plugin.StartupPlugin,
		octoprint.plugin.TemplatePlugin,
		octoprint.plugin.SimpleApiPlugin,
		octoprint.plugin.SettingsPlugin,
		octoprint.plugin.EventHandlerPlugin,
		octoprint.plugin.RestartNeedingPlugin
	):

	light_state = False

	def get_settings_defaults(self):
		return dict(
			gCodeStateCommand = "M355",
			gCodeToggleCommand = "M355 T"
			
		)

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=True),
			dict(type="settings", custom_bindings=True)
		]

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/octolight.js"],
			css=["css/octolight.css"],
			#less=["less/octolight.less"]
		)

	def on_after_startup(self):
		self.light_state = False
		self._logger.info("--------------------------------------------")
		self._logger.info("OctoLight started, listening for GET request")
		self._logger.info("Toggle_Command: {}, State_Command: {}".format(
			self._settings.get(["gCodeToggleCommand"]),
			self._settings.get(["gCodeStateCommand"])
		))
		self._logger.info("--------------------------------------------")

		# Setting the default state of pin

		# TODO:
		# Send GCode Command "gCodeStateCommand" and log response (Recv: echo:Case light: ON)
		# If State= ON then set light_state = True, else False

		

		self._plugin_manager.send_plugin_message(self._identifier, dict(isLightOn=self.light_state))

	def light_toggle(self):
		# Sets the GPIO every time, if user changed it in the settings.
		 # TODO:
		 # Send Light Toggle Gcode Command
		 # Get new Light State

		OctoPrint.control.sendGcode(self._settings.get(["gCodeToggleCommand"]))
		OctoPrint.control.sendGcode(self._settings.get(["gCodeStateCommand"]))
		self.light_state = self.get_state()
		
		self._plugin_manager.send_plugin_message(self._identifier, dict(isLightOn=self.light_state))

	def get_state(self):
		new_State = False
		## TODO:
		## Get Light State
		## Set light_state accordingly
		return new_State

	def on_api_get(self, request):
		action = request.args.get('action', default="toggle", type=str)

		if action == "toggle":
			self.light_toggle()

			return flask.jsonify(state=self.light_state)

		elif action == "getState":
			return flask.jsonify(state=self.light_state)

		elif action == "turnOn":
			if not self.light_state:
				self.light_toggle()

			return flask.jsonify(state=self.light_state)

		elif action == "turnOff":
			if self.light_state:
				self.light_toggle()

			return flask.jsonify(state=self.light_state)

		else:
			return flask.jsonify(error="action not recognized")

	def on_event(self, event, payload):
		if event == Events.CLIENT_OPENED:
			self._plugin_manager.send_plugin_message(self._identifier, dict(isLightOn=self.light_state))
			return

	def get_update_information(self):
		return dict(
			octolight=dict(
				displayName="OctoLight",
				displayVersion=self._plugin_version,

				type="github_release",
				current=self._plugin_version,

				user="adam3654",
				repo="OctoLight",
				pip="https://github.com/adam3654/OctoLight/archive/{target}.zip"
			)
		)

__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = OctoLightPlugin()

__plugin_hooks__ = {
	"octoprint.plugin.softwareupdate.check_config":
	__plugin_implementation__.get_update_information
}
