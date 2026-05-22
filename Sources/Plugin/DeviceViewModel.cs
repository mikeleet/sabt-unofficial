using OxyPlot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace User.ActiveBeltTensioner
{
    public class DeviceViewModel
    {
        public DeviceSettings Settings { get; }
        public MotorController MotorController { get; }
        public PlotModel TelemetryGraphModel { get; }
        public DevicePlugin Plugin { get; }

        public DeviceViewModel(
            DeviceSettings settings,
            MotorController motorController,
            PlotModel telemetryGraphModel,
            DevicePlugin plugin
        )
        {
            Settings = settings;
            MotorController = motorController;
            TelemetryGraphModel = telemetryGraphModel;
            Plugin = plugin;
        }
    }
}
