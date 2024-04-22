// MapComponent.jsx
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'mapbox-gl/dist/mapbox-gl.css';

const MapComponent = () => {
    const mapRef = useRef(null);

    useEffect(() => {
        const map = L.map(mapRef.current, {
            center: [20.5937, 78.9629], // Center coordinates
            zoom: 6,
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

        const customIcon = L.icon({
            iconUrl: './marker.png', // Adjust the path as necessary
            iconSize: [25, 41], // Size of the icon
            iconAnchor: [12, 41], // Point of the icon which will correspond to marker's location
            popupAnchor: [1, -34], // Point from which the popup should open relative to the iconAnchor
        });

        const controller = new AbortController();
        const signal = controller.signal;

        const fetchData = async () => {
            try {
                const response = await fetch('./coordinates.json', { signal });
                const data = await response.json();
                data.forEach(row => {
                    const lat = row.Latitude;
                    const lon = row.Longitude;
    
                    if (lat && lon && map && mapRef.current) {
                        L.marker([lat, lon], { icon: customIcon }).addTo(map);
                    }
                });
            } catch (err) {
                if (err.name !== 'AbortError') {
                    console.error(err);
                }
            }
        };
        
        fetchData();

        return () => {
            map.remove();
        };
    }, []);

    return <div ref={mapRef} style={{ height: '100vh', width: '100%' }} />;
};

export default MapComponent;