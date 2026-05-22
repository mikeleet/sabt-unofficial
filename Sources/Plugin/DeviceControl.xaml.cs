using SimHub;
using System;
using System.ComponentModel;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Threading;
using WoteverLocalization;

namespace User.ActiveBeltTensioner
{
    public partial class DeviceControl : UserControl
    {
        private readonly DevicePlugin _plugin;
        private readonly DispatcherTimer _updateSerialPortsTimer;

        public Action<string> OnSerialPortSelected;

        public DeviceControl(DevicePlugin plugin)
        {
            Logging.Current.Info("SABT: DeviceControl()...");

            _plugin = plugin;

            InitializeComponent();

            Loaded += OnLoaded;
            Unloaded += OnUnloaded;

            _plugin.Settings.IsEnabled = (_plugin.Settings.IsEnabled && _plugin.Settings.StartAutomatically);
            _plugin.Settings.PropertyChanged += OnPropertyChanged;

            _updateSerialPortsTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(5)
            };
            _updateSerialPortsTimer.Tick += UpdateSerialPorts;
        }
 
        private void OnPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            /*if (e.PropertyName == nameof(_plugin.Settings.SerialPort))
            {
                _plugin.MotorController.OpenSerialPort();
            }*/
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            Logging.Current.Info("SABT: OnLoaded()...");

            DataContext = new DeviceViewModel(
                _plugin.Settings,
                _plugin.MotorController,
                _plugin.TelemetryGraphModel,
                _plugin
            );

            _plugin.DoWithoutWaiting(
                devicePlugin =>
                {
                    devicePlugin.MotorController.UpdateSerialPorts();
                }
            );

            _updateSerialPortsTimer.Start();
        }

        private void OnUnloaded(object sender, RoutedEventArgs e)
        {
            Logging.Current.Info("SABT: OnUnloaded()...");

            _updateSerialPortsTimer.Stop();
        }

        private void UpdateSerialPorts(object sender, EventArgs e)
        {
            if (IsLoaded)
            {
                _plugin.DoWithoutWaiting(
                    devicePlugin =>
                    {
                        devicePlugin.MotorController.UpdateSerialPorts();
                    }
                );
            }
        }

        private void TestLeftMotor(object sender, RoutedEventArgs e)
        {
            _plugin.DoWithoutWaiting(
                devicePlugin =>
                {
                    if (!devicePlugin.MotorController.IsBusy)
                    {
                        Dispatcher.Invoke(() => PulseImage(LeftMotorImage));
                        devicePlugin.MotorController.RunTest(devicePlugin.MotorController.GetLeftMotor(), 0.5);
                    }
                }
            );
        }

        private void TestRightMotor(object sender, RoutedEventArgs e)
        {
            _plugin.DoWithoutWaiting(
                devicePlugin =>
                {
                    if (!devicePlugin.MotorController.IsBusy)
                    {
                        Dispatcher.Invoke(() => PulseImage(RightMotorImage));
                        devicePlugin.MotorController.RunTest(devicePlugin.MotorController.GetRightMotor(), 0.5);
                    }
                }
            );
        }

        private void PulseImage(System.Windows.Controls.Image image)
        {
            DoubleAnimationUsingKeyFrames anim = new DoubleAnimationUsingKeyFrames();
            // 8 pulses at 200ms intervals: 1.0 → 1.15 → 1.0 → 1.15 ...
            for (int i = 0; i <= 8; i++)
            {
                double s = (i % 2 == 0) ? 1.0 : 1.15;
                anim.KeyFrames.Add(new LinearDoubleKeyFrame(s, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(i * 200))));
            }
            ScaleTransform scale = (ScaleTransform)image.RenderTransform;
            scale.BeginAnimation(ScaleTransform.ScaleYProperty, anim);
        }

        private void SetupMotors(object sender, RoutedEventArgs e)
        {
            _plugin.DoWithoutWaiting(
                devicePlugin =>
                {
                    if (!devicePlugin.MotorController.IsBusy)
                    {
                        devicePlugin.MotorController.Setup();
                    }
                }
            );
        }

        private void OpenHyperlink(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Process.Start(((Hyperlink)sender).NavigateUri.ToString());
        }
    }
}