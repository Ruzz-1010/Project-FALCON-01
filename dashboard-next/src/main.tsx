import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";
import "./wave.css";
import "./motion.css";
import "leaflet/dist/leaflet.css";
import "./gps.css";
import "./power.css";
import "./system.css";

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
