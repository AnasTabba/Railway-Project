import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, Button } from '../components/Common';

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { results = [], searchParams = {} } = location.state || {};

  if (!results || results.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-2xl font-bold mb-4">No Trains Found</h1>
          <p className="text-gray-600 mb-6">Try searching with different criteria</p>
          <Button onClick={() => navigate('/')}>Back to Search</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Search Results</h1>
          <div className="text-gray-600 space-y-1">
            <p>{searchParams.source} → {searchParams.destination} on {searchParams.date}</p>
            {(searchParams.depart_after || searchParams.depart_before || searchParams.className || searchParams.max_price || searchParams.sort_by) && (
              <p className="text-sm">
                Filters:
                {searchParams.depart_after && ` after ${searchParams.depart_after}`}
                {searchParams.depart_before && ` before ${searchParams.depart_before}`}
                {searchParams.className && ` class ${searchParams.className}`}
                {searchParams.max_price && ` ≤ PKR ${searchParams.max_price}`}
                {searchParams.sort_by && `, sorted by ${searchParams.sort_by}`}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-6">
          {results.map((result, idx) => (
            <Card key={idx} className="hover:shadow-lg transition">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Train Details */}
                <div>
                  <p className="text-sm text-gray-500">Train</p>
                  <p className="font-bold text-lg">{result.train.train_number}</p>
                  <p className="text-gray-700">{result.train.name}</p>
                </div>

                {/* Time */}
                <div>
                  <p className="text-sm text-gray-500">Times</p>
                  <p className="font-bold text-secondary">
                    {result.departure_time_local} → {result.arrival_time_local}
                  </p>
                  <p className="text-sm text-gray-600">
                    Duration: {result.duration_hours.toFixed(1)}h
                  </p>
                </div>

                {/* Availability */}
                <div>
                  <p className="text-sm text-gray-500">Available Seats</p>
                  <div className="space-y-1">
                    {Object.entries(result.available_seats).map(([cls, seats]) => (
                      <p key={cls} className="text-sm">
                        {cls}: <span className="font-semibold text-secondary">{seats}</span>
                      </p>
                    ))}
                  </div>
                </div>

                {/* Fares */}
                <div>
                  <p className="text-sm text-gray-500">Fares (PKR)</p>
                  <div className="space-y-1">
                    {Object.entries(result.fares).map(([cls, fare]) => (
                      <p key={cls} className="text-sm">
                        {cls}: <span className="font-semibold">PKR {fare}</span>
                      </p>
                    ))}
                  </div>
                  <Button
                    onClick={() => navigate('/booking', {
                      state: {
                        train: result.train,
                        searchParams,
                        availableSeats: result.available_seats,
                        fares: result.fares,
                        classes: result.classes,
                      },
                    })}
                    variant="success"
                    className="mt-3 w-full"
                  >
                    Book Now
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="mt-8 text-center">
          <Button onClick={() => navigate('/')}>New Search</Button>
        </div>
      </div>
    </div>
  );
}
