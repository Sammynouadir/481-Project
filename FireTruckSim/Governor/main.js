const { app, BrowserWindow, ipcMain } = require('electron')
const dgram = require('dgram')
const path = require('node:path')

const BRAIN_PORT = 8150
const GOV_PORT = 8153

let mainWindow

const createWindow = () => {
  const win = new BrowserWindow({
    width: 400,
    height: 300,
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
    },
  })

  win.loadFile('index.html')
  mainWindow = win
}

app.whenReady().then(() => {
  const server = dgram.createSocket('udp4', { port: GOV_PORT })
  server.bind(GOV_PORT)

  createWindow()

  server.on('listening', () => {
    const address = server.address()
    console.log(`UDP server listening on ${address.address}:${address.port}`)
  })

  server.on('message', (msg, info) => {
    // Parse serialized JSON message
    const jsonList = JSON.parse(msg.toString())

    // Handle received message
    console.log('Received serialized JSON message:', jsonList)
    mainWindow.webContents.send('update-text', jsonList)
    mainWindow.webContents.send('inc-throttle', jsonList)
  })

  ipcMain.on('send-throttle', (_event, throttle) => {
    server.send(JSON.stringify({ "throttle": throttle }), BRAIN_PORT)
  })

  // show window when activating on macOS
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// quit when all windows are closed on Windows/Linux
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
