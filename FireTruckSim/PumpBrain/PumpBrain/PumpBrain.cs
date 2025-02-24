using System;
using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Reflection.Metadata.Ecma335;
using System.Text;
using System.Threading.Tasks;
using static System.Runtime.InteropServices.JavaScript.JSType;



namespace PumpBrain
{
    public class PumpBrain
    {
        public TestToolSupport TestToolSupporter { get; }
        public ControlPanelInterface CPInterface { get; set; }
        internal UDPCommunicator UDPCom;
        internal bool Paused { get; set; } = true; // TODO: put this to true when you put it on github so the test tool doesn't send pumpBrain values
        private List<Discharge> _discharges = new List<Discharge>();
        private Discharge _discharge1;
        private Discharge _discharge2;
        private Discharge _discharge3;
        private Discharge _tankFillLine;
        private Hydrant _hydrant;
        private Pump _pump;
        private Engine _engine;
        private FoamSystem _foamSystem;
        private Timer _updateTimer;
        private bool _usingTankWater;
        private bool _pumpHasWater;
        private double _totalFlowRate;
        private double _waterTankLevel;
        private double _waterTankSize;
        private double _normalizedWaterTankLevel;
        private double _tankToPumpPosition;
        private double _intakePosition;
        private double _intakePressure;

        public PumpBrain()
        {
            // Set up coms
            TestToolSupporter = new TestToolSupport(this);
            UDPCom = new UDPCommunicator(this, Consts.listenPort);
            
            // Set up components
            _hydrant = new Hydrant(40.0, 20.0, 1500.0, new Hose(50.0, .08)); // .08 common for 5 inch supply hose
            _pump = new Pump(2.27, -0.004, -0.000032, 2250.0, 3375.0, 80.0, 170.0); // Modeled after common 1500gpm pump
            _engine = new Engine(800.0, 2500.0, 20.0);
            _foamSystem= new FoamSystem(30.0);
            _waterTankSize = 500.0;
            _waterTankLevel = 500.0;
            _normalizedWaterTankLevel = 1.0;

            // Set up discharges
            _discharge1 = new Discharge(1, new Hose(200.0, 15.5), 0.648749, "200ft 1.75\" Hose 125gpm @ 100psi Fog Nozzle");
            _discharge2 = new Discharge(2, new Hose(200.0, 15.5), 0.648749, "200ft 1.75\" Hose 125gpm @ 100psi Fog Nozzle");
            _discharge3 = new Discharge(3, new Hose(4.0, 0.2), 2.0, "Deluge with 2\" Smooth Bore Nozzle"); 
            _discharges.Add(_discharge1);
            _discharges.Add(_discharge2);
            _discharges.Add(_discharge3);

            // The tank fill line works just like a discharge
            _tankFillLine = new Discharge(4, new Hose(1.0, 2.0), 2.0, "tank fill line");

            // Start the sim timer
            _updateTimer = new Timer(SimulationTick);
            _updateTimer?.Change(0, (int)(Consts.dt * 1000));

            // Set up control panel interface
            CPInterface = new ControlPanelInterface(this);
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
            foreach (var kvp in _pump.GetData())
            {
                data[kvp.Key] = kvp.Value;
            }

            // get data from _foamSystem
            foreach (var kvp in _foamSystem.GetData())
            {
                data[kvp.Key] = kvp.Value;
            }

            // get data from _tankFillLine
            foreach (var kvp in _tankFillLine.GetData())
            {
                data[kvp.Key] = kvp.Value;
            }

            // get data from _discharges
            foreach (var discharge in _discharges)
            {
                foreach (var kvp in discharge.GetData())
                {
                    data[kvp.Key] = kvp.Value;
                }
            }

            // Add the data from PumpBrain
            data[Consts.totalFlowRate] = _totalFlowRate;
            data[Consts.normalizedWaterTankLevel] = _normalizedWaterTankLevel;
            data[Consts.tankToPumpPosition] = _tankToPumpPosition;
            data[Consts.intakePosition] = _intakePosition;
            data[Consts.intakePressure] = _intakePressure;

            // Add these just for being able to see in the test tool
            //data["hydrant connected"] = Convert.ToDouble(_hydrant.Connected);
            //data["hydrant flow rate"] = _hydrant.FlowRate;
            //data["hydrant pressure"] = _hydrant.Pressure;
            //data["water tank level"] = _waterTankLevel;
            //data["tank fill flow rate"] = _tankFillLine.FlowRate;
            //for (int i = 0; i < _discharges.Count; i++)
            //{
            //    data["nozzle " + i + " pressure"] = _discharges[i].GetNozzlePressureForTesting();
            //}

            return data;
        }

        internal void SetData(ConcurrentDictionary<string, double> data)
        {
            if (data.TryGetValue(Consts.tankToPumpPosition, out var tankToPumpPosition))
            {
                _tankToPumpPosition = tankToPumpPosition;
            }
            if (data.TryGetValue(Consts.intakePosition, out var intakePosition))
            {
                _intakePosition = intakePosition;
            }
        }

        // Handle the deserialized JSON that just came in
        internal void ProcessIncomingData(ConcurrentDictionary<string, double> receivedData)
        {
            // For python testing app
            TestToolSupporter.LatestMessage = receivedData;

            // Pass receievedData to all the components
            SetData(receivedData);
            _engine.SetData(receivedData);
            _pump.SetData(receivedData);
            _tankFillLine.SetData(receivedData);
            _foamSystem.SetData(receivedData);
            foreach (var discharge in _discharges)
            {
                discharge.SetData(receivedData);
            }

        }

