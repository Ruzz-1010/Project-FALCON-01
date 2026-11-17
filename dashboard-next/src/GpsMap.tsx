import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import type { Gps } from "./types";

export default function GpsMap({gps}:{gps:Gps}){
 const host=useRef<HTMLDivElement>(null),mapRef=useRef<L.Map|null>(null),buoyRef=useRef<L.Marker|null>(null),lineRef=useRef<L.Polyline|null>(null),[tiles,setTiles]=useState<"loading"|"online"|"error">("loading");
 useEffect(()=>{if(!host.current||mapRef.current)return;const reference:L.LatLngExpression=[gps.referenceLatitude,gps.referenceLongitude],map=L.map(host.current,{zoomControl:true,attributionControl:true,preferCanvas:true}).setView(reference,17);mapRef.current=map;
  const layer=L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; OpenStreetMap contributors',crossOrigin:true}).on("load",()=>setTiles("online")).on("tileerror",()=>setTiles("error")).addTo(map);
  const baseIcon=L.divIcon({className:"falcon-map-icon",html:'<span class="base-pin"></span>',iconSize:[24,24],iconAnchor:[12,12]});
  L.marker(reference,{icon:baseIcon}).addTo(map).bindTooltip("Puerto Princesa demo deployment point");L.circle(reference,{radius:10,color:"#72d99d",weight:2,dashArray:"6 6",fillColor:"#72d99d",fillOpacity:.1}).addTo(map);
  const observer=new ResizeObserver(()=>map.invalidateSize());observer.observe(host.current);return()=>{observer.disconnect();layer.off();map.remove();mapRef.current=null};
 },[gps.referenceLatitude,gps.referenceLongitude]);
 useEffect(()=>{const map=mapRef.current;if(!map||!gps.valid||gps.latitude==null||gps.longitude==null)return;const point:L.LatLngExpression=[gps.latitude,gps.longitude],reference:L.LatLngExpression=[gps.referenceLatitude,gps.referenceLongitude];
  const buoyIcon=L.divIcon({className:"falcon-map-icon",html:'<span class="buoy-pin"><i></i></span>',iconSize:[34,34],iconAnchor:[17,17]});
  if(!buoyRef.current){buoyRef.current=L.marker(point,{icon:buoyIcon,zIndexOffset:500}).addTo(map).bindTooltip("FALCON-01 · live GPS",{direction:"top",offset:[0,-16]});lineRef.current=L.polyline([reference,point],{color:"#efbb70",weight:2,dashArray:"5 7"}).addTo(map);map.fitBounds(L.latLngBounds([reference,point]).pad(4),{maxZoom:18});}else{buoyRef.current.setLatLng(point);lineRef.current?.setLatLngs([reference,point]);}
 },[gps]);
 return <div className="gps-map-shell"><div className="gps-map" ref={host} aria-label="Live buoy map in Puerto Princesa, Palawan"/><span className={`tile-state is-${tiles}`}>{tiles==="online"?"MAP ONLINE":tiles==="error"?"TILES UNAVAILABLE":"LOADING MAP"}</span><div className="map-legend"><span><i className="buoy-dot"/>Live buoy</span><span><i className="base-dot"/>Deployment point</span><span><i className="zone-dot"/>10 m geofence</span></div></div>;
}
