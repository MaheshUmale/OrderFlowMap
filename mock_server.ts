const server = Bun.serve({
  port: 8765,
  fetch(req, server) {
    if (server.upgrade(req)) return;
    return new Response("Not a websocket", { status: 400 });
  },
  websocket: {
    message(ws, message) {
      const msg = JSON.parse(message.toString());
      if (msg.action === 'authenticate') {
        ws.send(JSON.stringify({ message: "Authentication successful", status: "success" }));
      } else if (msg.action === 'subscribe') {
        ws.send(JSON.stringify({ message: `Subscribed to ${msg.symbol}`, status: "success" }));
        let ltp = 25000, vol = 10000;
        const timer = setInterval(() => {
          const change = (Math.random() - 0.5) * 5;
          ltp = parseFloat((ltp + change).toFixed(2));
          const qty = Math.floor(Math.random() * 50) + 1;
          vol += qty;
          ws.send(JSON.stringify({
            type: "market_data",
            data: {
              symbol: msg.symbol, ltp, v: vol, lq: qty, ts: Date.now(),
              depth: {
                buy: [{ price: parseFloat((ltp - 0.05).toFixed(2)), quantity: 100 }],
                sell: [{ price: parseFloat((ltp + 0.05).toFixed(2)), quantity: 120 }]
              }
            }
          }));
        }, 300);
        ws.data = { timer };
      }
    },
    close(ws) { if (ws.data?.timer) clearInterval(ws.data.timer); }
  },
});
