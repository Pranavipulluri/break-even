// Netlify Function to handle user registration from mini websites
const { MongoClient } = require('mongodb');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/breakeven';

exports.handler = async (event, context) => {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
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

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const body = JSON.parse(event.body);
    const { email, name, phone, website_source, business_id, newsletter_signup = true } = body;

    // Validate required fields
    if (!email || !website_source) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          error: 'Email and website_source are required',
          success: false 
        })
      };
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          error: 'Invalid email format',
          success: false 
        })
      };
    }

    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db();

    // Check if user already exists
    const existingUser = await db.collection('website_subscribers').findOne({ 
      email: email.toLowerCase(),
      website_source 
    });

    let result;
    if (existingUser) {
      // Update existing user
      result = await db.collection('website_subscribers').updateOne(
        { _id: existingUser._id },
        {
          $set: {
            name: name || existingUser.name,
            phone: phone || existingUser.phone,
            last_updated: new Date(),
            newsletter_signup,
            active: true
          },
          $inc: { registration_count: 1 }
        }
      );
    } else {
      // Create new user
      const newUser = {
        email: email.toLowerCase(),
        name: name || '',
        phone: phone || '',
        website_source,
        business_id: business_id || null,
        newsletter_signup,
        registration_count: 1,
        created_at: new Date(),
        last_updated: new Date(),
        active: true,
        tags: ['website_signup'],
        source_ip: event.headers['client-ip'] || event.headers['x-forwarded-for'] || 'unknown'
      };

      result = await db.collection('website_subscribers').insertOne(newUser);
    }

    // Log the registration for analytics
    await db.collection('registration_logs').insertOne({
      email: email.toLowerCase(),
      name: name || '',
      website_source,
      business_id,
      registration_type: existingUser ? 'returning' : 'new',
      timestamp: new Date(),
      source_ip: event.headers['client-ip'] || event.headers['x-forwarded-for'] || 'unknown',
      user_agent: event.headers['user-agent'] || 'unknown'
    });

    // Send welcome email (you can integrate with your email service here)
    // await sendWelcomeEmail(email, name, website_source);

    await client.close();

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: existingUser ? 'User updated successfully' : 'User registered successfully',
        user_id: existingUser ? existingUser._id : result.insertedId,
        is_new_user: !existingUser
      })
    };

  } catch (error) {
    console.error('Registration error:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Internal server error',
        message: 'Failed to register user'
      })
    };
  }
};
