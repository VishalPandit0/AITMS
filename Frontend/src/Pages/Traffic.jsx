import { useState } from 'react'
import axios from 'axios'
import backgroundImage from '../assets/Traffic2.jpg';

export default function TrafficPage() {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (selectedFiles.length !== 4) {
      alert('Please upload exactly 4 videos.')
      return
    }

    const formData = new FormData()
    selectedFiles.forEach((file) => formData.append('videos', file))

    try {
      setLoading(true)
      setResult(null) // clear previous result
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(response.data)
      setSelectedFiles([])
      e.target.reset()
    } catch (error) {
      console.error('Error uploading files:', error)
      setResult({ error: 'Upload failed. Please try again later.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-gray-100">
      <div
        className="absolute inset-0 bg-cover bg-center blur-sm z-0"
        style={{ backgroundImage: `url(${backgroundImage})` }}
      />
      <div className="relative z-10 p-6">
        <div className="flex flex-col md:flex-row gap-6 max-w-6xl mx-auto">

          {/* Left Panel */}
          <div className="md:w-1/2 bg-gray-900 bg-opacity-90 p-6 shadow space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-white mb-2">
                🚦 Optimize Traffic Flow with AI
              </h2>
              <p className="text-white">
                Upload traffic videos from a 4-lane intersection. The system analyzes congestion and recommends green signal durations.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-white mb-2">
                🎬 Download Sample Video Set
              </h3>
              <p className="text-white mb-4">
                Need test videos? Download this zip containing all 4 sample lanes.
              </p>
              <a
                href="./Sample_videos.zip"
                download
                className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 font-semibold transition"
              >
                Download Sample Videos (ZIP)
              </a>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-white mb-2">
                📹 Upload 4 Traffic Videos
              </h3>
              <form onSubmit={handleSubmit} className="space-y-4">
                <input
                  type="file"
                  multiple
                  accept="video/*"
                  onChange={handleFileChange}
                  className="block w-full border px-3 py-2 text-white"
                />
                <button
                  type="submit"
                  className="w-full bg-red-500 text-white py-2 cursor-pointer font-semibold hover:bg-red-600 transition"
                >
                  Run Model
                </button>
              </form>
            </section>
          </div>

          {/* Right Panel */}
          <div className={`md:w-1/2 p-6 shadow min-h-[300px] flex justify-center items-center ${loading ? 'bg-black' : 'bg-white bg-opacity-90'}`}>
            {loading && (
              <div className="flex space-x-6">
                <div className="w-12 h-12 rounded-full bg-red-900 animate-red-glow" />
                <div className="w-12 h-12 rounded-full bg-yellow-900 animate-yellow-glow" />
                <div className="w-12 h-12 rounded-full bg-green-900 animate-green-glow" />
                <style>
                  {`
                    @keyframes redGlow {
                      0%, 33.33%, 100% { background-color: #7f1d1d; }
                      16.66% { background-color: #ef4444; }
                    }
                    @keyframes yellowGlow {
                      0%, 33.33%, 100% { background-color: #78350f; }
                      49.99% { background-color: #facc15; }
                    }
                    @keyframes greenGlow {
                      0%, 66.66%, 100% { background-color: #064e3b; }
                      83.33% { background-color: #22c55e; }
                    }
                    .animate-red-glow {
                      animation: redGlow 3s infinite;
                    }
                    .animate-yellow-glow {
                      animation: yellowGlow 3s infinite;
                    }
                    .animate-green-glow {
                      animation: greenGlow 3s infinite;
                    }
                  `}
                </style>
              </div>
            )}

            {!loading && !result && (
              <p className="text-gray-500 text-center">
                Optimization results will appear here.
                <br />
                <span className="text-2xl">🚦🚦🚦🚦</span>
              </p>
            )}

            {!loading && result?.error && (
              <div className="text-red-600 font-semibold text-center">
                <h3>Error:</h3>
                <p>{result.error}</p>
              </div>
            )}

            {!loading && result && !result.error && (
              <div className="text-gray-700">
                <h2 className="text-xl font-bold text-green-600 mb-2 text-center">
                  ✅ Optimization Results
                </h2>
                <ul className="list-disc pl-6 space-y-2">
                  {['lane1', 'lane2', 'lane3', 'lane4']
                    .sort((a, b) => result.priority[a] - result.priority[b])
                    .map((lane) => {
                      const laneData = result.traffic_data.find(d => d.direction === lane);
                      const hasAmbulance = laneData?.ambulance_detected;

                      return (
                        <li key={lane}>
                          🚦 {lane.charAt(0).toUpperCase() + lane.slice(1)}:
                          <strong> {result.optimized_times[lane]}s</strong> |
                          Priority: <span className="text-blue-600 font-medium">{result.priority[lane]}</span> |
                          Emergency: <span className={hasAmbulance ? "text-red-600 font-medium" : "text-gray-600"}>
                            {hasAmbulance ? "Detected" : "None"}
                          </span>
                        </li>
                      );
                    })}
                </ul>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
