using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Threading;

namespace PumpBrain
{
    internal class UDPCommunicator
    {
        private readonly PumpBrain _brain;
        private readonly UdpClient _udpSender;
        private readonly Timer _udpSendingTimer;
        private readonly UdpClient _udpListener;
        private readonly List<int> ports;
        private readonly ConcurrentQueue<ConcurrentDictionary<string, double>> _messageQueue = new ConcurrentQueue<ConcurrentDictionary<string, double>>();
        private readonly CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();

        internal UDPCommunicator(PumpBrain brain, int listeningPort)
        {
            _brain = brain;

            // Initialize UDP clients
            _udpSender = new UdpClient();
            _udpListener = new UdpClient(listeningPort);
            StartListening();

            // List of ports
            ports = new List<int>
            {
                Consts.listenPort, // THIS IS SENDING TO ITSELF, REMOVE THIS AT SOME POINT
                Consts.sendPortPTO,
                Consts.sendPortFoamController,
                Consts.sendPortGovernor,
                Consts.sendPortValveController1,
                Consts.sendPortValveController2,
                Consts.sendPortValveController3,
                Consts.sendPortValveController4,
                Consts.sendPortValveController5,
                Consts.sendPortValveController6,
                Consts.sendPortGauge1,
                Consts.sendPortGauge2,
                Consts.sendPortGauge3,
                Consts.sendPortGauge4,
                Consts.sendPortGauge5,
                Consts.sendPortGauge6,
                Consts.sendPortGauge7
            };

            // Timer for sending data
            _udpSendingTimer = new Timer(GetAndSendUDP, null, Timeout.Infinite, Timeout.Infinite);
            _udpSendingTimer?.Change(0, (int)(Consts.dt * 1000));

            // Task to handle and queue the incoming UDP messages
            Task.Run(() => ProcessMessageQueue(_cancellationTokenSource.Token));
        }

        internal void StartListening()
        {
            _udpListener.BeginReceive(OnMessageReceived, null);
        }

        internal void StopListening()
        {
            _udpListener.Close();
        }

        // Sends the message to all of the ports in the list
        internal void SendUDP(Dictionary<string, double> data, List<int> ports)
        {
            // Serialize to JSON
            string jsonData = JsonSerializer.Serialize(data);

            // Send JSON over UDP
            byte[] bytes = Encoding.UTF8.GetBytes(jsonData);
            foreach (var port in ports)
            {
                _udpSender.Send(bytes, bytes.Length, Consts.ip, port);
            }
        }

        // Callback for receiving UDP messages
        private void OnMessageReceived(IAsyncResult result)
        {
            try
            {
                IPEndPoint sender = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = _udpListener.EndReceive(result, ref sender);

                // Deserialize JSON
                string message = Encoding.UTF8.GetString(data);
                var receivedData = JsonSerializer.Deserialize<ConcurrentDictionary<string, double>>(message);

                // Pass the received data to the PumpBrain for processing
                if (receivedData != null)
                {
                    _messageQueue.Enqueue(receivedData);
                }

                // Continue listening
                _udpListener.BeginReceive(OnMessageReceived, null);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error receiving UDP message: {ex.Message}");
            }
        }

        // Pass the message to PumpBrain in a threadsafe, queued fasion
        private async Task ProcessMessageQueue(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                if (_messageQueue.TryDequeue(out var nextMessage))
                {
                    _brain.ProcessIncomingData(nextMessage);
                }
            }

            await Task.Delay(1);
        }

        // Timer callback for sending periodic UDP updates
        private void GetAndSendUDP(object? state)
        {
            if (!_brain.Paused)
            {
                SendUDP(_brain.GetData(), ports);
            }
        }
    }
}
