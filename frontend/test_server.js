const http = require('http');
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('Hello from Test Server');
});
server.listen(3005, () => console.log('Test Server running on 3005'));
