import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { bookingAPI } from '../api/client';
import { Card, Button, LoadingSpinner } from '../components/Common';

export default function ConfirmationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { pnr } = location.state || {};

  const [reservation, setReservation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!pnr) {
      navigate('/');
      return;
    }
    fetchReservation();
  }, [pnr, navigate]);

  const fetchReservation = async () => {
    try {
      const response = await bookingAPI.getReservation(pnr);
      setReservation(response.data.reservation);
    } catch (err) {
      console.error('Failed to fetch reservation');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  if (!reservation) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto text-center">
          <p className="text-red-600">Failed to load reservation</p>
          <Button onClick={() => navigate('/')} className="mt-4">Back Home</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <p className="text-6xl mb-4">✅</p>
          <h1 className="text-4xl font-bold text-green-700 mb-2">Booking Confirmed!</h1>
          <p className="text-gray-600">Your seat has been reserved</p>
        </div>

        <Card className="max-w-2xl mx-auto">
          <div className="space-y-6">
            {/* PNR */}
            <div className="bg-secondary text-white p-4 rounded text-center">
              <p className="text-sm mb-1">Your Ticket Number</p>
              <p className="text-4xl font-bold">{reservation.pnr}</p>
              <p className="text-sm mt-2">Save this for your journey</p>
            </div>

            {/* Journey Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-gray-500 text-sm">Train</p>
                <p className="font-bold text-lg">{reservation.train.train_number}</p>
                <p className="text-gray-700">{reservation.train.name}</p>
              </div>
              <div>
                <p className="text-gray-500 text-sm">Journey Date</p>
                <p className="font-bold text-lg">{reservation.journey_date}</p>
              </div>
              <div>
                <p className="text-gray-500 text-sm">Coach</p>
                <p className="font-bold text-lg">Coach {reservation.coach.coach_number}</p>
              </div>
              <div>
                <p className="text-gray-500 text-sm">Seat</p>
                <p className="font-bold text-lg">
                  {reservation.seat?.seat_number || 'To be assigned'}
                </p>
              </div>
            </div>

            {/* Important Notes */}
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <p className="font-semibold text-yellow-800">Important Instructions</p>
              <ul className="text-sm text-yellow-700 mt-2 list-disc list-inside space-y-1">
                <li>Report 30 minutes before departure</li>
                <li>Carry valid ID proof</li>
                <li>Platform number will be announced</li>
                <li>Luggage limit: 80kg per passenger</li>
              </ul>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <Button
                onClick={() => navigate('/dashboard')}
                variant="primary"
                className="flex-1"
              >
                View Bookings
              </Button>
              <Button
                onClick={() => navigate('/')}
                variant="success"
                className="flex-1"
              >
                Book Again
              </Button>
            </div>
          </div>
        </Card>

        {/* Confirmation Email Note */}
        <div className="text-center mt-8 text-gray-600">
          <p>Confirmation email has been sent to your registered email address</p>
        </div>
      </div>
    </div>
  );
}
