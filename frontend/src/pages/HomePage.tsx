import React from 'react';

const HomePage: React.FC = () => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Welcome to YubiKey Bitcoin Seed Storage</h2>
      <p className="mb-4">
        This application helps you securely store Bitcoin seed phrases using YubiKey&apos;s WebAuthn
        capabilities.
      </p>
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded dark:bg-yellow-900 dark:border-yellow-800 dark:text-yellow-100">
        <p className="text-yellow-800 dark:text-yellow-100">
          <strong>Note:</strong> This is a proof-of-concept application. The React frontend is under
          development.
        </p>
      </div>
      <div className="mt-6 flex space-x-4">
        <a href="/register" className="btn-primary">
          Register YubiKey
        </a>
        <a href="/authenticate" className="btn-secondary">
          Authenticate
        </a>
      </div>
    </div>
  );
};

export default HomePage;
