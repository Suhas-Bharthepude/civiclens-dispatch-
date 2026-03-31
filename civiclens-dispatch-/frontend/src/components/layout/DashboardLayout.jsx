// frontend/src/components/layout/DashboardLayout.jsx
// Two-column layout wrapper for the dispatcher dashboard.
//
// App.jsx passes TWO children inside this component:
//   <DashboardLayout>
//     <IncidentsList />   ← children[0] → left column
//     <IncidentDetail />  ← children[1] → right column
//   </DashboardLayout>
//
// We destructure children[0] and children[1] to place them
// in their respective columns.

import React from 'react'
import './DashboardLayout.css'

// children is an array when more than one child is passed
const DashboardLayout = ({ children }) => {
  // children[0] = IncidentsList (left column)
  // children[1] = IncidentDetail (right column)
  return (
    <div className="dashboard-layout">
      {/* Left column — takes up more space (the incidents table) */}
      <div className="dashboard-left">
        {children[0]}
      </div>
      {/* Right column — detail panel */}
      <div className="dashboard-right">
        {children[1]}
      </div>
    </div>
  )
}

export default DashboardLayout