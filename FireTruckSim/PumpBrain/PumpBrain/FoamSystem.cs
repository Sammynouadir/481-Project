using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{   
    internal class FoamSystem
    {
        internal double FoamTankLevel { get; private set; }
        private double _normalizedFoamLevel;
        private double _foamTankSize;
        private bool _foamSystemPower;
        private double _foamConcentration;
        private double _foamFlowRate;
        private double _totalFoamFlowed;

        internal FoamSystem(double tankSize)
        {
            _foamTankSize = tankSize;
            
            // Starts with power off and full tank
            _foamSystemPower = false;
            FoamTankLevel = _foamTankSize;
            _normalizedFoamLevel = 1.0;
            _foamConcentration = 0.0;
            _totalFoamFlowed = 0.0;
        }

        // Called each frame to keep track of how much foam has been flowed and how much is left in the tank
        internal void FlowFoam(double waterFlowRate)
        {
            // Calculate flow rate of foam. It's just water flow rate * foam concentration
            if (_foamSystemPower)
            {
                _foamFlowRate = waterFlowRate * _foamConcentration;
            }
            else // Don't flow foam when system is off
            {
                _foamFlowRate = 0.0;
            }

            // Calculate change in foam level this frame
            var changeInFoamLevel = (_foamFlowRate / 60.0) * Consts.dt;

            // Track total amount of foam flowed
            _totalFoamFlowed += changeInFoamLevel;

            // Adjust tank level while keeping it between full size and 0
            FoamTankLevel = Math.Max(Math.Min(FoamTankLevel + changeInFoamLevel, _foamTankSize), 0.0);

            // Calculate normalized foam tank level which is sent out to the gauges
            _normalizedFoamLevel = FoamTankLevel / _foamTankSize;
        }

        internal Dictionary<string, double> GetData()
        {
            var data = new Dictionary<string, double>();
            data[Consts.foamConcentration] = _foamConcentration;
            data[Consts.foamFlowRate] = _foamFlowRate;
            data[Consts.foamFlowTotal] = _totalFoamFlowed;
            data[Consts.foamSystemPower] = Convert.ToDouble(_foamSystemPower);
            data[Consts.normalizedFoamTankLevel] = _normalizedFoamLevel;
            return data;
        }

        internal void SetData(ConcurrentDictionary<string, double> data)
        {
            if (data.TryGetValue(Consts.foamConcentration, out var concentration))
            {
                _foamConcentration = concentration;
            }
            if (data.TryGetValue(Consts.foamSystemPower, out var foamSystemPower))
            {
                _foamSystemPower = Convert.ToBoolean(foamSystemPower);
            }
        }
    }
}
