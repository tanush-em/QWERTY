import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'

export default function Students() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStudents()
  }, [])

  const fetchStudents = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/students')
      setStudents(response.data)
    } catch (err) {
      setError('Failed to fetch students data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Students...</h2>
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
          <h1>Students</h1>
          <p>View all student records in the system.</p>
          
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Roll No.</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Year</th>
                  <th>Batch</th>
                  <th>Date of Birth</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student._id}>
                    <td>{student.roll}</td>
                    <td>{student.fullName}</td>
                    <td>{student.email}</td>
                    <td>{student.phone}</td>
                    <td>{student.year}</td>
                    <td>{student.batch}</td>
                    <td>{formatDate(student.dateOfBirth)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {students.length === 0 && (
            <div className="card">
              <p>No students found in the system.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
