import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'

export default function Faculties() {
  const [faculties, setFaculties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchFaculties()
  }, [])

  const fetchFaculties = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/faculties')
      setFaculties(response.data)
    } catch (err) {
      setError('Failed to fetch faculties data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Faculties...</h2>
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
          <h1>Faculties</h1>
          <p>View all faculty records in the system.</p>
          
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Designation</th>
                  <th>Subjects Count</th>
                </tr>
              </thead>
              <tbody>
                {faculties.map((faculty) => (
                  <tr key={faculty._id}>
                    <td>{faculty.employeeId}</td>
                    <td>{faculty.fullName}</td>
                    <td>{faculty.email}</td>
                    <td>{faculty.designation}</td>
                    <td>{faculty.subjects ? faculty.subjects.length : 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {faculties.length === 0 && (
            <div className="card">
              <p>No faculties found in the system.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
