import { ArrowRight, Eye, EyeOff, Lock, Mail, MapPin, Search, Shield, Sparkles, Zap } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { user, login, googleLogin, microsoftLogin } = useAuth();
  
  const { register, handleSubmit, formState: { errors } } = useForm();

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      await login(data.email, data.password);
      toast.success('Welcome back! 🎉');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);
      // In development mode, prompt for mock email and name
      const email = prompt("Enter mock Google email:", "google.user@example.com");
      if (!email) return;
      const name = prompt("Enter mock Google display name:", "Google User");
      if (!name) return;

      const mockToken = `mock_google_${name.replace(/\s+/g, '')}_${email}`;
      await googleLogin(mockToken);
      toast.success('Welcome! Signed in with Google 🎉');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Google Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleMicrosoftSignIn = async () => {
    try {
      setLoading(true);
      // In development mode, prompt for mock email and name
      const email = prompt("Enter mock Microsoft email:", "ms.user@example.com");
      if (!email) return;
      const name = prompt("Enter mock Microsoft display name:", "Microsoft User");
      if (!name) return;

      const mockToken = `mock_ms_${name.replace(/\s+/g, '')}_${email}`;
      await microsoftLogin(mockToken);
      toast.success('Welcome! Signed in with Microsoft 🎉');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Microsoft Login failed');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: Sparkles, title: 'AI-Powered Tools', description: 'Generate content and get business insights' },
    { icon: Shield, title: 'Secure & Reliable', description: 'Your data is protected with enterprise-grade security' },
    { icon: Zap, title: 'Real-time Updates', description: 'Get instant notifications for customer interactions' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex relative">
      {/* Discover Button - Floating Action */}
      <Link 
        to="/discover" 
        className="fixed top-4 right-4 z-50 bg-gradient-to-r from-primary-600 to-secondary-600 text-white px-4 py-2 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 font-medium"
      >
        <Search size={16} />
        <span className="hidden sm:inline">Discover Businesses</span>
        <span className="sm:hidden">Discover</span>
      </Link>
      {/* Left Side - Features */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 to-secondary-600"></div>
        <div className="absolute inset-0 bg-hero-pattern opacity-10"></div>
        
        {/* Floating Elements */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-white/10 rounded-full animate-float"></div>
        <div className="absolute bottom-32 right-16 w-24 h-24 bg-white/10 rounded-full animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-10 w-16 h-16 bg-white/10 rounded-full animate-float" style={{ animationDelay: '4s' }}></div>
        
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="mb-12">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">B</span>
              </div>
              <h1 className="text-3xl font-bold font-display">Break-even</h1>
            </div>
            <h2 className="text-4xl font-bold mb-4 leading-tight">
              Grow Your Business with AI-Powered Tools
            </h2>
            <p className="text-xl text-white/80 leading-relaxed">
              Create stunning websites, manage customers, and boost your business 
              with intelligent automation and insights.
            </p>
          </div>

            <div className="space-y-6">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3 mb-3">
                  <MapPin className="text-white" size={20} />
                  <h3 className="font-semibold text-white">Discover Local Businesses</h3>
                </div>
                <p className="text-white/80 text-sm mb-3">
                  Explore businesses created with Break-even platform. Find services, restaurants, and shops near you!
                </p>
                <Link 
                  to="/discover" 
                  className="inline-flex items-center text-white bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  <Search size={14} className="mr-2" />
                  Browse Now
                </Link>
              </div>
              
              {features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-4 group">
                <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl group-hover:bg-white/20 transition-colors">
                  <feature.icon size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{feature.title}</h3>
                  <p className="text-white/70">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold">B</span>
              </div>
              <h1 className="text-2xl font-bold text-gradient font-display">Break-even</h1>
            </div>
            
            {/* Mobile Discover CTA */}
            <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-4 mb-6 border border-primary-100">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <MapPin className="text-primary-600" size={18} />
                <span className="font-semibold text-primary-700">Discover Local Businesses</span>
              </div>
              <p className="text-sm text-primary-600 mb-3">
                Find amazing businesses near you
              </p>
              <Link 
                to="/discover" 
                className="btn-primary btn-sm w-full flex items-center justify-center"
              >
                <Search size={14} className="mr-2" />
                Explore Now
              </Link>
            </div>
          </div>

          <div className="card border-0 shadow-large">
            <div className="text-center mb-8">
              <h2 className="heading-2 text-gray-900 mb-2">Welcome back!</h2>
              <p className="text-gray-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-primary-600 hover:text-primary-700 font-semibold transition-colors">
                  Sign up for free
                </Link>
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Email Field */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  Email address
                </label>
                <div className="relative">
                  <input
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                    type="email"
                    className={`input-field pl-12 ${errors.email ? 'input-error' : ''}`}
                    placeholder="Enter your email"
                  />
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                </div>
                {errors.email && (
                  <p className="text-danger-600 text-sm flex items-center space-x-1">
                    <span>{errors.email.message}</span>
                  </p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  Password
                </label>
                <div className="relative">
                  <input
                    {...register('password', {
                      required: 'Password is required',
                      minLength: {
                        value: 6,
                        message: 'Password must be at least 6 characters'
                      }
                    })}
                    type={showPassword ? 'text' : 'password'}
                    className={`input-field pl-12 pr-12 ${errors.password ? 'input-error' : ''}`}
                    placeholder="Enter your password"
                  />
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <button
                    type="button"
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-danger-600 text-sm">{errors.password.message}</p>
                )}
              </div>

              {/* Remember & Forgot */}
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded transition-colors"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                    Remember me
                  </label>
                </div>

                <Link
                  to="/forgot-password"
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full btn-lg group relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-primary-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                
                <div className="relative flex items-center justify-center space-x-2">
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <span>Sign in</span>
                      <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </div>
              </button>
            </form>

            {/* Social Login */}
            <div className="mt-8">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white text-gray-500 font-medium">Or continue with</span>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-3">
                <button 
                  type="button"
                  onClick={handleGoogleSignIn}
                  className="btn-ghost border border-gray-200 hover:border-gray-300 hover:shadow-sm"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="currentColor"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span className="ml-2">Google</span>
                </button>

                <button 
                  type="button"
                  onClick={handleMicrosoftSignIn}
                  className="btn-ghost border border-gray-200 hover:border-gray-300 hover:shadow-sm"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 23 23">
                    <path fill="#F25022" d="M1.5 1.5h9.25v9.25H1.5z"/>
                    <path fill="#7FBA00" d="M12.25 1.5H21.5v9.25h-9.25z"/>
                    <path fill="#00A4EF" d="M1.5 12.25h9.25V21.5H1.5z"/>
                    <path fill="#FFB900" d="M12.25 12.25H21.5V21.5h-9.25z"/>
                  </svg>
                  <span className="ml-2">Microsoft</span>
                </button>
              </div>
            </div>
          </div>

          {/* Terms */}
          <p className="mt-8 text-center text-xs text-gray-500">
            By signing in, you agree to our{' '}
            <Link to="/terms" className="text-primary-600 hover:text-primary-700">Terms of Service</Link>
            {' '}and{' '}
            <Link to="/privacy" className="text-primary-600 hover:text-primary-700">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

