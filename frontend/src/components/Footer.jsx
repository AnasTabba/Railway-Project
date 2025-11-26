import React from 'react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-white py-8 mt-12">
      <div className="container mx-auto px-4 text-center">
        <p>&copy; {currentYear} Railway Management System. All rights reserved.</p>
        <p className="text-sm text-gray-400 mt-2">
          Built with React, Flask, and PostgreSQL
        </p>
      </div>
    </footer>
  );
}
