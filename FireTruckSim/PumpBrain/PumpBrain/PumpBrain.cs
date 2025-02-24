using System;
using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace PumpBrain
{
    public class PumpBrain
    {
        public TestToolSupport TestToolSupporter { get; }
        internal UDPCommunicator UDPCom;
        private Timer _updateTimer;
        public bool Paused { get; set; } = false;
        private Pump _pump { get; set; }
        private Engine _engine { get; set; }
        private FoamSystem _foamSystem { get; set; }


        public PumpBrain()
        {
            TestToolSupporter = new TestToolSupport(this);
            UDPCom = new UDPCommunicator(this, Consts.listenPort);
            _pump = new Pump(2.27, 2250.0, 3375.0, 80.0, 170.0, 1500.0);
            _engine = new Engine();
            _foamSystem= new FoamSystem();
            _updateTimer = new Timer(SimulationTick);
            _updateTimer?.Change(0, (int)(Consts.dt * 1000));
        }

        // Put all data that is going to be sent over UDP into a dictionary
        internal Dictionary<string, double> GetData()
        {
            var data = new Dictionary<string, double>();

            // get data from _engine
            foreach (var kvp in _engine.GetData())
            {
                data[kvp.Key] = kvp.Value;
            }
            // get data from _pump
            // get data from _foamSystem
            // Put all of theses into one dictonary and return it
            return data;
        }

        // Handle the deserialized JSON that just came in
        internal void ProcessIncomingData(ConcurrentDictionary<string, double> receivedData)
        {
            // For python testing app
            TestToolSupporter.LatestMessage = receivedData;

            // Pass receievedData to all the components
            _engine.SetData(receivedData);
        }

        /// <summary>
        /// Calculate the engine RPM based on the throttle
        /// Calculate pump discharge pressure
        /// </summary>
        // Execute the simulation's core logic
        private void SimulationTick(object? state)
        {
            if (!Paused)
            {
                // Set engine speed
                // Set the pump speed
                // Calculate intake pressure
                // Calculate discharge pressures
                // Calculate flow rates
                // Handle water tank
                // Handle foam
                _engine.CalculateEngineRpm();

            }
        }
    }
}
