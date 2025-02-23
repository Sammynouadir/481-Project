using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Intrinsics.Arm;
using System.Security.AccessControl;
using System.Text;
using System.Threading.Tasks;
using System.Transactions;

namespace PumpBrain
{
    internal class Pump
    {
        public double MasterDischargePressure { get; private set; }
        private double _previousPumpPressure;
        private double _gearRatio;
        private double _flowResistanceCoefficient;
        private double _quadraticFlowCoefficient;
        private double _minPumpRpm;
        private double _maxPumpRpm;
        private double _minPressure;
        private double _maxPressure;
        private double _psiPerRpm;
        private bool _ptoEngaged; // TODO: put this back to false and uncomment it in set data when PTO app is ready

        public Pump(double gearRatio, double fowResistanceCoefficient, double quadraticFlowCoefficient, double minPumpRpm, double maxPumpRpm, double minPressure, double maxPressure)
        {
            _gearRatio = gearRatio;
            _flowResistanceCoefficient= fowResistanceCoefficient;
            _quadraticFlowCoefficient= quadraticFlowCoefficient;
            _minPumpRpm = minPumpRpm;
            _maxPumpRpm = maxPumpRpm;
            _minPressure = minPressure;
            _maxPressure = maxPressure;

            // The raw PSI increase per pump RPM without external factors like flow rate
            _psiPerRpm = (_maxPressure - _minPressure) / (_maxPumpRpm - _minPumpRpm);
        }

        // Master pressure = psi at this rpm with 0 flow * (flow resistance coefficient # 1 * flow rate) + (flow resistance coefficient #2 * flowrate^2) + intake pressure
        internal void CalculatePressure(double flowRate, double engineRpm, double intakePressure, bool pumpHasWater)
        {
            double pumpRpm;
            double smoothingFactor = 0.7;

            // Pressure is 0 if there is no water in the pump
            if (!pumpHasWater)
            {
                MasterDischargePressure = 0.0;
                return;
            }

            // Determin pumpRpm
            if (_ptoEngaged)
            {
                pumpRpm = engineRpm * _gearRatio;
            }
            else
            {
                pumpRpm = 0.0;
            }

            // Determin raw pressure generated at this RPM without flow rate
            var noFlowPressure = _psiPerRpm * (pumpRpm - _minPumpRpm) + _minPressure;

            // Adjust for flow rate
            var generatedPressure = Math.Max(noFlowPressure + _flowResistanceCoefficient * flowRate + _quadraticFlowCoefficient * flowRate * flowRate, 0.0);

            // Smooth the generated pressure to help avoid spikes and keep things fluid
            //double smoothedGeneratedPressure = (smoothingFactor * _previousPumpPressure) + ((1 - smoothingFactor) * generatedPressure);

            double smoothedGeneratedPressure = (smoothingFactor * generatedPressure) + ((1 - smoothingFactor) * generatedPressure);

            // Add intake pressure
            MasterDischargePressure = smoothedGeneratedPressure + intakePressure;



            // Store the updated pressure for the next cycle
            _previousPumpPressure = MasterDischargePressure;

            //MasterDischargePressure = generatedPressure + intakePressure;

        }

        internal Dictionary<string, double> GetData()
        {
            var data = new Dictionary<string, double>();
            data[Consts.masterDischargePressure] = MasterDischargePressure;
            data[Consts.pto] = Convert.ToDouble(_ptoEngaged);
            return data;
        }

        internal void SetData(ConcurrentDictionary<string, double> data)
        {
            if (data.TryGetValue(Consts.pto, out var pto))
            {
                this._ptoEngaged = Convert.ToBoolean(pto);
            }
        }
    }  
}
