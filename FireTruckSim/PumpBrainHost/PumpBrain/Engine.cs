using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    internal class Engine
    {
        public double Rpm { get; private set; }
        private double _throttle = 0.0;
        private double _idleRpm;
        private double _maxRpm;
        private double _engineSpeed; // Determines how fast engine adjusts RPM

        public Engine(double idleRpm, double maxRpm, double engineSpeed)
        {
            _idleRpm = idleRpm;
            _maxRpm = maxRpm;
            _engineSpeed = Math.Max(engineSpeed, 0.0000001); // must be above 0.0
        }

        // Throttle acts as the % between idle and max rpm the engine will spin at
        internal void AdjustEngineRpm()
        {
            // Make sure thorttle is between 0.0 and 1.0
            var clampedThrottle = Math.Max(Math.Min(_throttle, 1.0), 0.0);

            // Find target RPM
            var targetRpm = ((_maxRpm - _idleRpm) * clampedThrottle) + _idleRpm;

            // STYLE 1: Adjust RPM a fixed amount
            // Move towards the target RPM without going past it
            if (targetRpm - Rpm > 0.0) // Moving up
            {
                if (Rpm + _engineSpeed > targetRpm) // Don't go past the target
                {
                    Rpm = targetRpm;
                }
                else
                {
                    Rpm += _engineSpeed;
                }
            }
            else if (targetRpm - Rpm < 0.0) // Moving down
            {
                if (Rpm - _engineSpeed < targetRpm) // Don't go past the target
                {
                    Rpm = targetRpm;
                }
                else
                {
                    Rpm -= _engineSpeed;
                }
            }

            //// STYLE 2: Change RPM faster when further away from target
            //// Find target RPM and calculate how far away it is from the current Rpm
            //var targetDelta = targetRpm - Rpm;

            //// Smoothly move actual RPM towards target RPM
            //Rpm = Rpm + (targetDelta * _engineSpeed);

            //// STYLE 3: Snap RPM to correct position
            //Rpm = ((_maxRpm - _idleRpm) * clampedThrottle) + _idleRpm;
        }

        internal Dictionary<string, double> GetData()
        {
            var data = new Dictionary<string, double>();
            data[Consts.engineRpm] = Rpm;
            return data;
        }

        internal void SetData(ConcurrentDictionary<string, double> data)
        {
            if (data.TryGetValue(Consts.throttle, out var throttle))
            {
                this._throttle = throttle;
            }
        }
    }
}
