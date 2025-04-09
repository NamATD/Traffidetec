import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

// Fix for default markers
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const TrafficMap = () => {
  const [trafficData, setTrafficData] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/traffic');
        setTrafficData(response.data);
      } catch (error) {
        console.error('Error fetching traffic data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const getTrafficColor = (density) => {
    if (density < 30) return '#4CAF50';
    if (density < 60) return '#FFC107';
    return '#F44336';
  };

  const handleMarkerClick = (point) => {
    setSelectedVideo(point.video_path);
  };

  return (
    <div className="map-container">
      <MapContainer
        center={[10.8035, 106.6963]}
        zoom={14}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {trafficData.map((point) => (
          <Marker
            key={point.name}
            position={[point.lat, point.lng]}
            icon={L.divIcon({
              className: 'custom-icon',
              html: `<div style="
                background-color: ${getTrafficColor(point.density)};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 0 4px rgba(0,0,0,0.3);
              "></div>`,
            })}
            eventHandlers={{
              click: () => handleMarkerClick(point)
            }}
          >
            <Popup>
              <div className="popup-content">
                <h3>{point.name}</h3>
                <p className="address">{point.address}</p>
                <p>Mật độ: {point.density}%</p>
                <p>Tình trạng: {point.status}</p>
                <p>Số phương tiện: {point.vehicle_count}</p>
                <p className="timestamp">
                  Cập nhật: {new Date(point.timestamp).toLocaleString()}
                </p>
                <div className="video-container">
                  <img
                    src={`http://localhost:5000/video_feed/${point.video_path.split('/').pop()}`}
                    alt="Traffic Detection"
                    className="traffic-video"
                  />
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default TrafficMap;