"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
const url = __importStar(require("url"));
const dgram = __importStar(require("dgram"));
// Handle sending
const udpSocket = dgram.createSocket("udp4");
electron_1.ipcMain.on("send-udp", (event, data) => {
    const message = Buffer.from(JSON.stringify(data));
    udpSocket.send(message, 8150, "127.0.0.1");
    console.log("Sent UDP message:", data);
});
// Handle listening
const listenerSocket = dgram.createSocket("udp4");
listenerSocket.on("message", (msg, rinfo) => {
    try {
        const data = JSON.parse(msg.toString());
        if ("pto" in data) {
            mainWindow?.webContents.send("pto-update", data.pto);
        }
    }
    catch (err) {
        console.error("Invalid UDP message received:", err);
    }
});
listenerSocket.bind(8151);
const isDev = process.env.NODE_ENV !== "production";
// Auto reload to make my life easier
if (isDev) {
    require("electron-reload")(__dirname, {
        electron: path.join(__dirname, "../node_modules/.bin/electron.cmd"),
        forceHardReset: true,
        hardResetMethod: "exit"
    });
}
let mainWindow = null;
function createWindow() {
    mainWindow = new electron_1.BrowserWindow({
        width: 250,
        height: 300,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
            nodeIntegration: false,
            devTools: true,
        },
    });
    if (isDev) {
        mainWindow.loadURL("http://localhost:5173");
        mainWindow.webContents.openDevTools();
    }
    else {
        mainWindow.loadURL(url.format({
            pathname: path.join(__dirname, "../dist-renderer/index.html"),
            protocol: "file:",
            slashes: true,
        }));
        console.log("Loading from", path.join(__dirname, "../dist-renderer/index.html"));
    }
    mainWindow.on("closed", () => {
        mainWindow = null;
    });
}
electron_1.app.whenReady().then(createWindow);
electron_1.app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        electron_1.app.quit();
    }
});
electron_1.app.on("activate", () => {
    if (mainWindow === null) {
        createWindow();
    }
});
