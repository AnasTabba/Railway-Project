import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchAPI, stationAPI } from '../api/client';
import { Card, Button, LoadingSpinner, ErrorAlert } from '../components/Common';

export default function SearchPage() {
  const navigate = useNavigate();
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    source: '',
    destination: '',
    date: new Date().toISOString().split('T')[0],
    depart_after: '',
    depart_before: '',
    className: '',
    max_price: '',
    sort_by: 'fare',
  });

  useEffect(() => {
    fetchStations();
  }, []);

  const fetchStations = async () => {
    try {
      const response = await stationAPI.getAll();
      setStations(response.data);
    } catch (err) {
      setError('Failed to load stations');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const getActiveFilters = () => {
    const filters = [];
    if (formData.depart_after) filters.push({ key: 'depart_after', label: `After ${formData.depart_after}` });
    if (formData.depart_before) filters.push({ key: 'depart_before', label: `Before ${formData.depart_before}` });
    if (formData.className) filters.push({ key: 'className', label: formData.className });
    if (formData.max_price) filters.push({ key: 'max_price', label: `≤ PKR ${formData.max_price}` });
    if (formData.sort_by !== 'fare') filters.push({ key: 'sort_by', label: `Sort: ${formData.sort_by}` });
    return filters;
  };

  const removeFilter = (key) => {
    setFormData(prev => ({
      ...prev,
      [key]: key === 'sort_by' ? 'fare' : '',
    }));
  };

  const clearAllFilters = () => {
    setFormData(prev => ({
      ...prev,
      depart_after: '',
      depart_before: '',
      className: '',
      max_price: '',
      sort_by: 'fare',
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.source || !formData.destination || !formData.date) {
      setError('Please fill all fields');
      return;
    }

    if (formData.source === formData.destination) {
      setError('Source and destination must be different');
      return;
    }

    setLoading(true);
    try {
      const { source, destination, date, depart_after, depart_before, className, max_price, sort_by } = formData;
      const response = await searchAPI.searchTrains(source, destination, date, {
        depart_after,
        depart_before,
        className,
        max_price,
        sort_by,
      });
      navigate('/results', {
        state: {
          results: response.data.results,
          searchParams: formData,
        },
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-primary mb-4">🚂 Find Your Train</h1>
          <p className="text-gray-600">Search and book trains across Pakistan</p>
        </div>

        <Card className="max-w-2xl mx-auto">
          {error && <ErrorAlert message={error} />}

          <form onSubmit={handleSearch} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Source Station */}
              <div>
                <label className="block text-sm font-semibold mb-2">From</label>
                <select
                  name="source"
                  value={formData.source}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                >
                  <option value="">Select source</option>
                  {stations.map(station => (
                    <option key={station.station_id} value={station.code}>
                      {station.name} ({station.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Destination Station */}
              <div>
                <label className="block text-sm font-semibold mb-2">To</label>
                <select
                  name="destination"
                  value={formData.destination}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                >
                  <option value="">Select destination</option>
                  {stations.map(station => (
                    <option key={station.station_id} value={station.code}>
                      {station.name} ({station.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Journey Date */}
              <div>
                <label className="block text-sm font-semibold mb-2">Date</label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Depart After</label>
                <input
                  type="time"
                  name="depart_after"
                  value={formData.depart_after}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Depart Before</label>
                <input
                  type="time"
                  name="depart_before"
                  value={formData.depart_before}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Class</label>
                <select
                  name="className"
                  value={formData.className}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                >
                  <option value="">Any</option>
                  <option value="ECONOMY">ECONOMY</option>
                  <option value="AC STANDARD">AC STANDARD</option>
                  <option value="AC SLEEPER">AC SLEEPER</option>
                  <option value="AC BUSINESS">AC BUSINESS</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Max Price (PKR)</label>
                <input
                  type="number"
                  name="max_price"
                  value={formData.max_price}
                  onChange={handleChange}
                  placeholder="e.g. 1500"
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Sort By</label>
                <select
                  name="sort_by"
                  value={formData.sort_by}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-secondary"
                >
                  <option value="fare">Lowest Fare</option>
                  <option value="duration">Shortest Duration</option>
                  <option value="departure">Earliest Departure</option>
                </select>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full py-3 text-lg"
            >
              {loading ? 'Searching...' : 'Search Trains'}
            </Button>

            {/* Active Filters Chips */}
            {getActiveFilters().length > 0 && (
              <div className="flex flex-wrap gap-2 items-center pt-4 border-t">
                <span className="text-sm text-gray-600 font-semibold">Active filters:</span>
                {getActiveFilters().map(filter => (
                  <button
                    key={filter.key}
                    type="button"
                    onClick={() => removeFilter(filter.key)}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-secondary text-white text-sm rounded-full hover:bg-secondary/80 transition"
                  >
                    {filter.label}
                    <span className="font-bold">×</span>
                  </button>
                ))}
                <button
                  type="button"
                  onClick={clearAllFilters}
                  className="text-sm text-gray-600 hover:text-gray-800 underline"
                >
                  Clear all
                </button>
              </div>
            )}
          </form>
        </Card>

        {/* Popular Routes */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-center mb-8">Popular Routes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { from: 'Karachi', to: 'Lahore', code: 'KHI-LHE' },
              { from: 'Islamabad', to: 'Karachi', code: 'ISB-KHI' },
              { from: 'Peshawar', to: 'Islamabad', code: 'PEW-ISB' },
            ].map(route => (
              <Card key={route.code} className="text-center cursor-pointer hover:shadow-lg transition">
                <p className="text-xl font-semibold mb-2">{route.from} → {route.to}</p>
                <p className="text-gray-500 text-sm">{route.code}</p>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
