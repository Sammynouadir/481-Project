using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    internal class Engine
    {
        private double throttle = 0.5;
        private double idleRpm = 800;
        private double maxRpm = 2500;
        private double rpm;

        internal Dictionary<string, double> GetData()
        {
            var data = new Dictionary<string, double>();
            data[Consts.engineRpm] = rpm;
            return data;
        }

        internal void SetData(ConcurrentDictionary<string, double> data)
        {
            if (data.TryGetValue(Consts.throttle, out var throttle))
            {
                this.throttle = throttle;
            }
        }

        // Throttle acts as the % between idle and max rpm the engine will spin at
        internal void CalculateEngineRpm()
        {
            // Make sure thorttle is between 0.0 and 1.0
            var clampedThrottle = Math.Max(Math.Min(throttle, 1.0), 0.0);
            rpm = ((maxRpm - idleRpm) * clampedThrottle) + idleRpm;
        }
    }
}
