import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import CampaignsPage from './pages/CampaignsPage.jsx';
import CampaignDetailPage from './pages/CampaignDetailPage.jsx';
import CallDetailPage from './pages/CallDetailPage.jsx';
import TestCallPage from './pages/TestCallPage.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<CampaignsPage />} />
          <Route path="campaigns/:id" element={<CampaignDetailPage />} />
          <Route path="calls/:id" element={<CallDetailPage />} />
          <Route path="test-call" element={<TestCallPage />} />
          <Route path="*" element={<div className="empty-state">Page not found.</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
