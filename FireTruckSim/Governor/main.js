const { app, BrowserWindow, ipcMain } = require('electron')
const dgram = require('dgram')

// receive over GOV_PORT, send over BRAIN_PORT
const BRAIN_PORT = 8150
const GOV_PORT = 8153

// there is only 1 main window
let mainWindow

// create main window
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
  // socket over which to communicate with pump brain
  const socket = dgram.createSocket('udp4', { port: GOV_PORT })
  socket.bind(GOV_PORT)

  // show main window
  createWindow()

  // UDP message received
  socket.on('message', (msg, info) => {
    // Parse serialized JSON message
    const json = JSON.parse(msg.toString())

    // Handle received message
    console.log('Received serialized JSON message:', json)
    mainWindow.webContents.send('update-text', json)
    mainWindow.webContents.send('inc-throttle', json)
  })

  // only thing needed to send back is throttle
  ipcMain.on('send-throttle', (_event, throttle) => {
    socket.send(JSON.stringify({ "throttle": throttle }), BRAIN_PORT)
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
