using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    internal class Hose
    {
        internal double FlowRate;
        private double _length;
        private double _friction;

        internal Hose(double length, double friction)
        {
            _length = length;
            _friction = friction;
        }

        // Friction loss is length * friction loss coefficient * flow rate ^ 2
        internal double CalculateHoseFrictionLoss()
        {
            return (_length / 100.0) * _friction * Math.Pow((FlowRate / 100.0), 2.0);
        }
    }
}
