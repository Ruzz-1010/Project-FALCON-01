import {fileURLToPath} from 'node:url';
const local = path => fileURLToPath(new URL(path, import.meta.url));
export default {
  root: local('./'), base: './', publicDir: false,
  resolve: {alias: {three: local('../dashboard-next/node_modules/three')}},
  server: {host: '127.0.0.1', port: 5175, strictPort: true, fs: {allow: [local('../')]}},
  preview: {host: '127.0.0.1', port: 4175, strictPort: true},
  build: {
    outDir: 'dist', emptyOutDir: true,
    rollupOptions: {input: {main: local('./index.html'), present: local('./present.html'), lite: local('./lite-buoy.html')}}
  }
};
