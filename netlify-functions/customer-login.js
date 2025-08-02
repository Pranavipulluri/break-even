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
        if (!data.login_email || !data.login_password) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Email and password are required' 
                })
            };
        }

        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        const db = client.db(DATABASE_NAME);

        // Find customer
        const customer = await db.collection('customers').findOne({
            email: data.login_email.toLowerCase(),
            business_id: data.business_id ? new ObjectId(data.business_id) : null
        });

        if (!customer) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({
                    success: false,
                    message: 'Invalid email or password'
                })
            };
        }

        // Verify password
        const passwordMatch = await bcrypt.compare(data.login_password, customer.password);
        
        if (!passwordMatch) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({
                    success: false,
                    message: 'Invalid email or password'
                })
            };
        }

        // Update last login
        await db.collection('customers').updateOne(
            { _id: customer._id },
            { 
                $set: { 
                    last_login: new Date(),
                    login_count: (customer.login_count || 0) + 1
                }
            }
        );

        // Generate JWT token
        const token = jwt.sign(
            { 
                customerId: customer._id.toString(),
                email: customer.email,
                businessId: data.business_id
            },
            JWT_SECRET,
            { expiresIn: '7d' }
        );

        // Return customer data (without password)
        const customerData = {
            id: customer._id.toString(),
            name: customer.name,
            email: customer.email,
            phone: customer.phone || '',
            created_at: customer.created_at,
            last_login: new Date(),
            token: token
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: 'Login successful',
                customer: customerData
            })
        };

    } catch (error) {
        console.error('Error during customer login:', error);
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
