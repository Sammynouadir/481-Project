const { ipcRenderer } = require('electron')

const keys = ["master discharge pressure", "intake pressure", "engine rpm"]

ipcRenderer.on('update-text', (_event, jsonList) => {
  for (const key of keys) {
    const id = key.replaceAll(" ", "-")
    const element = document.getElementById(id)
    if (element) element.innerText = Math.round(jsonList[ key ])
  }

  const ptoIndicator = document.getElementById("pto")
  if (jsonList.pto >= 0.5) {
    ptoIndicator.innerText = "On"
  } else {
    ptoIndicator.innerText = "Off"
  }
})

ipcRenderer.on('inc-throttle', (_event, msg) => {
  if (msg.throttle == null || msg.pto < 0.5) {
    msg.throttle = 0
  } else {
    const target = document.getElementById("target-pressure").innerText
    msg.throttle += 0.001 * (target - msg[ "master discharge pressure" ])
  }

  ipcRenderer.send('send-throttle', msg.throttle)
})

function incTarget(n) {
  const targetElem = document.getElementById("target-pressure")
  let target = Number(targetElem.innerText) + n
  if (target < 0) target = 0
  targetElem.innerText = target
}
