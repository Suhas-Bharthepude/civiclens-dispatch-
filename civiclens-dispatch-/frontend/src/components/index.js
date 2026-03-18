// frontend/src/components/index.js
// Barrel export file - exports all components from one place
// This allows importing multiple components in one line
//
// Without this file:
//   import HealthCheck from './components/HealthCheck'
//   import IncidentsList from './components/IncidentsList'
//   import IncidentDetail from './components/IncidentDetail'
//
// With this file:
//   import { HealthCheck, IncidentsList, IncidentDetail } from './components'
//
// Much cleaner!

// Export all components
// Each component is exported by name (named export)
export { default as DashboardLayout } from './DashboardLayout'
export { default as HealthCheck } from './HealthCheck'
export { default as IncidentCard } from './IncidentCard'
export { default as IncidentDetail } from './IncidentDetail'
export { default as IncidentsList } from './IncidentsList'
export { default as IncidentTable } from './IncidentTable'
export { default as LoadingState } from './LoadingState'
export { default as SectionDivider } from './SectionDivider'
export { default as SubmitIncidentForm } from './SubmitIncidentForm'
export { default as Toast } from './Toast'
export { default as ToastContainer } from './ToastContainer'

// Note: We're re-exporting default exports as named exports
// This allows destructured imports: import { ComponentName } from './components'