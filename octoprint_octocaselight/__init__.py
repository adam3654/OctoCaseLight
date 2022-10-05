# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
#import octoprint.control

from octoprint.events import Events
import flask


class OctoCaseLightPlugin(
		octoprint.plugin.AssetPlugin,
		octoprint.plugin.StartupPlugin,
		octoprint.plugin.TemplatePlugin,
		octoprint.plugin.SimpleApiPlugin,
		octoprint.plugin.SettingsPlugin,
		octoprint.plugin.EventHandlerPlugin,
		octoprint.plugin.RestartNeedingPlugin
	):
	def __init__(self):
		self.light_state = False
		self.wait_light  = False
		self.wait_ok     = False

	def get_settings_defaults(self):
		return dict(
			gCodeStateCommand  = "M355",
			gCodeOnCommand = "M355 S1",
			gCodeOffCommand = "M355 S0"
			#isLightOn          = False
			
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
	
	def get_api_commands(self):
		return {'wait_command': []}
	
	def on_api_command(self, command, data):
		if command == 'wait_command':
			self.wait_ok = True
			
	def on_gcode_sending(self, comm, phase, cmd, cmd_type, gcode, subcode=None, tags=None, *args, **kwargs):
		if 'M355' in cmd: self.wait_light = True
		return None
	
	def on_gcode_recieved(self, comm, line, *args, **kwargs):
		if ((not self.wait_light) and (not self.wait_ok)) or line.strip() in ['','wait','Not SD printing'] or line.strip()[:2]=='T:':
			return line
		if 'Case light:' in line.strip():
			if ': OFF' in line.strip():
				self.light_state = False
			elif ': ON' in line.strip():
				self.light_state = True
		elif line.strip() == 'ok' or line.strip()[:2]=='ok':
			self.wait_light = False
			if self.wait_ok:
				self.wait_ok = False
		return line
	
	def on_server_connect(self, *args, **kwargs):
		self.get_state()
		return

	def on_after_startup(self):
		self.light_state = False
		self._logger.info("--------------------------------------------")
		self._logger.info("OctoLight started, listening for GET request")
		self._logger.info("On_Command: {}, Off_Command: {}, State_Command: {}".format(
			self._settings.get(["gCodeOnCommand"]),
			self._settings.get(["gCodeOffCommand"]),
			self._settings.get(["gCodeStateCommand"])
		))
		self._logger.info("--------------------------------------------")
		self.get_state()
		return


	def light_toggle(self):
		# Sets the GPIO every time, if user changed it in the settings.	
		self.get_state()	
		if (self.light_state):
			self._printer.commands(self._settings.get(["gCodeOffCommand"]))
			self.light_state = False
		else:
			self._printer.commands(self._settings.get(["gCodeOnCommand"]))
			self.light_state = True
		self._plugin_manager.send_plugin_message(self._identifier, dict(isLightOn=self.light_state))
		return


	def get_state(self):		
		self._printer.commands(self._settings.get(["gCodeStateCommand"]))
		self._plugin_manager.send_plugin_message(self._identifier, dict(isLightOn=self.light_state))
		return

	def on_api_get(self, request):
		action = request.args.get('action', default="toggle", type=str)
		self.get_state()
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
			self.get_state()
		return

	def get_update_information(self):
		return dict(
			octolight=dict(
				displayName="OctoLight",
				displayVersion=self._plugin_version,

				type="github_release",
				current=self._plugin_version,

				user="adam3654",
				repo="OctoCaseLight",
				pip="https://github.com/adam3654/OctoCaseLight/archive/refs/heads/master.zip"
			)
		)

__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OctoCaseLightPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.received": __plugin_implementation__.on_gcode_recieved,
		"octoprint.comm.protocol.gcode.sending": __plugin_implementation__.on_gcode_sending,
		"octoprint.printer.handle_connect": __plugin_implementation__.on_server_connect
	}
