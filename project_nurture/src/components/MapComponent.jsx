// MapComponent.jsx
import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'mapbox-gl/dist/mapbox-gl.css';
// eslint-disable-next-line no-unused-vars
import { MarkerClusterGroup } from 'react-leaflet-cluster'
import 'leaflet.heat';

const MapComponent = () => {
    const mapRef = useRef(null);

    useEffect(() => {
        const markers = new L.MarkerClusterGroup();

        const map = L.map(mapRef.current, {
            center: [20.5937, 78.9629], // Center coordinates
            zoom: 6
        });

        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: 'mapbox/streets-v11', // Example style
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1Ijoic2FjaDgxNDEiLCJhIjoiY2x1cXQ2MGdlMDFyYTJsbzJpd2k2c2hrZCJ9.Exjb8uFz7gboyXpa4MlNVw'
        }).addTo(map);

        const customIcon = L.icon({
            iconUrl: './marker.png',
            iconSize: [25, 41], // Size of the icon
            iconAnchor: [12, 41], // Point of the icon which will correspond to marker's location
            popupAnchor: [1, -34], // Point from which the popup should open relative to the iconAnchor
        });

        const heat = L.heatLayer([], { radius: 25 });

        const fetchData = async () => {
            try {
                const response = await fetch('./coordinates.json');
                const data = await response.json();
                // let i=0;
                data.forEach(row => {
                    // i++;
                    const lat = row.Latitude;
                    const lon = row.Longitude;
                    const scale = row.Scale;

                    if (lat && lon && map && mapRef.current) {
                        // console.log("Adding the marker!",i);
                        heat.addLatLng([lat, lon, scale]);
                        markers.addLayer(L.marker([lat, lon], { icon: customIcon }));
                        // console.log("Marker added!");
                    }
                });
                heat.addTo(map);
                map.addLayer(markers);
            } catch (err) {
                console.error(err);
            }
        };
        
        fetchData();

        return () => {
            map.remove();
        };
    }, []);

    return (
        <>
            <style>
                {`
                    .map-container {
                        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                        transition: 0.3s;
                        border-radius: 15px; /* Add rounded corners */
                        overflow: hidden; /* Ensure the map follows the rounded corners */
                    }
                `}
            </style>
            <div ref={mapRef} className="map-container" style={{ height: '100vh', width: '100%' }} >
            </div>
        </>
    );
};

export default MapComponent;