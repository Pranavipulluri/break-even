import React, { useState } from 'react';
import { aiServices } from '../services/aiServices';
import toast from 'react-hot-toast';

const AITestPage = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testGeminiContent = async () => {
    setLoading(true);
    try {
      // Use development endpoint that doesn't require auth
      const response = await fetch('http://localhost:5000/api/ai-tools/dev/gemini-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: "Say hello and confirm you're working! Generate a short business tagline."
        })
      });
      
      const result = await response.json();
      setResult({ service: 'Gemini Content', data: result });
      
      if (result.success) {
        toast.success('Gemini AI is working!');
      } else {
        toast.error('Gemini AI failed: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      toast.error('Error testing Gemini: ' + error.message);
      setResult({ service: 'Gemini Content', error: error.message });
    }
    setLoading(false);
  };

  const testNetlifyDeploy = async () => {
    setLoading(true);
    try {
      const businessInfo = {
        hero_title: "Test Website",
        hero_subtitle: "Testing AI deployment",
        about_us: "This is a test website created by AI.",
        contact_cta: "Contact us for testing!"
      };
      
      const response = await fetch('http://localhost:5000/api/ai-tools/dev/netlify-deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          site_name: "AI Test Site",
          business_info: businessInfo
        })
      });
      
      const result = await response.json();
      setResult({ service: 'Netlify Deploy', data: result });
      
      if (result.success) {
        toast.success(`Website deployed! URL: ${result.website_url}`);
      } else {
        toast.error('Netlify deployment failed: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      toast.error('Error testing Netlify: ' + error.message);
      setResult({ service: 'Netlify Deploy', error: error.message });
    }
    setLoading(false);
  };

  const testGitHubDeploy = async () => {
    setLoading(true);
    try {
      const businessInfo = {
        hero_title: "GitHub Test Website",
        hero_subtitle: "Testing GitHub Pages deployment",
        about_us: "This is a test website deployed to GitHub Pages.",
        contact_cta: "Contact us for testing!"
      };
      
      const response = await fetch('http://localhost:5000/api/ai-tools/dev/github-deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          site_name: "GitHub Test Site",
          business_info: businessInfo
        })
      });
      
      const result = await response.json();
      setResult({ service: 'GitHub Deploy', data: result });
      
      if (result.success) {
        toast.success(`Website deployed! URL: ${result.website_url}`);
      } else {
        toast.error('GitHub deployment failed: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      toast.error('Error testing GitHub: ' + error.message);
      setResult({ service: 'GitHub Deploy', error: error.message });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">AI Services Test Page</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <button
          onClick={testGeminiContent}
          disabled={loading}
          className="btn-primary p-4 text-center"
        >
          {loading ? 'Testing...' : 'Test Gemini AI'}
        </button>
        
        <button
          onClick={testNetlifyDeploy}
          disabled={loading}
          className="btn-primary p-4 text-center bg-teal-600 hover:bg-teal-700"
        >
          {loading ? 'Deploying...' : 'Test Netlify Deploy'}
        </button>
        
        <button
          onClick={testGitHubDeploy}
          disabled={loading}
          className="btn-primary p-4 text-center bg-gray-800 hover:bg-gray-900"
        >
          {loading ? 'Deploying...' : 'Test GitHub Deploy'}
        </button>
      </div>

      {result && (
        <div className="bg-gray-50 border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Test Result: {result.service}</h3>
          
          {result.data && (
            <div className="space-y-4">
              <div>
                <strong>Success:</strong> {result.data.success ? '✅ Yes' : '❌ No'}
              </div>
              
              {result.data.success && result.data.website_url && (
                <div>
                  <strong>Website URL:</strong>
                  <br />
                  <a 
                    href={result.data.website_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline break-all"
                  >
                    {result.data.website_url}
                  </a>
                </div>
              )}
              
              {result.data.content && (
                <div>
                  <strong>Generated Content:</strong>
                  <p className="bg-white p-3 rounded border mt-2">{result.data.content}</p>
                </div>
              )}
              
              {result.data.error && (
                <div>
                  <strong>Error:</strong>
                  <p className="text-red-600 bg-red-50 p-3 rounded border mt-2">{result.data.error}</p>
                </div>
              )}
            </div>
          )}
          
          {result.error && (
            <div>
              <strong>Error:</strong>
              <p className="text-red-600 bg-red-50 p-3 rounded border mt-2">{result.error}</p>
            </div>
          )}
          
          <details className="mt-4">
            <summary className="cursor-pointer text-sm text-gray-600">Raw Response</summary>
            <pre className="bg-gray-100 p-3 rounded text-xs mt-2 overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default AITestPage;
