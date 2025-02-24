using System;
using System.Collections.Generic;
using System.Data.SqlTypes;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    static internal class Consts
    {
        public static readonly double dt = .05;
        public static readonly string ip = "127.0.0.1";

        // Ports
        public static readonly int listenPort = 8150;
        public static readonly int sendPortPTO = 8151;
        public static readonly int sendPortFoamController = 8152;
        public static readonly int sendPortGovernor = 8153;
        public static readonly int sendPortValveController1 = 8154;
        public static readonly int sendPortValveController2 = 8155;
        public static readonly int sendPortValveController3 = 8156;
        public static readonly int sendPortValveController4 = 8157;
        public static readonly int sendPortValveController5 = 8158;
        public static readonly int sendPortValveController6 = 8159;
        public static readonly int sendPortGauge1 = 8160;
        public static readonly int sendPortGauge2 = 8161;
        public static readonly int sendPortGauge3 = 8162;
        public static readonly int sendPortGauge4 = 8163;
        public static readonly int sendPortGauge5 = 8164;
        public static readonly int sendPortGauge6 = 8165;
        public static readonly int sendPortGauge7 = 8166;

        // PTO
        public static readonly string pto = "pto";

        // Governor
        public static readonly string throttle = "throttle";
        public static readonly string engineRpm = "engine rpm";
        
        // Foam Controller
        public static readonly string foamSystemPower = "foam system power";
        public static readonly string foamConcentration = "foam concentration";
        public static readonly string foamFlowRate = "foam flow rate";
        public static readonly string foamFlowTotal = "foam flow total";

        // Gauges
        public static readonly string intakePressure = "intake pressure"; // Governor also needs this
        public static readonly string masterDischargePressure = "master discharge pressure"; // Governor also needs this
        public static readonly string discharge1Pressure = "discharge 1 pressure";
        public static readonly string discharge2Pressure = "discharge 2 pressure";
        public static readonly string discharge3Pressure = "discharge 3 pressure";
        public static readonly string discharge1FlowRate = "discharge 1 flow rate";
        public static readonly string discharge2FlowRate = "discharge 2 flow rate";
        public static readonly string discharge3FlowRate = "discharge 3 flow rate";
        public static readonly string normalizedWaterTankLevel = "normalized water tank level";
        public static readonly string normalizedFoamTankLevel = "normalized foam tank level";

        // Valve controllers
        public static readonly string discharge1Position = "discharge 1 position";
        public static readonly string discharge2Position = "discharge 2 position";
        public static readonly string discharge3Position = "discharge 3 position";
        public static readonly string intakePosition = "intake position";
        public static readonly string tankToPumpPosition = "tank to pump position";
        public static readonly string tankFillPosition = "tank fill position";
    }
}
