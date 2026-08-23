import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { getToken } from './api.js';
import Layout from './components/Layout.jsx';
import Login from './pages/Login.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import AgentsPage from './pages/AgentsPage.jsx';
import AgentBuilderPage from './pages/AgentBuilderPage.jsx';
import CampaignsPage from './pages/CampaignsPage.jsx';
import CampaignDetailPage from './pages/CampaignDetailPage.jsx';
import CallDetailPage from './pages/CallDetailPage.jsx';
import TestCallPage from './pages/TestCallPage.jsx';

// livekit-client (~700 kB minified) is only needed on the Playground route —
// keep it out of the initial bundle.
const PlaygroundPage = lazy(() => import('./pages/PlaygroundPage.jsx'));
const DevToolsPage = lazy(() => import('./pages/DevToolsPage.jsx'));

function RouteFallback() {
  return (
    <div className="loading-page">
      <span className="spinner" /> Loading…
    </div>
  );
}

/** Redirects to /login when there is no stored JWT. */
function RequireAuth({ children }) {
  const location = useLocation();
  if (!getToken()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}

function NotFound() {
  return <div className="empty-state">Page not found.</div>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<RouteFallback />}>
        <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          element={
            <RequireAuth>
              <Layout />
            </RequireAuth>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="agents" element={<AgentsPage />} />
          {/* No key prop: navigating /agents/new -> /agents/:id/edit after
              creation must preserve the wizard's in-memory state. */}
          <Route path="agents/new" element={<AgentBuilderPage />} />
          <Route path="agents/:id/edit" element={<AgentBuilderPage />} />
          <Route path="playground" element={<PlaygroundPage />} />
          <Route path="playground/:agentVersionId" element={<PlaygroundPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="campaigns/:id" element={<CampaignDetailPage />} />
          <Route path="calls/:id" element={<CallDetailPage />} />
          <Route path="test-call" element={<TestCallPage />} />
          <Route path="dev" element={<DevToolsPage />} />
          <Route path="*" element={<NotFound />} />
        </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
