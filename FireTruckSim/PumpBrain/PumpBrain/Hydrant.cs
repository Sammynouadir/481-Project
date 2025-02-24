using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    public class Hydrant
    {
        internal bool Connected = false;
        internal double FlowRate { get; set; }
        internal double Pressure { get; private set; }
        private double _noFlowPressure;
        private double _residualPressure;
        private double _flowRateAtResidualPressure;
        private double _pressureDropCoefficiant;
        private Hose _supplyHose;

        internal Hydrant(double noFlowPressure, double residualPressure, double flowRateAtResidualPressure, Hose supplyHose)
        {
            _noFlowPressure = noFlowPressure;
            _residualPressure = residualPressure;
            _flowRateAtResidualPressure = flowRateAtResidualPressure;
            _supplyHose = supplyHose;

            // Pressure starts out at the no flow pressure
            Pressure = _noFlowPressure;

            // Calculate the pressure drop coefficiant used later to calculate pressure at a given flow rate
            _pressureDropCoefficiant = (_noFlowPressure - _residualPressure) / (_flowRateAtResidualPressure / 100.0) / (_flowRateAtResidualPressure / 100.0);
        }

        // Pressure = (pressure with no flow - (flowrate / 100)^2 * pressure drop coefficiant) - hose friciton loss
        internal void CalculatePressure()
        {
            if (Connected)
            {
                Pressure = (_noFlowPressure - Math.Pow((FlowRate / 100.0), 2.0) * _pressureDropCoefficiant) - _supplyHose.CalculateHoseFrictionLoss();
            }
            else
            {
                Pressure = 0.0;
            }
        }

    }
}
