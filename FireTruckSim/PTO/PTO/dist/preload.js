"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
electron_1.contextBridge.exposeInMainWorld("api", {
    sendUDP: (data) => {
        electron_1.ipcRenderer.send("send-udp", data);
    },
    onPTOUpdate: (callback) => {
        electron_1.ipcRenderer.on("pto-update", (_event, value) => {
            callback(value);
        });
    }
});
