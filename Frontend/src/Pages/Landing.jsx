import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import demo_video from '../assets/Demo.mp4'; 

export default function LandingPage() {
  const [isLoading, setIsLoading] = useState(true);  
  const navigate = useNavigate();

  
  const handleEnter = () => {
    navigate('/traffic');  
  };

  
  const handleVideoLoad = () => {
    setIsLoading(false);  
  };

  return (
    <div className="w-full bg-gray-900">
      {/* Hero Section */}
      <div className="relative flex flex-col md:flex-row h-screen w-full">
        {/* Left Side */}
        <div className="w-full md:w-1/2 flex flex-col justify-center px-6 md:px-12 space-y-6 relative">
          <div className="text-4xl md:text-6xl font-bold text-red-500 font-winky">
            AI BASED TRAFFIC MANAGEMENT SYSTEM
          </div>

          <p className="text-lg md:text-[20px] max-w-xl leading-relaxed text-white font-semibold">
            Our system leverages AI-powered object detection to monitor and optimize real-time traffic flow using computer vision.
          </p>

          <div className="mt-4">
            <h3 className="text-xl font-bold mb-2 text-red-600">How It Works</h3>
            <ul className="list-disc ml-5 space-y-1 text-white">
              <li>Upload videos showing 4 lanes at an intersection.</li>
              <li>AI model analyzes traffic congestion using computer vision.</li>
              <li>Gives higher priority to lanes with emergency vehicles.</li>
              <li>Suggests optimized green signal durations for all directions.</li>
            </ul>
          </div>

          <div className="flex justify-center my-5">
            <button
              onClick={handleEnter}
              className="px-8 py-4 bg-red-500 hover:bg-red-600 cursor-pointer text-lg font-bold text-white rounded-xl transition duration-300 shadow-lg"
            >
              Enter System
            </button>
          </div>
        </div>

        {/* Right Side */}
        <div className="w-full md:w-1/2 relative">
          {isLoading && (
            <div className="absolute inset-0 flex justify-center items-center bg-gray-200 bg-opacity-50">
              <div className="border-t-4 border-red-500 border-solid w-16 h-16 rounded-full animate-spin"></div>
            </div>
          )}
          <video
            className="w-full h-full object-cover"
            autoPlay
            loop
            muted
            playsInline
            onLoadedData={handleVideoLoad} 
          >
            <source src={demo_video} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      </div>
    </div>
  );
}
