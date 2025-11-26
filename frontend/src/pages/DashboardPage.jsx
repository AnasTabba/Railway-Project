import React, { useState, useEffect } from 'react';
import { bookingAPI } from '../api/client';
import { Card, Button, LoadingSpinner, ErrorAlert } from '../components/Common';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchReservations();
  }, [isAuthenticated, navigate]);

  const fetchReservations = async () => {
    try {
      const response = await bookingAPI.getUserReservations();
      setReservations(response.data.reservations);
    } catch (err) {
      setError('Failed to load reservations');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelReservation = async (pnr) => {
    if (!window.confirm('Are you sure you want to cancel this reservation?')) return;

    try {
      await bookingAPI.cancelReservation(pnr);
      setReservations(prev => prev.map(r =>
        r.pnr === pnr ? { ...r, status: 'CANCELLED' } : r
      ));
    } catch (err) {
      setError(err.response?.data?.error || 'Cancellation failed');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome, {user?.name}!</h1>
          <p className="text-gray-600">Manage your train bookings</p>
        </div>

        {error && <ErrorAlert message={error} />}

        {reservations.length === 0 ? (
          <Card className="text-center">
            <p className="text-gray-600 mb-4">No bookings yet</p>
            <Button onClick={() => navigate('/')}>Search Trains</Button>
          </Card>
        ) : (
          <div className="space-y-6">
            {reservations.map(reservation => (
              <Card key={reservation.reservation_id}>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-start">
                  {/* PNR */}
                  <div>
                    <p className="text-sm text-gray-500">PNR</p>
                    <p className="font-bold text-lg text-secondary">{reservation.pnr}</p>
                  </div>

                  {/* Train Details */}
                  <div>
                    <p className="text-sm text-gray-500">Train</p>
                    <p className="font-bold">{reservation.train.train_number}</p>
                    <p className="text-sm">{reservation.train.name}</p>
                  </div>

                  {/* Journey */}
                  <div>
                    <p className="text-sm text-gray-500">Journey</p>
                    <p className="font-bold">{reservation.journey_date}</p>
                    <p className="text-sm">Coach {reservation.coach.coach_number}</p>
                  </div>

                  {/* Status */}
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <div className={`inline-block px-3 py-1 rounded text-white text-sm font-semibold
                      ${reservation.status === 'BOOKED' ? 'bg-green-500' : ''}
                      ${reservation.status === 'HOLD' ? 'bg-yellow-500' : ''}
                      ${reservation.status === 'CANCELLED' ? 'bg-red-500' : ''}
                    `}>
                      {reservation.status}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="space-y-2">
                    {reservation.status === 'HOLD' && (
                      <p className="text-xs text-orange-600">
                        Expires: {new Date(reservation.hold_expires_at).toLocaleString()}
                      </p>
                    )}
                    {reservation.status !== 'CANCELLED' && (
                      <Button
                        onClick={() => handleCancelReservation(reservation.pnr)}
                        variant="danger"
                        className="w-full text-sm"
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        <div className="mt-8 text-center">
          <Button onClick={() => navigate('/')} variant="primary">
            Search More Trains
          </Button>
        </div>
      </div>
    </div>
  );
}
