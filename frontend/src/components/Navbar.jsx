import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-primary text-white shadow-lg">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-3 group">
          <img 
            src="/assets/logo.svg" 
            alt="Safar Logo" 
            className="h-12 w-12 transition-transform group-hover:scale-110"
          />
          <div>
            <span className="text-3xl font-bold text-secondary tracking-wide">Safar</span>
            <p className="text-xs text-gray-300 italic" style={{fontFamily: 'Noto Nastaliq Urdu, serif'}}>یادوں کا سفر</p>
          </div>
        </Link>

        <div className="flex items-center gap-6">
          {isAuthenticated ? (
            <>
              <span className="text-sm">Hello, {user?.name}</span>
              <Link to="/dashboard" className="hover:text-secondary transition">
                Dashboard
              </Link>
              {user?.role === 'ADMIN' && (
                <Link to="/admin" className="hover:text-secondary transition">
                  Admin
                </Link>
              )}
              <button
                onClick={handleLogout}
                className="bg-red-600 px-4 py-2 rounded hover:bg-red-700 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-secondary transition">
                Login
              </Link>
              <Link to="/register" className="hover:text-secondary transition">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
