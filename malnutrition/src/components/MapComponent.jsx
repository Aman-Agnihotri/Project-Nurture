// MapComponent.jsx
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'mapbox-gl/dist/mapbox-gl.css';

const MapComponent = () => {
 const mapRef = useRef(null);

 useEffect(() => {
    const map = L.map(mapRef.current, {
      center: [51.505, -0.09], // Example coordinates
      zoom: 13,
      layers: [
        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
          attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
          maxZoom: 18,
          id: 'mapbox/streets-v11', // Example style
          tileSize: 512,
          zoomOffset: -1,
          accessToken: 'pk.eyJ1Ijoic2FjaDgxNDEiLCJhIjoiY2x1cXQ2MGdlMDFyYTJsbzJpd2k2c2hrZCJ9.Exjb8uFz7gboyXpa4MlNVw'
        })
      ]
    });

    return () => {
      map.remove();
    };
 }, []);

 return <div ref={mapRef} style={{ height: '100vh', width: '100%' }} />;
};

export default MapComponent;