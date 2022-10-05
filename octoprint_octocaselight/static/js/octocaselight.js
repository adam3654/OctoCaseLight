$(function() {
    function OctocaselightViewModel(parameters){
    	var self = this;

        self.settingsViewModel = parameters[0]
        self.loginState = parameters[1];

    	self.light_indicator = $("#light_indicator");
    	self.isLightOn = ko.observable(undefined);

        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };

    	self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "octocaselight") {
                return;
            }

            if (data.isLightOn !== undefined) {
                self.isLightOn(data.isLightOn);
            }
        };

        self.onStartup = function () {
            self.isLightOn.subscribe(function() {
                if (self.isLightOn()) {
                    self.light_indicator.removeClass("off").addClass("on");
                } else {
                    self.light_indicator.removeClass("on").addClass("off");
                }
            });
        }
    }

     OCTOPRINT_VIEWMODELS.push({
        construct: OctocaselightViewModel,
        dependencies: ["settingsViewModel","loginStateViewModel"],
        elements: ["#navbar_plugin_octocaselight","#settings_plugin_octocaselight"]
    });
});