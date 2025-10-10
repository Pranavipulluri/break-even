const { MongoClient } = require('mongodb');

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
let cachedClient = null;

async function connectToDatabase() {
  if (cachedClient) {
    return cachedClient;
  }
  
  const client = new MongoClient(MONGODB_URI);
  await client.connect();
  cachedClient = client;
  return client;
}

// Email service (using SendGrid or similar)
async function sendConsultationEmail(consultationData) {
  // You can integrate with SendGrid, Mailgun, or another email service here
  console.log('Sending consultation confirmation email:', consultationData);
  
  // For now, we'll log the email content
  // In production, replace this with actual email sending
  return {
    success: true,
    message: 'Email sent successfully'
  };
}

exports.handler = async (event, context) => {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  };

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    // Get firm ID from the request body
    const consultationData = JSON.parse(event.body);
    const firmId = consultationData.firmId;
    
    if (!firmId) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          success: false, 
          error: 'Firm ID is required' 
        }),
      };
    }
    
    console.log('Booking consultation for firm:', firmId);
    console.log('Consultation data:', consultationData);

    // Connect to database
    const client = await connectToDatabase();
    const db = client.db('break_even');
    
    // Create consultation record
    const consultation = {
      consultation_id: `cons_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      firm_id: firmId,
      client_name: consultationData.name,
      client_email: consultationData.email,
      client_phone: consultationData.phone || '',
      preferred_date: consultationData.date,
      preferred_time: consultationData.time,
      consultation_type: consultationData.type || 'general',
      case_description: consultationData.description || '',
      status: 'pending',
      created_at: new Date(),
      updated_at: new Date()
    };

    // Insert consultation
    await db.collection('consultations').insertOne(consultation);
    
    // Get firm info for email
    const firm = await db.collection('law_firms').findOne({ firm_id: firmId });
    
    // Send confirmation emails
    const emailData = {
      ...consultation,
      firm_name: firm?.firm_name || 'Law Firm',
      firm_email: firm?.contact?.email_address || '',
      firm_phone: firm?.contact?.phone_number || ''
    };
    
    // Send email to client and firm
    await sendConsultationEmail(emailData);
    
    // Update analytics
    await db.collection('law_firm_analytics').updateOne(
      { firm_id: firmId },
      { 
        $inc: { consultation_requests: 1 },
        $set: { last_consultation_request: new Date() }
      },
      { upsert: true }
    );

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'Consultation booked successfully',
        consultation_id: consultation.consultation_id,
        firm_contact: {
          name: firm?.firm_name,
          email: firm?.contact?.email_address,
          phone: firm?.contact?.phone_number
        }
      }),
    };

  } catch (error) {
    console.error('Error booking consultation:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Failed to book consultation',
        details: error.message
      }),
    };
  }
};