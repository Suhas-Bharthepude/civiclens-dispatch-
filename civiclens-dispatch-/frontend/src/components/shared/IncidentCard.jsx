// frontend/src/IncidentCard.jsx
// This is a custom component that displays a single incident
// It's REUSABLE - we can show many incidents using this same component

// ========================================
// INCIDENT CARD COMPONENT
// ========================================

// Function component that accepts props
// Props is an object containing data passed from parent
function IncidentCard(props) {
  
  // We can destructure props to extract specific values
  // This is equivalent to:
  // const id = props.id;
  // const description = props.description;
  // etc.
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    // Main container div
    // className in JSX (not class, because class is a JavaScript keyword)
    <div className="incident-card">
      
      {/* Incident ID */}
      {/* {props.id} embeds JavaScript expression */}
      <h3>Incident #{props.id}</h3>
      
      {/* Source badge */}
      <p>
        <strong>Source:</strong> 
        <span className="badge">{props.source}</span>
      </p>
      
      {/* Description */}
      <p>
        <strong>Description:</strong> {props.description}
      </p>
      
      {/* Location */}
      <p>
        <strong>Location:</strong> {props.location}
      </p>
      
      {/* Severity badge - conditional CSS class */}
      <p>
        <strong>Severity:</strong>
        {/* 
          Conditional className based on severity value
          This is a JavaScript expression using template literal
        */}
        <span className={`severity-badge severity-${props.severity}`}>
          {props.severity.toUpperCase()}
        </span>
      </p>
      
    </div>
  )
}

// ========================================
// EXPORT
// ========================================

// Export so other components can import this
export default IncidentCard