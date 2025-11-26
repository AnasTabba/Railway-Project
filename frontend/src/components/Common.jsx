import React from 'react';

export const LoadingSpinner = () => (
  <div className="flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-secondary"></div>
  </div>
);

export const ErrorAlert = ({ message }) => (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
    ⚠️ {message}
  </div>
);

export const SuccessAlert = ({ message }) => (
  <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
    ✓ {message}
  </div>
);

export const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
    {children}
  </div>
);

export const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'primary',
  className = ''
}) => {
  const baseClass = 'px-4 py-2 rounded font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-secondary text-white hover:bg-blue-600',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    success: 'bg-accent text-white hover:bg-green-600',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClass} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export default {
  LoadingSpinner,
  ErrorAlert,
  SuccessAlert,
  Card,
  Button,
};
