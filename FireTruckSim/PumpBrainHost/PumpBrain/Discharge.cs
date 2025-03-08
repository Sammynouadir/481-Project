using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    internal class Discharge
    {
        internal double FlowRate { get; private set; }
        internal double Pressure { get; private set; }
        internal double Position { get; private set; }
        internal string Description { get; private set; }
        private Hose _hose;
        private int _id;
        private string _flowRateKey;
        private string _pressureKey;
        private string _positionKey;
        private double _nozzleDiameter;
        private double _nozzleDiameterSquared;
        private double _nozzlePressure;
        private double _previousPressure;
        private double _targetPosition;

        public Discharge(int id, Hose hose, double nozzleDiameter, string description)
        {
            _hose = hose;
            _nozzleDiameter = nozzleDiameter;
            Description = description;
            _nozzleDiameterSquared = _nozzleDiameter * _nozzleDiameter;

            // Set UDP keys. There will be one object created for each ID so they remaine unique
            switch (id)
            {
                case 1:
                    _flowRateKey = Consts.discharge1FlowRate;
                    _pressureKey = Consts.discharge1Pressure;
                    _positionKey = Consts.discharge1Position;
                    break;

                case 2:
                    _flowRateKey = Consts.discharge2FlowRate;
                    _pressureKey = Consts.discharge2Pressure;
                    _positionKey = Consts.discharge2Position;
                    break;

                case 3:
                    _flowRateKey = Consts.discharge3FlowRate;
                    _pressureKey = Consts.discharge3Pressure;
                    _positionKey = Consts.discharge3Position;
                    break;

                case 4: // For tank fill line
                    _flowRateKey = Consts.tankFilleFlowRate;
                    _pressureKey = Consts.tankFillPressure;
                    _positionKey = Consts.tankFillPosition;
                    break;

                default:
                    _flowRateKey = "";
                    _pressureKey = "";
                    _positionKey = "";
                    break;
            }
        }

        // Flow rate = water friction * diameter^2 * sqrt(pressure)
        public void CalculateFlowRate()
        {
            // Subtract hose friction loss from pressure
            _nozzlePressure = Pressure - _hose.CalculateHoseFrictionLoss();

            // Set flow rate to 0 if discharge is closed or pressure is 0
            if (_nozzlePressure < 0.01 || Position < .05)
            {
                FlowRate = 0.0;
                _hose.FlowRate = FlowRate;
            }
            else // Calculate the flow rate and update the hoses flow rate
            {
                // Smooth the change in flow rate to avoid spiking cycle
                double smoothingFactor = 0.1;
                double maxFlowChange = 10.0;
                double newFlowRate = smoothingFactor * FlowRate + (1 - smoothingFactor) * (Consts.waterFlowRateCoefficient * _nozzleDiameterSquared * Math.Sqrt(_nozzlePressure));
                FlowRate = Math.Clamp(newFlowRate, FlowRate - maxFlowChange, FlowRate + maxFlowChange);
                _hose.FlowRate = FlowRate;
            }
        }

        // Pressure = master pressure * position
        internal void CalculatePressure(double masterPressure)
        {
            if (masterPressure < 0.1)
            {
                // Just lock at 0 if the pressure is this low. Helps avoid spiking.
                Pressure = 0.0;
            }
            else
            {
                // Smooth the change in flowrate to help avoid spiking and keep things fluid
                double smoothingFactor = 0.2;
                Pressure = smoothingFactor * _previousPressure + (1 - smoothingFactor) * masterPressure * Position;
            }

            // Store previous pressure to allow to smooth changes
            _previousPressure = Pressure;
        }

        // Smooth change in valve position to help avoid spiking
        internal void AdjustPosition()
        {
            double maxValveChangePerTick = 0.05;

            // Move toward the target position gradually
            double change = Math.Clamp(_targetPosition - Position, -maxValveChangePerTick, maxValveChangePerTick);
            Position += change;
        }

        internal Dictionary<string, double> GetData()
        {
            var data = new Dictionary<string, double>();
            data[_flowRateKey] = FlowRate;
            data[_pressureKey] = Pressure;
            data[_positionKey] = Position;
            return data;
        }

        internal void SetData(ConcurrentDictionary<string, double> data)
        {
            if (data.TryGetValue(_positionKey, out var position))
            {
                _targetPosition = position;
            }
        }

        // TODO: remove this, it's just for testing so you can put it up on the test tool
        internal double GetNozzlePressureForTesting()
        {
            return _nozzlePressure;
        }
    }
}