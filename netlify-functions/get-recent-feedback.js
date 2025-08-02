const { MongoClient, ObjectId } = require('mongodb');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = 'break_even_db';

exports.handler = async (event, context) => {
    // Handle CORS
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    if (event.httpMethod !== 'GET') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ success: false, message: 'Method not allowed' })
        };
    }

    let client;
    try {
        const { queryStringParameters } = event;
        const business_id = queryStringParameters?.business_id;
        const limit = parseInt(queryStringParameters?.limit) || 10;

        if (!business_id) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Business ID is required' 
                })
            };
        }

        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        const db = client.db(DATABASE_NAME);

        // Get recent feedback (only positive and neutral feedback for public display)
        const feedback = await db.collection('customer_feedback').find({
            business_id: new ObjectId(business_id),
            sentiment: { $in: ['positive', 'neutral'] }, // Only show positive/neutral feedback publicly
            rating: { $gte: 3 } // Only show 3+ star ratings
        }).sort({ created_at: -1 }).limit(limit).toArray();

        // Remove sensitive information and format for display
        const publicFeedback = feedback.map(item => ({
            customer_name: item.customer_name || 'Anonymous Customer',
            feedback_message: item.feedback_message,
            rating: item.rating,
            sentiment: item.sentiment,
            feedback_category: item.feedback_category,
            created_at: item.created_at
        }));

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                feedback: publicFeedback,
                count: publicFeedback.length
            })
        };

    } catch (error) {
        console.error('Error fetching recent feedback:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: 'Internal server error. Please try again later.',
                feedback: []
            })
        };
    } finally {
        if (client) {
            await client.close();
        }
    }
};
