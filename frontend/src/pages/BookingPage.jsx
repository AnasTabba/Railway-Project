import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { bookingAPI } from '../api/client';
import { Card, Button, ErrorAlert, SuccessAlert } from '../components/Common';
import { useAuth } from '../context/AuthContext';

export default function BookingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const { train, searchParams, availableSeats, fares, classes } = location.state || {};

  const [step, setStep] = useState(1); // 1: Select Class, 2: Passenger Details, 3: Confirm
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedClass, setSelectedClass] = useState('');
  const [formData, setFormData] = useState({
    passenger_name: '',
    passenger_age: '',
    passenger_email: user?.email || '',
  });
  const [pnr, setPnr] = useState('');

  if (!train || !classes) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto text-center">
          <p className="text-gray-600">Invalid booking session. Redirecting...</p>
          <Button onClick={() => navigate('/')} className="mt-4">Back to Search</Button>
        </div>
      </div>
    );
  }

  // Build class options from classes array
  const classOptions = classes.reduce((acc, cls) => {
    acc[cls.class_name] = {
      class_id: cls.class_id,
      seats_available: cls.seats_available,
      fare: cls.fare
    };
    return acc;
  }, {});

  const handleClassSelect = (className) => {
    setSelectedClass(className);
    setError('');
    setStep(2);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (!formData.passenger_name.trim()) {
      setError('Passenger name required');
      return false;
    }
    if (!formData.passenger_age || formData.passenger_age < 1 || formData.passenger_age > 120) {
      setError('Valid age required');
      return false;
    }
    return true;
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      const response = await bookingAPI.createReservation({
        train_id: train.train_id,
        journey_date: searchParams.date,
        class_id: classOptions[selectedClass].class_id,
        passenger_name: formData.passenger_name,
        passenger_age: parseInt(formData.passenger_age),
        passenger_email: formData.passenger_email,
      });

      setPnr(response.data.reservation.pnr);
      setSuccess('Reservation created! Proceed to payment.');
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.error || 'Booking failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    setLoading(true);
    try {
      // Find reservation by PNR to get reservation_id
      const reservation = await bookingAPI.getReservation(pnr);
      await bookingAPI.processPayment(reservation.data.reservation.reservation_id, {
        method: 'CREDIT_CARD'
      });
      navigate('/confirmation', { state: { pnr } });
    } catch (err) {
      setError(err.response?.data?.error || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Booking</h1>

        {/* Step Indicator */}
        <div className="flex justify-between mb-8 max-w-2xl">
          {[1, 2, 3].map(s => (
            <div
              key={s}
              className={`flex-1 text-center ${
                s === step ? 'text-secondary font-bold' : 'text-gray-500'
              }`}
            >
              Step {s}
            </div>
          ))}
        </div>

        <Card className="max-w-2xl mx-auto">
          {error && <ErrorAlert message={error} />}
          {success && <SuccessAlert message={success} />}

          {/* Step 1: Select Class */}
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Select Class</h2>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(classOptions).map(([className, classInfo]) => (
                  <button
                    key={className}
                    onClick={() => handleClassSelect(className)}
                    disabled={classInfo.seats_available === 0}
                    className="p-4 border-2 rounded hover:border-secondary disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    <p className="font-bold">{className}</p>
                    <p className="text-sm">PKR {classInfo.fare}</p>
                    <p className="text-sm text-gray-500">{classInfo.seats_available} seats</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Passenger Details */}
          {step === 2 && (
            <form onSubmit={handleBooking} className="space-y-4">
              <h2 className="text-2xl font-bold mb-6">Passenger Details</h2>

              <div>
                <label className="block text-sm font-semibold mb-2">Name</label>
                <input
                  type="text"
                  name="passenger_name"
                  value={formData.passenger_name}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="Full name"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Age</label>
                <input
                  type="number"
                  name="passenger_age"
                  value={formData.passenger_age}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="Age"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Email</label>
                <input
                  type="email"
                  name="passenger_email"
                  value={formData.passenger_email}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="Email"
                />
              </div>

              <div className="flex gap-4">
                <Button onClick={() => setStep(1)} variant="primary">
                  Back
                </Button>
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? 'Confirming...' : 'Continue to Payment'}
                </Button>
              </div>
            </form>
          )}

          {/* Step 3: Payment */}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Payment</h2>
              <div className="bg-blue-50 p-4 rounded mb-6">
                <p className="text-sm text-gray-600">PNR: {pnr}</p>
                <p className="font-bold text-lg">Amount: PKR {classOptions[selectedClass].fare}</p>
              </div>
              <Button
                onClick={handlePayment}
                disabled={loading}
                variant="success"
                className="w-full py-3"
              >
                {loading ? 'Processing...' : 'Confirm Payment'}
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
