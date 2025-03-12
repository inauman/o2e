import React from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-primary-500 py-4 shadow-md">
        <div className="container mx-auto px-4">
          <h1 className="text-2xl font-bold text-white">YubiKey Bitcoin Seed Storage</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">{children}</main>

      <footer className="bg-gray-800 text-white py-6">
        <div className="container mx-auto px-4 text-center">
          <p>YubiKey Bitcoin Seed Storage - A proof-of-concept application</p>
          <p className="text-sm mt-2">
            © {new Date().getFullYear()} YubiKey Bitcoin Seed Storage Team
          </p>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
