// React 18 doesn't require React import for JSX, but we need it for type definitions
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layouts/MainLayout';
import HomePage from './pages/HomePage';

// Import other pages when they're created
// import RegistrationPage from './pages/RegistrationPage';
// import AuthenticationPage from './pages/AuthenticationPage';
// import SeedManagementPage from './pages/SeedManagementPage';

const App: React.FC = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* Add other routes when components are created */}
          {/* <Route path="/register" element={<RegistrationPage />} /> */}
          {/* <Route path="/authenticate" element={<AuthenticationPage />} /> */}
          {/* <Route path="/manage" element={<SeedManagementPage />} /> */}
        </Routes>
      </MainLayout>
    </Router>
  );
};

export default App;
