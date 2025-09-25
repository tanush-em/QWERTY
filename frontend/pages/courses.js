import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'

export default function Courses() {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCourses()
  }, [])

  const fetchCourses = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/courses')
      setCourses(response.data)
    } catch (err) {
      setError('Failed to fetch courses data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Courses...</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error">
        {error}
      </div>
    )
  }

  return (
    <div>
      <div className="navbar">
        <div className="container">
          <h1>CSE-AIML ERP System</h1>
          <nav>
            <Link href="/">Dashboard</Link>
            <Link href="/students">Students</Link>
            <Link href="/faculties">Faculties</Link>
            <Link href="/courses">Courses</Link>
            <Link href="/leaves">Leaves</Link>
            <Link href="/timetable">Timetable</Link>
          </nav>
        </div>
      </div>

      <div className="main-content">
        <div className="container">
          <h1>Courses</h1>
          <p>View all course records in the system.</p>
          
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Course Code</th>
                  <th>Title</th>
                  <th>Credits</th>
                  <th>Semester</th>
                  <th>Faculty In Charge</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {courses.map((course) => (
                  <tr key={course._id}>
                    <td>{course.code}</td>
                    <td>{course.title}</td>
                    <td>{course.credits}</td>
                    <td>{course.semester}</td>
                    <td>{course.facultyInCharge || 'Not assigned'}</td>
                    <td>{course.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {courses.length === 0 && (
            <div className="card">
              <p>No courses found in the system.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
