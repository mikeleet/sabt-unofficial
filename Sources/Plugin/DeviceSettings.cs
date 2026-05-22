using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace User.ActiveBeltTensioner
{
    public class DeviceSettings : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        private const string _deviceNotFound = "N/A";

        private void InvokePropertyChange([CallerMemberName] string name = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }

        private string _serialPort = _deviceNotFound;
        public string SerialPort
        {
            get { return _serialPort; }
            set
            {
                if (_serialPort != value)
                {
                    _serialPort = value ?? _deviceNotFound;
                    InvokePropertyChange(nameof(SerialPort));
                    InvokePropertyChange(nameof(IsSerialPortValid));
                }
            }
        }

        private bool _isEnabled = false;
        public bool IsEnabled
        {
            get { return _isEnabled; }
            set
            {
                if (_isEnabled != value)
                {
                    _isEnabled = value;
                    InvokePropertyChange(nameof(IsEnabled));
                }
            }
        }

        private bool _startAutomatically = true;
        public bool StartAutomatically
        {
            get { return _startAutomatically; }
            set
            {
                if (_startAutomatically != value)
                {
                    _startAutomatically = value;
                    InvokePropertyChange(nameof(StartAutomatically));
                }
            }
        }

        private bool _isFlipped = false;
        public bool IsFlipped
        {
            get { return _isFlipped; }
            set
            {
                if (_isFlipped != value)
                {
                    _isFlipped = value;
                    InvokePropertyChange(nameof(IsFlipped));
                }
            }
        }

        private int _idleTension = 150;
        public int IdleTension
        {
            get { return _idleTension; }
            set
            {
                if (_idleTension != value)
                {
                    _idleTension = value;
                    InvokePropertyChange(nameof(IdleTension));
                }
            }
        }

        private int _minimumTension = 200;
        public int MinimumTension
        {
            get { return _minimumTension; }
            set
            {
                if (_minimumTension != value)
                {
                    _minimumTension = Math.Min(value, _maximumTension);
                    InvokePropertyChange(nameof(MinimumTension));
                    InvokePropertyChange(nameof(IsMinimumTensionNonZero));
                }
            }
        }

        private int _maximumTension = 1000;
        public int MaximumTension
        {
            get { return _maximumTension; }
            set
            {
                if (_maximumTension != value)
                {
                    _maximumTension = Math.Max(value, _minimumTension);
                    InvokePropertyChange(nameof(MaximumTension));
                }
            }
        }

        private int _minimumSurge = -8;
        public int MinimumSurge
        {
            get { return _minimumSurge; }
            set
            {
                if (_minimumSurge != value)
                {
                    _minimumSurge = Math.Min(value, _maximumSurge);
                    InvokePropertyChange(nameof(MinimumSurge));
                }
            }
        }

        private int _maximumSurge = 25;
        public int MaximumSurge
        {
            get { return _maximumSurge; }
            set
            {
                if (_maximumSurge != value)
                {
                    _maximumSurge = Math.Max(value, _minimumSurge);
                    InvokePropertyChange(nameof(MaximumSurge));
                }
            }
        }

        private int _minimumSway = -25;
        public int MinimumSway
        {
            get { return _minimumSway; }
            set
            {
                if (_minimumSway != value)
                {
                    _minimumSway = Math.Min(value, _maximumSway);
                    InvokePropertyChange(nameof(MinimumSway));

                }
            }
        }

        private int _maximumSway = 25;
        public int MaximumSway
        {
            get { return _maximumSway; }
            set
            {
                if (_maximumSway != value)
                {
                    _maximumSway = Math.Max(value, _minimumSway);
                    InvokePropertyChange(nameof(MaximumSway));

                }
            }
        }

        private int _minimumHeave = -25;
        public int MinimumHeave
        {
            get { return _minimumHeave; }
            set
            {
                if (_minimumHeave != value)
                {
                    _minimumHeave = Math.Min(value, _maximumHeave);
                    InvokePropertyChange(nameof(MinimumHeave));
                }
            }
        }

        private int _maximumHeave = 90;
        public int MaximumHeave
        {
            get { return _maximumHeave; }
            set
            {
                if (_maximumHeave != value)
                {
                    _maximumHeave = Math.Max(value, _minimumHeave);
                    InvokePropertyChange(nameof(MaximumHeave));
                }
            }
        }

        private int _sideBias = 0;
        public int SideBias
        {
            get { return _sideBias; }
            set {
                if (_sideBias != value)
                {
                    _sideBias = value;
                    InvokePropertyChange(nameof(SideBias));
                }
            }
        }

        private int _smoothingFactor = 300;
        public int SmoothingFactor
        {
            get { return _smoothingFactor; }
            set
            {
                if (_smoothingFactor != value)
                {
                    _smoothingFactor = value;
                    InvokePropertyChange(nameof(SmoothingFactor));
                }
            }
        }

        private int _corneringStrength = 1000;
        public int CorneringStrength
        {
            get { return _corneringStrength; }
            set
            {
                if (_corneringStrength != value)
                {
                    _corneringStrength = value;
                    InvokePropertyChange(nameof(CorneringStrength));
                }
            }
        }

        private int _accelerationStrength = 1000;
        public int AccelerationStrength
        {
            get { return _accelerationStrength; }
            set
            {
                if (_accelerationStrength != value)
                {
                    _accelerationStrength = value;
                    InvokePropertyChange(nameof(AccelerationStrength));
                }
            }
        }

        private int _brakingStrength = 1000;
        public int BrakingStrength
        {
            get { return _brakingStrength; }
            set
            {
                if (_brakingStrength != value)
                {
                    _brakingStrength = value;
                    InvokePropertyChange(nameof(BrakingStrength));
                }
            }
        }

        private int _jumpingStrength = 1000;
        public int JumpingStrength
        {
            get { return _jumpingStrength; }
            set
            {
                if (_jumpingStrength != value)
                {
                    _jumpingStrength = value;
                    InvokePropertyChange(nameof(JumpingStrength));
                }
            }
        }

        private int _landingStrength = 1000;
        public int LandingStrength
        {
            get { return _landingStrength; }
            set
            {
                if (_landingStrength != value)
                {
                    _landingStrength = value;
                    InvokePropertyChange(nameof(LandingStrength));
                }
            }
        }

        private int _shiftingStrength = 0;
        public int ShiftingStrength
        {
            get { return _shiftingStrength; }
            set
            {
                if (_shiftingStrength != value)
                {
                    _shiftingStrength = value;
                    InvokePropertyChange(nameof(ShiftingStrength));
                }
            }
        }

        private bool _isAdaptiveNormalizationEnabled = false;
        public bool IsAdaptiveNormalizationEnabled
        {
            get { return _isAdaptiveNormalizationEnabled; }
            set
            {
                if (_isAdaptiveNormalizationEnabled != value)
                {
                    _isAdaptiveNormalizationEnabled = value;
                    InvokePropertyChange(nameof(IsAdaptiveNormalizationEnabled));
                    InvokePropertyChange(nameof(IsStaticRangeEnabled));
                }
            }
        }

        private int _adaptiveDecayRate = 500;
        public int AdaptiveDecayRate
        {
            get { return _adaptiveDecayRate; }
            set
            {
                if (_adaptiveDecayRate != value)
                {
                    _adaptiveDecayRate = value;
                    InvokePropertyChange(nameof(AdaptiveDecayRate));
                }
            }
        }

        private bool _isAutoReconnectEnabled = true;
        public bool IsAutoReconnectEnabled
        {
            get { return _isAutoReconnectEnabled; }
            set
            {
                if (_isAutoReconnectEnabled != value)
                {
                    _isAutoReconnectEnabled = value;
                    InvokePropertyChange(nameof(IsAutoReconnectEnabled));
                }
            }
        }

        private bool _suppressActivationWarning = true;
        public bool SuppressActivationWarning
        {
            get { return _suppressActivationWarning; }
            set
            {
                if (_suppressActivationWarning != value)
                {
                    _suppressActivationWarning = value;
                    InvokePropertyChange(nameof(SuppressActivationWarning));
                }
            }
        }

        private int _massageDuration = 5;
        public int MassageDuration
        {
            get { return _massageDuration; }
            set
            {
                if (_massageDuration != value)
                {
                    _massageDuration = Math.Max(3, Math.Min(value, 30));
                    InvokePropertyChange(nameof(MassageDuration));
                }
            }
        }

        private int _massageStrength = 500;
        public int MassageStrength
        {
            get { return _massageStrength; }
            set
            {
                if (_massageStrength != value)
                {
                    _massageStrength = Math.Max(100, Math.Min(value, 1000));
                    InvokePropertyChange(nameof(MassageStrength));
                }
            }
        }

        private int _autoReconnectDelay = 3;
        public int AutoReconnectDelay
        {
            get { return _autoReconnectDelay; }
            set
            {
                if (_autoReconnectDelay != value)
                {
                    _autoReconnectDelay = Math.Max(0, Math.Min(value, 10));
                    InvokePropertyChange(nameof(AutoReconnectDelay));
                }
            }
        }


        public bool IsMinimumTensionNonZero
        {
            get { return MinimumTension > 0; }
        }

        public bool IsStaticRangeEnabled
        {
            get { return !IsAdaptiveNormalizationEnabled; }
        }

        public bool IsSerialPortValid
        {
            get { return !String.IsNullOrEmpty(_serialPort) && (_serialPort != _deviceNotFound); }
        }
    }
}