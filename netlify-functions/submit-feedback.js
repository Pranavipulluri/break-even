// Netlify Function to handle feedback submission from mini websites
const { MongoClient, ObjectId } = require('mongodb');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = 'break_even_db';

// Sentiment analysis function (simple keyword-based)
function analyzeSentiment(text) {
    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'awesome', 'fantastic', 'wonderful', 'satisfied', 'happy', 'pleased'];
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointed', 'angry', 'frustrated', 'annoyed'];
    
    const words = text.toLowerCase().split(/\s+/);
    let positiveCount = 0;
    let negativeCount = 0;
    
    words.forEach(word => {
        if (positiveWords.includes(word)) positiveCount++;
        if (negativeWords.includes(word)) negativeCount++;
    });
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
}

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
        const requiredFields = ['customer_name', 'customer_email', 'feedback_message', 'rating'];
        for (const field of requiredFields) {
            if (!data[field]) {
                return {
                    statusCode: 400,
                    headers,
                    body: JSON.stringify({ 
                        success: false, 
                        message: `${field} is required` 
                    })
                };
            }
        }

        // Connect to MongoDB
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        const db = client.db(DATABASE_NAME);

        // Analyze sentiment
        const sentiment = analyzeSentiment(data.feedback_message);
        
        // Prepare feedback document
        const feedbackDoc = {
            customer_name: data.customer_name,
            customer_email: data.customer_email,
            customer_phone: data.customer_phone || '',
            feedback_message: data.feedback_message,
            feedback_category: data.feedback_category || 'general',
            rating: parseInt(data.rating),
            product_interest: data.product_interest || '',
            follow_up: data.follow_up === 'yes',
            sentiment: sentiment,
            website_source: data.website_source || 'unknown',
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            type: 'feedback',
            created_at: new Date(),
            ip_address: event.headers['x-forwarded-for'] || event.headers['x-real-ip'] || 'unknown',
            user_agent: event.headers['user-agent'] || 'unknown'
        };

        // Insert feedback
        const result = await db.collection('customer_feedback').insertOne(feedbackDoc);

        // If customer wants newsletter signup, add to subscribers
        if (data.newsletter_signup === 'yes') {
            const subscriberDoc = {
                name: data.customer_name,
                email: data.customer_email,
                phone: data.customer_phone || '',
                source: 'feedback_form',
                interests: ['feedback'],
                business_id: data.business_id ? new ObjectId(data.business_id) : null,
                website_source: data.website_source || 'unknown',
                subscribed_at: new Date(),
                is_active: true
            };

            // Upsert subscriber (update if exists, insert if not)
            await db.collection('newsletter_subscribers').updateOne(
                { email: data.customer_email, business_id: subscriberDoc.business_id },
                { $set: subscriberDoc },
                { upsert: true }
            );
        }

        // Track analytics
        const analyticsDoc = {
            type: 'feedback_submission',
            business_id: data.business_id ? new ObjectId(data.business_id) : null,
            website_source: data.website_source || 'unknown',
            rating: parseInt(data.rating),
            sentiment: sentiment,
            category: data.feedback_category || 'general',
            timestamp: new Date(),
            metadata: {
                has_product_interest: !!data.product_interest,
                wants_follow_up: data.follow_up === 'yes',
                newsletter_signup: data.newsletter_signup === 'yes'
            }
        };

        await db.collection('website_analytics').insertOne(analyticsDoc);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: 'Thank you for your feedback! We appreciate your input and will review it carefully.',
                feedback_id: result.insertedId.toString(),
                sentiment: sentiment
            })
        };

    } catch (error) {
        console.error('Error submitting feedback:', error);
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

// Calculate sentiment score (-1 to 1)
function calculateSentimentScore(text) {
  const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'awesome', 'perfect', 'outstanding', 'brilliant', 'superb', 'happy', 'satisfied', 'pleased', 'impressed'];
  const negativeWords = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'disappointing', 'poor', 'unsatisfied', 'angry', 'frustrated', 'annoying', 'useless', 'waste', 'problem', 'issue'];
  
  const words = text.toLowerCase().split(/\s+/);
  let score = 0;
  
  words.forEach(word => {
    if (positiveWords.includes(word)) score += 1;
    if (negativeWords.includes(word)) score -= 1;
  });
  
  // Normalize score based on text length
  return Math.max(-1, Math.min(1, score / Math.max(1, words.length / 10)));
}

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
    const { 
      feedback, 
      rating, 
      email, 
      name, 
      website_source, 
      business_id,
      feedback_type = 'general',
      category = 'feedback'
    } = body;

    // Validate required fields
    if (!feedback || !website_source) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          error: 'Feedback and website_source are required',
          success: false 
        })
      };
    }

    // Validate rating if provided
    if (rating && (rating < 1 || rating > 5)) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          error: 'Rating must be between 1 and 5',
          success: false 
        })
      };
    }

    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    const db = client.db();

    // Perform sentiment analysis
    const sentiment = analyzeSentiment(feedback);
    const sentimentScore = calculateSentimentScore(feedback);

    // Create feedback document
    const feedbackDoc = {
      feedback: feedback.trim(),
      rating: rating || null,
      email: email ? email.toLowerCase() : null,
      name: name || 'Anonymous',
      website_source,
      business_id: business_id || null,
      feedback_type,
      category,
      sentiment: {
        label: sentiment,
        score: sentimentScore,
        confidence: Math.abs(sentimentScore)
      },
      metadata: {
        word_count: feedback.trim().split(/\s+/).length,
        character_count: feedback.length,
        has_email: !!email,
        has_rating: !!rating
      },
      created_at: new Date(),
      source_ip: event.headers['client-ip'] || event.headers['x-forwarded-for'] || 'unknown',
      user_agent: event.headers['user-agent'] || 'unknown',
      processed: false
    };

    // Insert feedback
    const result = await db.collection('website_feedback').insertOne(feedbackDoc);

    // Update user profile if email provided
    if (email) {
      await db.collection('website_subscribers').updateOne(
        { email: email.toLowerCase(), website_source },
        {
          $set: {
            last_feedback_date: new Date(),
            name: name || undefined
          },
          $inc: { feedback_count: 1 },
          $push: {
            feedback_history: {
              feedback_id: result.insertedId,
              rating: rating || null,
              sentiment: sentiment,
              date: new Date()
            }
          }
        },
        { upsert: false }
      );
    }

    // Create analytics summary for dashboard
    await db.collection('feedback_analytics').updateOne(
      { 
        website_source,
        date: new Date().toISOString().split('T')[0] // YYYY-MM-DD format
      },
      {
        $inc: {
          total_feedback: 1,
          [`sentiment_${sentiment}`]: 1,
          total_rating: rating || 0,
          rating_count: rating ? 1 : 0
        },
        $set: {
          last_updated: new Date()
        }
      },
      { upsert: true }
    );

    await client.close();

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: 'Feedback submitted successfully',
        feedback_id: result.insertedId,
        sentiment: {
          label: sentiment,
          score: sentimentScore
        },
        analytics: {
          word_count: feedbackDoc.metadata.word_count,
          sentiment: sentiment
        }
      })
    };

  } catch (error) {
    console.error('Feedback submission error:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Internal server error',
        message: 'Failed to submit feedback'
      })
    };
  }
};
