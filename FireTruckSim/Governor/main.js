const { app, BrowserWindow } = require('electron')
const dgram = require('dgram')
const path = require('node:path')

const BRAIN_PORT = 8150
const GOV_PORT = 8153

const createWindow = () => {
  const win = new BrowserWindow({
    width: 400,
    height: 300,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    },
  })

  win.loadFile('index.html')
}

app.whenReady().then(() => {
  const server = dgram.createSocket('udp4', { port: GOV_PORT })

  server.on('message', (msg, info) => {
    // Parse serialized JSON message
    const jsonList = JSON.parse(msg.toString())

    // Handle received message
    console.log('Received serialized JSON message:', jsonList)
    const response = JSON.stringify([{ Key: "Throttle", Value: 100 }])
    server.send(response, BRAIN_PORT)
  })

  server.on('listening', () => {
    const address = server.address()
    console.log(`UDP server listening on ${address.address}:${address.port}`)
  })

  server.bind(GOV_PORT)

  createWindow()

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
