const { app, BrowserWindow, shell } = require('electron')
const path = require('path')
const http = require('http')
const fs = require('fs')

// 内嵌静态文件服务器（解决 loadFile 白屏问题）
const PORT = 3333

function getMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase()
  const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js':   'application/javascript',
    '.css':  'text/css',
    '.png':  'image/png',
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg':  'image/svg+xml',
    '.ico':  'image/x-icon',
    '.json': 'application/json',
    '.woff': 'font/woff',
    '.woff2':'font/woff2',
    '.ttf':  'font/ttf',
  }
  return mimeTypes[ext] || 'application/octet-stream'
}

function startServer(distDir) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      // 去掉 query string
      let urlPath = req.url.split('?')[0]
      if (urlPath === '/') urlPath = '/index.html'

      let filePath = path.join(distDir, urlPath)

      // 如果文件不存在，回退到 index.html（SPA 路由支持）
      if (!fs.existsSync(filePath)) {
        filePath = path.join(distDir, 'index.html')
      }

      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404)
          res.end('Not Found')
          return
        }
        res.writeHead(200, { 'Content-Type': getMimeType(filePath) })
        res.end(data)
      })
    })

    server.listen(PORT, '127.0.0.1', () => {
      resolve(server)
    })
  })
}

async function createWindow() {
  const distDir = path.join(__dirname, 'dist')
  await startServer(distDir)

  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: '纸张实验室 · 本地 OCR',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  win.loadURL(`http://127.0.0.1:${PORT}/`)

  // 外部链接在系统浏览器中打开
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // 隐藏菜单栏
  win.setMenuBarVisibility(false)
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
