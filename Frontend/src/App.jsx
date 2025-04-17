import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from './Pages/Landing'
import Traffic from './Pages/Traffic'

const App = () => {
  return (
  <>
  <Routes>
    <Route path="/" element={<Landing />} />
    <Route path="/traffic" element={<Traffic />} />
  </Routes>
  </>
  )
}

export default App
