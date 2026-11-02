export default {
  server: {
    port: 5176,
    proxy: {
      "/status": "http://127.0.0.1:8767",
      "/wave": "http://127.0.0.1:8767",
      "/gps": "http://127.0.0.1:8767",
      "/ai": "http://127.0.0.1:8767"
    }
  }
};
