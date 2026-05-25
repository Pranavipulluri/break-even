import { Clock, Globe, MapPin, Navigation, Phone, Search, Star, Users } from 'lucide-react';
import { useEffect, useState } from 'react';

const Discover = () => {
  // Simple fallback translate function
  const translate = (text) => text;
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'map'
  const [businesses, setBusinesses] = useState([]);
  const [featuredBusinesses, setFeaturedBusinesses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});

  const defaultCategories = [
    { value: 'all', label: 'All Categories', icon: '🏪' },
    { value: 'beauty', label: 'Beauty & Wellness', icon: '💄' },
    { value: 'legal', label: 'Legal Services', icon: '⚖️' },
    { value: 'restaurant', label: 'Food & Dining', icon: '🍽️' },
    { value: 'fitness', label: 'Fitness & Sports', icon: '💪' },
    { value: 'services', label: 'Professional Services', icon: '💼' },
    { value: 'healthcare', label: 'Healthcare', icon: '🏥' }
  ];

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Load businesses when search/filter changes
  useEffect(() => {
    loadBusinesses();
  }, [searchTerm, selectedCategory]);

  const loadInitialData = async () => {
    try {
      // Load categories, featured businesses, and stats in parallel
      const [categoriesRes, featuredRes, statsRes] = await Promise.all([
        fetch('/api/public/discover/categories'),
        fetch('/api/public/discover/featured'),
        fetch('/api/public/discover/stats')
      ]);

      if (categoriesRes.ok) {
        const categoriesData = await categoriesRes.json();
        if (categoriesData.success) {
          setCategories([defaultCategories[0], ...categoriesData.categories]);
        }
      }

      if (featuredRes.ok) {
        const featuredData = await featuredRes.json();
        if (featuredData.success) {
          setFeaturedBusinesses(featuredData.businesses);
        }
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        if (statsData.success) {
          setStats(statsData.stats);
        }
      }

      // Load initial businesses
      await loadBusinesses();
    } catch (error) {
      console.error('Error loading initial data:', error);
      // Fallback to default categories
      setCategories(defaultCategories);
    } finally {
      setLoading(false);
    }
  };

  const loadBusinesses = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      params.append('limit', '20');

      const response = await fetch(`/api/public/discover/businesses?${params}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setBusinesses(data.businesses);
        }
      }
    } catch (error) {
      console.error('Error loading businesses:', error);
    }
  };

  // If backend is not available, use mock data
  const mockBusinesses = [
    {
      id: 1,
      name: 'Glamour Beauty Salon',
      category: 'beauty',
      description: 'Professional beauty treatments and styling services',
      rating: 4.8,
      reviews: 124,
      location: 'Hyderabad, Telangana',
      distance: '0.8 km',
      phone: '+91 98765 43210',
      website: 'glamour-salon.break-even.app',
      image: 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400&h=300&fit=crop',
      tags: ['Hair Styling', 'Facial', 'Makeup'],
      openTime: '9:00 AM - 8:00 PM',
      featured: true
    },
    {
      id: 2,
      name: 'TechLaw Associates',
      category: 'legal',
      description: 'Expert legal consultation for technology and business matters',
      rating: 4.9,
      reviews: 89,
      location: 'Bangalore, Karnataka',
      distance: '1.2 km',
      phone: '+91 98765 43211',
      website: 'techlaw.break-even.app',
      image: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=300&fit=crop',
      tags: ['Corporate Law', 'Tech Consulting', 'Contracts'],
      openTime: '10:00 AM - 6:00 PM',
      featured: false
    },
    {
      id: 3,
      name: 'Fresh Bites Restaurant',
      category: 'restaurant',
      description: 'Authentic local cuisine with modern twist',
      rating: 4.6,
      reviews: 256,
      location: 'Mumbai, Maharashtra',
      distance: '2.1 km',
      phone: '+91 98765 43212',
      website: 'freshbites.break-even.app',
      image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop',
      tags: ['Vegetarian', 'Family Dining', 'Takeaway'],
      openTime: '11:00 AM - 11:00 PM',
      featured: true
    }
  ];

  // Use mock data if no real businesses loaded
  const displayBusinesses = businesses.length > 0 ? businesses : mockBusinesses;
  const displayFeatured = featuredBusinesses.length > 0 ? featuredBusinesses : mockBusinesses.filter(b => b.featured);
  const displayCategories = categories.length > 1 ? categories : defaultCategories;

  const filteredBusinesses = displayBusinesses.filter(business => {
    const matchesSearch = business.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         business.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (business.tags || []).some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || business.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">B</span>
                </div>
                <h1 className="text-xl font-bold text-gradient font-display">Break-even</h1>
              </div>
              <div className="hidden md:block h-6 w-px bg-gray-300"></div>
              <h2 className="text-lg font-semibold text-gray-700 hidden md:block">{translate('Discover Businesses')}</h2>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setViewMode(viewMode === 'grid' ? 'map' : 'grid')}
                className="btn-ghost text-sm"
              >
                {viewMode === 'grid' ? (
                  <>
                    <MapPin size={16} className="mr-2" />
                    {translate('Map View')}
                  </>
                ) : (
                  <>
                    <Users size={16} className="mr-2" />
                    {translate('Grid View')}
                  </>
                )}
              </button>
              <a
                href="/login"
                className="btn-primary"
              >
                {translate('Sign In')}
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder={translate('Search businesses, services, or locations...')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {displayCategories.map(category => (
                  <option key={category.value} value={category.value}>
                    {category.icon} {translate(category.label)}
                    {category.count ? ` (${category.count})` : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Statistics Bar */}
          {stats.totalBusinesses && (
            <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg p-4 mt-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-primary-600">{stats.totalBusinesses}+</div>
                  <div className="text-sm text-primary-700">{translate('Active Businesses')}</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-secondary-600">{stats.totalReviews}+</div>
                  <div className="text-sm text-secondary-700">{translate('Customer Reviews')}</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">⭐ {stats.avgRating}</div>
                  <div className="text-sm text-green-700">{translate('Average Rating')}</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">{stats.newBusinessesThisMonth}+</div>
                  <div className="text-sm text-blue-700">{translate('New This Month')}</div>
                </div>
              </div>
            </div>
          )}

            {/* Category Pills */}
            <div className="flex flex-wrap gap-2 mt-4">
              {displayCategories.slice(1).map(category => (
                <button
                  key={category.value}
                  onClick={() => setSelectedCategory(category.value)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    selectedCategory === category.value
                      ? 'bg-primary-100 text-primary-700 border border-primary-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span className="mr-2">{category.icon}</span>
                  {translate(category.label)}
                  {category.count && (
                    <span className="ml-2 bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                      {category.count}
                    </span>
                  )}
                </button>
              ))}
            </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          /* Loading State */
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
              <Search size={24} className="text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {translate('Loading businesses...')}
            </h3>
            <p className="text-gray-600">
              {translate('Discovering amazing local businesses for you')}
            </p>
            {/* Loading Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-pulse">
                  <div className="h-48 bg-gray-200"></div>
                  <div className="p-6">
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4 mb-4"></div>
                    <div className="flex space-x-2 mb-4">
                      <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                      <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                    </div>
                    <div className="h-10 bg-gray-200 rounded"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <>
            {/* Stats */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {translate('Discover Local Businesses')}
                  </h3>
                  <p className="text-gray-600">
                    {translate('Found')} <span className="font-semibold">{filteredBusinesses.length}</span> {translate('businesses near you')}
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <Navigation size={16} />
                  <span>{translate('Sorted by distance')}</span>
                </div>
              </div>
            </div>

        {viewMode === 'grid' ? (
          <div>
            {/* Featured Businesses */}
            {displayFeatured.length > 0 && (
              <div className="mb-12">
                <h4 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                  <Star className="mr-2 text-yellow-500" size={20} />
                  {translate('Featured Businesses')}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {displayFeatured.map(business => (
                    <BusinessCard key={business.id} business={business} featured={true} />
                  ))}
                </div>
              </div>
            )}

            {/* All Businesses */}
            <div>
              <h4 className="text-xl font-bold text-gray-900 mb-6">
                {translate('All Businesses')}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredBusinesses.map(business => (
                  <BusinessCard key={business.id} business={business} />
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Map View Placeholder */
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin size={32} className="text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {translate('Interactive Map View')}
            </h3>
            <p className="text-gray-600 mb-6">
              {translate('Explore businesses on an interactive map with real-time locations and directions.')}
            </p>
            <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg p-6">
              <p className="text-primary-700 font-medium">
                🗺️ {translate('Map integration coming soon!')} 
                <br />
                <span className="text-sm text-primary-600">
                  {translate('Will include Google Maps integration, real-time directions, and location-based search.')}
                </span>
              </p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {filteredBusinesses.length === 0 && (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search size={32} className="text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {translate('No businesses found')}
            </h3>
            <p className="text-gray-600 mb-6">
              {translate('Try adjusting your search terms or category filters.')}
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
              }}
              className="btn-primary"
            >
              {translate('Clear Filters')}
            </button>
          </div>
        )}
        </>
        )}
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {translate('Own a Business?')}
            </h3>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              {translate('Join Break-even today and get discovered by thousands of potential customers. Create your professional website in minutes!')}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/register"
                className="btn-primary btn-lg"
              >
                {translate('Get Started Free')}
              </a>
              <a
                href="/login"
                className="btn-ghost btn-lg"
              >
                {translate('Sign In')}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Business Card Component
const BusinessCard = ({ business, featured = false }) => {
  // Simple fallback translate function
  const translate = (text) => text;

  return (
    <div className={`bg-white rounded-xl border overflow-hidden hover:shadow-lg transition-shadow ${
      featured ? 'border-primary-200 ring-2 ring-primary-100' : 'border-gray-200'
    }`}>
      {/* Business Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={business.image}
          alt={business.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {featured && (
          <div className="absolute top-3 left-3">
            <div className="bg-yellow-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center">
              <Star size={12} className="mr-1" />
              {translate('Featured')}
            </div>
          </div>
        )}
        <div className="absolute top-3 right-3 bg-white rounded-full px-2 py-1 text-xs font-medium text-gray-600">
          {business.distance}
        </div>
      </div>

      {/* Business Info */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="font-bold text-lg text-gray-900 mb-1">{business.name}</h3>
            <p className="text-gray-600 text-sm">{business.description}</p>
          </div>
        </div>

        {/* Rating */}
        <div className="flex items-center space-x-2 mb-4">
          <div className="flex items-center">
            <Star className="text-yellow-400 fill-current" size={16} />
            <span className="font-semibold text-gray-900 ml-1">{business.rating}</span>
          </div>
          <span className="text-gray-500 text-sm">({business.reviews} {translate('reviews')})</span>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {business.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Location & Hours */}
        <div className="space-y-2 text-sm text-gray-600 mb-4">
          <div className="flex items-center">
            <MapPin size={14} className="mr-2" />
            <span>{business.location}</span>
          </div>
          <div className="flex items-center">
            <Clock size={14} className="mr-2" />
            <span>{business.openTime}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <a
            href={`https://${business.website}`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex-1 text-center text-sm"
          >
            <Globe size={14} className="mr-2" />
            {translate('Visit Website')}
          </a>
          <a
            href={`tel:${business.phone}`}
            className="btn-ghost border border-gray-200 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Phone size={16} />
          </a>
        </div>
      </div>
    </div>
  );
};

export default Discover;