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

// Email service for contact inquiries
async function sendContactEmail(contactData, firmData) {
  console.log('Sending contact inquiry email:', contactData);
  
  // Email content for firm
  const firmEmailContent = `
    New Contact Inquiry for ${firmData.firm_name}
    
    From: ${contactData.name}
    Email: ${contactData.email}
    Phone: ${contactData.phone || 'Not provided'}
    Subject: ${contactData.subject || 'General Inquiry'}
    
    Message:
    ${contactData.message}
    
    Received: ${new Date().toLocaleString()}
  `;

  // Email content for client
  const clientEmailContent = `
    Thank you for contacting ${firmData.firm_name}
    
    We have received your inquiry and will respond within 24 hours.
    
    Your message:
    ${contactData.message}
    
    Contact Information:
    Phone: ${firmData.contact?.phone_number || 'Contact us through our website'}
    Email: ${firmData.contact?.email_address}
    Address: ${firmData.contact?.office_address || ''}
    
    Best regards,
    ${firmData.firm_name} Team
  `;

  // In production, send actual emails here
  console.log('Firm email:', firmEmailContent);
  console.log('Client email:', clientEmailContent);
  
  return {
    success: true,
    message: 'Contact emails sent successfully'
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
    const contactData = JSON.parse(event.body);
    const firmId = contactData.firmId;
    
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
    
    console.log('Contact inquiry for firm:', firmId);
    console.log('Contact data:', contactData);

    // Connect to database
    const client = await connectToDatabase();
    const db = client.db('break_even');
    
    // Create contact record
    const contact = {
      contact_id: `contact_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      firm_id: firmId,
      name: contactData.name,
      email: contactData.email,
      phone: contactData.phone || '',
      subject: contactData.subject || 'General Inquiry',
      message: contactData.message,
      status: 'new',
      created_at: new Date(),
      updated_at: new Date()
    };

    // Insert contact record
    await db.collection('law_firm_contacts').insertOne(contact);
    
    // Get firm info
    const firm = await db.collection('law_firms').findOne({ firm_id: firmId });
    
    if (!firm) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({
          success: false,
          error: 'Law firm not found'
        }),
      };
    }
    
    // Send emails
    await sendContactEmail(contactData, firm);
    
    // Update analytics
    await db.collection('law_firm_analytics').updateOne(
      { firm_id: firmId },
      { 
        $inc: { contact_inquiries: 1 },
        $set: { last_contact_inquiry: new Date() }
      },
      { upsert: true }
    );

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'Your message has been sent successfully. We will respond within 24 hours.',
        contact_id: contact.contact_id,
        firm_info: {
          name: firm.firm_name,
          response_time: '24 hours'
        }
      }),
    };

  } catch (error) {
    console.error('Error processing contact:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Failed to send message',
        details: error.message
      }),
    };
  }
};