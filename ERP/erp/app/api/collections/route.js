import connectDB from '@/lib/mongodb';
import mongoose from 'mongoose';

export async function GET() {
  try {
    await connectDB();
    
    // Get all collections in the database
    const db = mongoose.connection.db;
    const collections = await db.listCollections().toArray();
    
    const collectionNames = collections.map(collection => ({
      name: collection.name,
      type: collection.type || 'collection'
    }));
    
    return Response.json({ 
      success: true, 
      collections: collectionNames 
    });
  } catch (error) {
    console.error('Error fetching collections:', error);
    return Response.json({ 
      success: false, 
      error: error.message 
    }, { status: 500 });
  }
}
