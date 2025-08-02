const { MongoClient, ObjectId } = require('mongodb');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = 'break_even_db';

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
        const requiredFields = ['newsletter_name', 'newsletter_email'];
        for (const field of requiredFields) {
            if (!data[field]) {
                return {
                    statusCode: 400,
                    headers,
                    body: JSON.stringify({ 
                        success: false, 
                        message: `${field.replace('newsletter_', '').replace('_', ' ')} is required` 
                    })
                };
            }
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.newsletter_email)) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Please enter a valid email address' 
                })
            };
        }

        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        const db = client.db(DATABASE_NAME);

        // Parse interests
        const interests = data.newsletter_interests ? 
            data.newsletter_interests.split(',').filter(i => i.trim()) : 
            ['general'];
        
        // Prepare subscriber document
        const subscriberDoc = {
            name: data.newsletter_name,
            email: data.newsletter_email,
            phone: data.newsletter_phone || '',
            source: 'newsletter_signup',
            interests: interests,
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            website_source: data.website_source || 'unknown',
            subscribed_at: new Date(),
            is_active: true,
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown',
            user_agent: event.headers['user-agent'] || 'unknown',
            metadata: {
                signup_method: 'mini_website',
                interests_selected: interests.length
            }
        };

        // Check if subscriber already exists
        const existingSubscriber = await db.collection('newsletter_subscribers').findOne({
            email: data.newsletter_email,
            business_id: subscriberDoc.business_id
        });

        let result;
        let isNewSubscriber = false;

        if (existingSubscriber) {
            // Update existing subscriber
            result = await db.collection('newsletter_subscribers').updateOne(
                { _id: existingSubscriber._id },
                { 
                    $set: {
                        name: subscriberDoc.name,
                        interests: subscriberDoc.interests,
                        is_active: true,
                        updated_at: new Date(),
                        metadata: subscriberDoc.metadata
                    }
                }
            );
        } else {
            // Insert new subscriber
            result = await db.collection('newsletter_subscribers').insertOne(subscriberDoc);
            isNewSubscriber = true;
        }

        // Track analytics
        const analyticsDoc = {
            type: 'newsletter_signup',
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            website_source: data.website_source || 'unknown',
            timestamp: new Date(),
            metadata: {
                interests: interests,
                is_new_subscriber: isNewSubscriber,
                has_phone: !!data.newsletter_phone
            }
        };

        await db.collection('website_analytics').insertOne(analyticsDoc);

        // Send welcome email (you can implement this later)
        // await sendWelcomeEmail(data.newsletter_email, data.newsletter_name);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: isNewSubscriber ? 
                    'Welcome! You\'ve successfully subscribed to our newsletter.' : 
                    'Thank you! Your newsletter preferences have been updated.',
                subscriber_id: result.insertedId ? result.insertedId.toString() : existingSubscriber._id.toString(),
                is_new: isNewSubscriber
            })
        };

    } catch (error) {
        console.error('Error processing newsletter signup:', error);
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
