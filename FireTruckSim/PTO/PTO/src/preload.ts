import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("api", {
  sendUDP: (data: Record<string, number>) => {
    ipcRenderer.send("send-udp", data);
  },
  onPTOUpdate: (callback: (value: number) => void) => {
    ipcRenderer.on("pto-update", (_event, value) => {
      callback(value);
    });
  }
});
