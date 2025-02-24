using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.AccessControl;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    internal class Pump
    {
        private double _gearRatio;
        private double _minPumpRpm;
        private double _maxPumpRpm;
        private double _minPressure;
        private double _maxPressure;
        private double _maxFlowRate;
        private double _psiPerRpm;

        public Pump(double gearRatio, double minPumpRpm, double maxPumpRpm, double minPressure, double maxPressure, double maxFlowRate)
        {
            _gearRatio = gearRatio;
            _minPumpRpm = minPumpRpm;
            _maxPumpRpm = maxPumpRpm;
            _minPressure = minPressure;
            _maxPressure = maxPressure;
            _maxFlowRate = maxFlowRate;

            // The raw PSI increase per pump RPM without external factors like flow rate
            _psiPerRpm = (_maxPressure - _minPressure) / (_maxPumpRpm - _minPumpRpm);
        }

        internal void CalculatePressure(double flowRate, double engineRpm)
        {

        }
    }  
}
