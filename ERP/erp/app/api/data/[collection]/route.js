import connectDB from '@/lib/mongodb';
import mongoose from 'mongoose';

export async function GET(request, { params }) {
  try {
    await connectDB();
    
    const { collection } = params;
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit')) || 100;
    const skip = parseInt(searchParams.get('skip')) || 0;
    
    const db = mongoose.connection.db;
    const collectionData = await db.collection(collection)
      .find({})
      .limit(limit)
      .skip(skip)
      .toArray();
    
    // Get collection stats
    const count = await db.collection(collection).countDocuments();
    
    return Response.json({ 
      success: true, 
      data: collectionData,
      count,
      limit,
      skip
    });
  } catch (error) {
    console.error(`Error fetching data from collection ${params.collection}:`, error);
    return Response.json({ 
      success: false, 
      error: error.message 
    }, { status: 500 });
  }
}
