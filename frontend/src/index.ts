import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
  },
});

app.get("/", (_req, res) => {
  res.send(`<html><head><title>TS Socket Demo</title></head><body><h1>TypeScript Socket.IO Server</h1><script src="/socket.io/socket.io.js"></script><script>const s = io(); s.on('connect', ()=>console.log('connected'));</script></body></html>`);
});

io.on("connection", (socket) => {
  console.log("client connected", socket.id);
  socket.emit("welcome", { msg: "hello from TS server" });
  socket.on("ping", () => socket.emit("pong"));
});

const port = process.env.PORT || 4000;
httpServer.listen(port, () => console.log(`TS server listening on ${port}`));
