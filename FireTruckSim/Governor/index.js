const { ipcRenderer } = require('electron')

// keys of interest in the JSON object received over socket
const keys = ["master discharge pressure", "intake pressure", "engine rpm"]

// engine throttle (sent but not received over socket)
let throttle

// update display text
ipcRenderer.on('update-text', (_event, msg) => {
  // these values should be displayed as integers based on value received over socket
  for (const key of keys) {
    const id = key.replaceAll(" ", "-")
    const element = document.getElementById(id)
    if (element) element.innerText = Math.round(msg[ key ])
  }

  // set PTO indicator on/off
  const ptoIndicator = document.getElementById("pto")
  if (msg.pto >= 0.5) {
    ptoIndicator.innerText = "On"
  } else {
    ptoIndicator.innerText = "Off"
  }
})

// increment (or decrement) throttle by small amount based on difference between target and discharge pressures
ipcRenderer.on('inc-throttle', (_event, msg) => {
  // throttle must be 0 if PTO is not enabled
  if (msg.pto < 0.5) {
    throttle = 0
  } else {
    const target = document.getElementById("target-pressure").innerText
    throttle += 0.001 * (target - msg[ "master discharge pressure" ])
  }

  // send throttle over socket
  ipcRenderer.send('send-throttle', throttle)
})

// increment (or decrement if negative) target pressure by n
// target pressure is not sent over the socket and is only stored in the element's innerText
function incTarget(n) {
  const targetElem = document.getElementById("target-pressure")
  let target = Number(targetElem.innerText) + n
  if (target < 0) target = 0
  targetElem.innerText = target
}
