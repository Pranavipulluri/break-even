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
        const requiredFields = ['interest_name', 'interest_email', 'interested_products'];
        for (const field of requiredFields) {
            if (!data[field]) {
                return {
                    statusCode: 400,
                    headers,
                    body: JSON.stringify({ 
                        success: false, 
                        message: `${field.replace('interest_', '').replace('_', ' ')} is required` 
                    })
                };
            }
        }

        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        const db = client.db(DATABASE_NAME);
        
        // Prepare interest document
        const interestDoc = {
            customer_name: data.interest_name,
            customer_email: data.interest_email,
            customer_phone: data.interest_phone || '',
            interested_products: data.interested_products,
            budget_range: data.budget_range || '',
            purchase_timeline: data.purchase_timeline || '',
            website_source: data.website_source || 'unknown',
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            type: 'product_interest',
            lead_score: calculateLeadScore(data),
            created_at: new Date(),
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown',
            user_agent: event.headers['user-agent'] || 'unknown',
            status: 'new'
        };

        // Insert interest
        const result = await db.collection('product_interests').insertOne(interestDoc);

        // If customer wants newsletter signup, add to subscribers
        if (data.newsletter_signup === 'yes') {
            const subscriberDoc = {
                name: data.interest_name,
                email: data.interest_email,
                phone: data.interest_phone || '',
                source: 'product_interest',
                interests: ['products', 'promotions'],
                business_id: data.business_id ? new ObjectId(data.business_id) : null,
                website_source: data.website_source || 'unknown',
                subscribed_at: new Date(),
                is_active: true,
                metadata: {
                    interested_products: data.interested_products,
                    budget_range: data.budget_range,
                    purchase_timeline: data.purchase_timeline
                }
            };

            // Upsert subscriber (update if exists, insert if not)
            await db.collection('newsletter_subscribers').updateOne(
                { email: data.interest_email, business_id: subscriberDoc.business_id },
                { $set: subscriberDoc },
                { upsert: true }
            );
        }

        // Track analytics
        const analyticsDoc = {
            type: 'product_interest',
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            website_source: data.website_source || 'unknown',
            lead_score: interestDoc.lead_score,
            timestamp: new Date(),
            metadata: {
                budget_range: data.budget_range,
                purchase_timeline: data.purchase_timeline,
                newsletter_signup: data.newsletter_signup === 'yes',
                has_phone: !!data.interest_phone
            }
        };

        await db.collection('website_analytics').insertOne(analyticsDoc);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: 'Thank you for your interest! We\'ll be in touch soon with more information about our products.',
                interest_id: result.insertedId.toString(),
                lead_score: interestDoc.lead_score
            })
        };

    } catch (error) {
        console.error('Error submitting product interest:', error);
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

// Calculate lead score based on provided information
function calculateLeadScore(data) {
    let score = 0;
    
    // Base score for submitting interest
    score += 10;
    
    // Phone number provided
    if (data.interest_phone) score += 15;
    
    // Budget range scoring
    const budgetScores = {
        'under_100': 5,
        '100_500': 10,
        '500_1000': 15,
        '1000_5000': 20,
        'over_5000': 25
    };
    score += budgetScores[data.budget_range] || 0;
    
    // Purchase timeline scoring
    const timelineScores = {
        'immediately': 30,
        'within_week': 25,
        'within_month': 20,
        'within_quarter': 15,
        'just_browsing': 5
    };
    score += timelineScores[data.purchase_timeline] || 0;
    
    // Newsletter signup
    if (data.newsletter_signup === 'yes') score += 10;
    
    // Product interest detail (longer description = higher interest)
    if (data.interested_products && data.interested_products.length > 50) {
        score += 10;
    }
    
    return Math.min(score, 100); // Cap at 100
}
