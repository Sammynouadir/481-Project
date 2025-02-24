using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PumpBrain
{
    // Functions and values made accessable for a python based tool used to test sending/receiving UDP messages using this .dll
    public class TestToolSupport
    {
        private PumpBrain _brain;
        public ConcurrentDictionary<string, double> LatestMessage;

        internal TestToolSupport(PumpBrain brain)
        {
            _brain = brain;
        }

        public string TestStart()
        {
            return "Start called";
        }

        public string TestStop()
        {
            return "Stop called";
        }

        public string TestPause()
        {
            return "Pause called";
        }

        public void BackDoorSendTestUDP(Dictionary<string, double> data, int port)
        {
            
            _brain.UDPCom.SendUDP(data, new List<int> { port });
        }
    }
}
