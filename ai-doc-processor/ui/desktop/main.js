const { app, BrowserWindow, shell } = require("electron");
const path = require("path");

const WEB_URL = process.env.WEB_URL || "http://localhost:3000";

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "AI Document Processor",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Load the Next.js web UI (dev server or built static export)
  win.loadURL(WEB_URL);

  // Open external links in the system browser
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
