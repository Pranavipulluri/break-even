// Netlify Function to get products for child websites
const { MongoClient } = require('mongodb');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/breakeven';

exports.handler = async (event, context) => {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle OPTIONS request for CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const business_id = event.queryStringParameters?.business_id;

    // Connect to MongoDB
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db();

    // Get products for the business
    let query = {};
    if (business_id) {
      query.business_id = business_id;
    }

    const products = await db.collection('products').find(query).limit(20).toArray();

    await client.close();

    // Return sample products if none found
    if (products.length === 0) {
      const sampleProducts = [
        {
          id: '1',
          name: 'Fresh Bread',
          price: '$5.99',
          description: 'Freshly baked daily bread',
          image: '',
          stock: 10,
          category: 'Bakery'
        },
        {
          id: '2',
          name: 'Chocolate Cake',
          price: '$15.99',
          description: 'Rich chocolate cake',
          image: '',
          stock: 5,
          category: 'Desserts'
        },
        {
          id: '3',
          name: 'Croissants',
          price: '$3.50',
          description: 'Buttery French croissants',
          image: '',
          stock: 15,
          category: 'Pastries'
        }
      ];

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          success: true,
          products: sampleProducts,
          message: 'Sample products displayed'
        })
      };
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        products: products.map(product => ({
          id: product._id.toString(),
          name: product.name,
          price: product.price,
          description: product.description,
          image: product.image || '',
          stock: product.stock || 0,
          category: product.category || 'General'
        }))
      })
    };

  } catch (error) {
    console.error('Error fetching products:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Failed to fetch products',
        message: error.message
      })
    };
  }
};
