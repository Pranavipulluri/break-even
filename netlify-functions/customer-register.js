const { MongoClient, ObjectId } = require('mongodb');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = 'break_even_db';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

exports.handler = async (event, context) => {
    // Handle CORS
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ success: false, message: 'Method not allowed' })
        };
    }

    let client;
    try {
        const data = JSON.parse(event.body);
        
        // Validate required fields
        const requiredFields = ['register_name', 'register_email', 'register_password'];
        for (const field of requiredFields) {
            if (!data[field]) {
                return {
                    statusCode: 400,
                    headers,
                    body: JSON.stringify({ 
                        success: false, 
                        message: `${field.replace('register_', '').replace('_', ' ')} is required` 
                    })
                };
            }
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.register_email)) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Please enter a valid email address' 
                })
            };
        }

        // Validate password strength
        if (data.register_password.length < 6) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Password must be at least 6 characters long' 
                })
            };
        }

        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        const db = client.db(DATABASE_NAME);

        // Check if customer already exists
        const existingCustomer = await db.collection('customers').findOne({
            email: data.register_email.toLowerCase(),
            business_id: data.business_id ? new ObjectId(data.business_id) : null
        });

        if (existingCustomer) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({
                    success: false,
                    message: 'An account with this email already exists'
                })
            };
        }

        // Hash password
        const saltRounds = 10;
        const hashedPassword = await bcrypt.hash(data.register_password, saltRounds);

        // Create customer document
        const customerDoc = {
            name: data.register_name,
            email: data.register_email.toLowerCase(),
            phone: data.register_phone || '',
            password: hashedPassword,
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            website_source: data.website_source || 'unknown',
            marketing_emails: data.marketing_emails === 'yes',
            created_at: new Date(),
            last_login: new Date(),
            login_count: 1,
            is_active: true,
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown',
            user_agent: event.headers['user-agent'] || 'unknown'
        };

        // Insert customer
        const result = await db.collection('customers').insertOne(customerDoc);

        // If customer wants marketing emails, add to newsletter
        if (data.marketing_emails === 'yes') {
            const subscriberDoc = {
                name: data.register_name,
                email: data.register_email.toLowerCase(),
                phone: data.register_phone || '',
                source: 'customer_registration',
                interests: ['general'],
                business_id: data.business_id ? new ObjectId(data.business_id) : null,
                website_source: data.website_source || 'unknown',
                subscribed_at: new Date(),
                is_active: true
            };

            await db.collection('newsletter_subscribers').updateOne(
                { email: data.register_email.toLowerCase(), business_id: subscriberDoc.business_id },
                { $set: subscriberDoc },
                { upsert: true }
            );
        }

        // Track analytics
        const analyticsDoc = {
            type: 'customer_registration',
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            website_source: data.website_source || 'unknown',
            timestamp: new Date(),
            metadata: {
                has_phone: !!data.register_phone,
                marketing_emails: data.marketing_emails === 'yes'
            }
        };

        await db.collection('website_analytics').insertOne(analyticsDoc);

        // Generate JWT token
        const token = jwt.sign(
            { 
                customerId: result.insertedId.toString(),
                email: data.register_email.toLowerCase(),
                businessId: data.business_id
            },
            JWT_SECRET,
            { expiresIn: '7d' }
        );

        // Return customer data (without password)
        const customerData = {
            id: result.insertedId.toString(),
            name: data.register_name,
            email: data.register_email.toLowerCase(),
            phone: data.register_phone || '',
            created_at: new Date(),
            last_login: new Date(),
            token: token
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: 'Account created successfully! Welcome to our community.',
                customer: customerData
            })
        };

    } catch (error) {
        console.error('Error during customer registration:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: 'Internal server error. Please try again later.'
            })
        };
    } finally {
        if (client) {
            await client.close();
        }
    }
};
