// Local visual preview. Native Windows actions are unavailable in the browser.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const port = Number(process.env.MIDNIGHT_PREVIEW_PORT || 4173);
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.ico':'image/x-icon','.mp3':'audio/mpeg'};
const publicFiles = new Set(['index.html', 'styles.css', 'styles-modern.css', 'interface.css', 'renderer.js', 'interface.js']);
http.createServer((request, response) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname); }
  catch { response.writeHead(400).end(); return; }
  if(!['GET','HEAD'].includes(request.method)) { response.writeHead(405).end(); return; }
  const file = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
  const relative = path.relative(root, file);
  if(relative.startsWith('..') || path.isAbsolute(relative) || !(publicFiles.has(relative) || relative.startsWith('assets' + path.sep))) {
    response.writeHead(404).end(); return;
  }
  fs.readFile(file, (error, data) => {
    if(error) { response.writeHead(404).end(); return; }
    response.writeHead(200, {'Content-Type':types[path.extname(file)] || 'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
    response.end(request.method === 'HEAD' ? undefined : data);
  });
}).listen(port, '127.0.0.1', () => console.log(`Midnight preview: http://127.0.0.1:${port}/?preview=1`));