        // Execute the simulation's core logic
        private void SimulationTick(object? state)
        {
            if (!Paused)
            {
                //double pumpInletPressure;
                double tankToPumpPressure = 1.0; // Pressure from the tank would depend on elevation relative to the pump which is too complex

                // Adjust valve positions
                _tankFillLine.AdjustPosition();
                foreach (var discharge in _discharges)
                {
                    discharge.AdjustPosition();
                }

                // Adjust engine rpm based on throttle from governor
                _engine.AdjustEngineRpm();

                // Set pump inlet pressure and keep track of water source
                // Pump inlet pressure is intake pressure if intake is open and connected to hydrant
                if (_hydrant.Connected && _intakePosition > 0.05)
                {
                    _intakePressure = _hydrant.Pressure * _intakePosition;
                    _pumpHasWater = true;
                    _usingTankWater = false;
                }
                // Pump inlet pressure is hard coded pressure from water tank if the T2P valve is open and there is water in tank
                else if (_tankToPumpPosition > 0.05 && _waterTankLevel > 0.01)
                {
                    _intakePressure = tankToPumpPressure * _tankToPumpPosition;
                    _pumpHasWater = true;
                    _usingTankWater = true;
                }
                // Pump inlet pressure is 0 if there is no water
                else
                {
                    _intakePressure = 0.0;
                    _pumpHasWater = false;
                    _usingTankWater = false;
                }
                
                // Calculate the pump pressure
                _pump.CalculatePressure(_totalFlowRate, _engine.Rpm, _intakePressure, _pumpHasWater);

                // Total flowrate used for hydrant pressure this frame and pump pressure next frame
                _totalFlowRate = CalculateTotalFlowRate(_pump.MasterDischargePressure);
                
                // Update the hydrant flow rate and calculate its pressure
                if (_hydrant.Connected && _intakePosition > 0.05 && !_usingTankWater)
                {
                    _hydrant.FlowRate = _totalFlowRate;
                    _hydrant.CalculatePressure();
                }

                // Update foam system
                _foamSystem.FlowFoam(_totalFlowRate);

                AdjustWaterTankLevel();
            }
        }

        // Sum up flowrate from all discharges + the tank fill line
        private double CalculateTotalFlowRate(double masterDischargePressure) 
        {
            double totalFlowRate = 0.0;

            // Discharges
            foreach (var discharge in _discharges)
            {
                // Pressure is needed in flow rate calculation
                discharge.CalculatePressure(masterDischargePressure);
                discharge.CalculateFlowRate();
                totalFlowRate += discharge.FlowRate;
            }

            // Tank fill line
            _tankFillLine.CalculatePressure(masterDischargePressure);
            _tankFillLine.CalculateFlowRate();
            totalFlowRate += _tankFillLine.FlowRate;

            return totalFlowRate;
        }

        // Water flows from tank if not using hydrant and T2P valve is open
        private void AdjustWaterTankLevel()
        {
            var changeInWaterLevel = 0.0; ;

            // Water used
            if (_usingTankWater)
            {
                changeInWaterLevel -= (_totalFlowRate / 60.0) * Consts.dt;
            }

            // Water coming in from tank fill valve
            if (_tankFillLine.Position > .05)
            {
                changeInWaterLevel += (_tankFillLine.FlowRate / 60.0) * Consts.dt;
            }

            // Keep water tank level between full size and 0
            _waterTankLevel = Math.Max(Math.Min(_waterTankLevel + changeInWaterLevel, _waterTankSize), 0.0);

            // Calculate normalized water tank level which is sent out to the gauges
            _normalizedWaterTankLevel = _waterTankLevel / _waterTankSize;
        }

        /// <summary>
        /// A class to be used by the control panel to get and set values of the running instance of PumpBrain
        /// </summary>
        public class ControlPanelInterface
        {
            private PumpBrain _brain;
            public ControlPanelInterface(PumpBrain brain)
            {
                _brain = brain;
            }

            public void SetPauseState(bool pause)
            {
                _brain.Paused = pause;
            }

            public bool GetPauseState()
            {
                return _brain.Paused;
            }

            public void SetHydrantConnected(bool connected)
            {
                _brain._hydrant.Connected = connected;
            }

            public bool GetHydrantConnected()
            {
                return _brain._hydrant.Connected;
            }

            public double GetHydrantPressure()
            {
                return _brain._hydrant.Pressure;
            }

            public double GetHydrantFlowRate()
            {
                return _brain._hydrant.FlowRate;
            }

            public double GetWaterTankLevel()
            {
                return _brain._waterTankLevel;
            }

            public double GetFoamTankLevel()
            {
                return _brain._foamSystem.FoamTankLevel;
            }

            public List<double> GetNozzlePressures()
            {
                var nozzlePressures = new List<double>();

                foreach (var discharge in _brain._discharges)
                {
                    nozzlePressures.Add(discharge.Pressure);
                }

                return nozzlePressures;
            }

            public List<double> GetNozzleFlowRates()
            {
                var nozzleFlowRates = new List<double>();

                foreach (var discharge in _brain._discharges)
                {
                    nozzleFlowRates.Add(discharge.FlowRate);
                }

                return nozzleFlowRates;
            }

            public List<string> GetDischargeDescriptions()
            {
                var descriptions = new List<string>();

                foreach (var discharge in _brain._discharges)
                {
                    descriptions.Add(discharge.Description);
                }

                return descriptions;
            }
        }
    }
}
