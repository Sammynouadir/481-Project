import { app, BrowserWindow, ipcMain } from "electron";
import * as path from "path";
import * as url from "url";
import * as dgram from "dgram";

// Handle sending
const udpSocket = dgram.createSocket("udp4");
ipcMain.on("send-udp", (event, data: Record<string, number>) => {
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
  } catch (err) {
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

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
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
  } else {
    mainWindow.loadURL(
      url.format({
        pathname: path.join(__dirname, "../dist-renderer/index.html"),
        protocol: "file:",
        slashes: true,
      })
    );
    console.log("Loading from", path.join(__dirname, "../dist-renderer/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow === null) {
    createWindow();
  }
});
