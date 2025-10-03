import connectDB from '@/lib/mongodb';
import Student from '@/models/Student';
import Faculty from '@/models/Faculty';
import Course from '@/models/Course';
import Attendance from '@/models/Attendance';
import LeaveRequest from '@/models/LeaveRequest';
import Timetable from '@/models/Timetable';

const MODELS = {
  students: Student,
  faculties: Faculty,
  courses: Course,
  attendances: Attendance,
  leaverequests: LeaveRequest,
  timetables: Timetable
};

const POPULATE_OPTIONS = {
  students: null, // No population needed
  faculties: null, // No population needed
  courses: 'facultyInCharge', // Populate faculty details
  attendances: 'student', // Populate student details
  leaverequests: 'student handledBy', // Populate student and faculty details
  timetables: 'slots.course slots.faculty' // Populate course and faculty in slots
};

export async function GET(request, { params }) {
  try {
    await connectDB();
    
    const { collection } = params;
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit')) || 100;
    const skip = parseInt(searchParams.get('skip')) || 0;
    
    const Model = MODELS[collection];
    if (!Model) {
      return Response.json({ 
        success: false, 
        error: `Collection ${collection} not found` 
      }, { status: 404 });
    }
    
    let query = Model.find({});
    
    // Add population if needed
    const populateFields = POPULATE_OPTIONS[collection];
    if (populateFields) {
      query = query.populate(populateFields);
    }
    
    // Apply pagination
    query = query.limit(limit).skip(skip).sort({ createdAt: -1 });
    
    const collectionData = await query.exec();
    const count = await Model.countDocuments();
    
    // Format the data for better display
    const formattedData = collectionData.map(item => {
      const itemObj = item.toObject();
      
      // Format specific fields for better display
      if (collection === 'attendances') {
        // Calculate attendance percentage for display
        itemObj.attendancePercentage = Math.round(itemObj.attendancePercentage * 100) / 100;
      }
      
      if (collection === 'leaverequests') {
        // Format dates for better display
        if (itemObj.startDate) {
          itemObj.startDate = new Date(itemObj.startDate).toLocaleDateString();
        }
        if (itemObj.endDate) {
          itemObj.endDate = new Date(itemObj.endDate).toLocaleDateString();
        }
      }
      
      if (collection === 'courses' && itemObj.facultyInCharge) {
        // Simplify faculty display
        itemObj.facultyName = itemObj.facultyInCharge?.fullName || 'Not Assigned';
      }
      
      return itemObj;
    });
    
    return Response.json({ 
      success: true, 
      data: formattedData,
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
