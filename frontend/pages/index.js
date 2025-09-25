import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/dashboard')
      setStats(response.data)
    } catch (err) {
      setError('Failed to fetch dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Dashboard...</h2>
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
          <h1>Dashboard</h1>
          <p>Welcome to the CSE-AIML ERP System. This is a read-only interface for viewing student, faculty, course, and leave records.</p>
          
          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <h3>{stats.totalStudents}</h3>
                <p>Total Students</p>
              </div>
              <div className="stat-card">
                <h3>{stats.totalFaculties}</h3>
                <p>Total Faculties</p>
              </div>
              <div className="stat-card">
                <h3>{stats.totalCourses}</h3>
                <p>Total Courses</p>
              </div>
              <div className="stat-card">
                <h3>{stats.totalLeaves}</h3>
                <p>Total Leave Applications</p>
              </div>
            </div>
          )}

          <div className="card">
            <h2>Quick Actions</h2>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <Link href="/students" className="btn">View Students</Link>
              <Link href="/faculties" className="btn">View Faculties</Link>
              <Link href="/courses" className="btn">View Courses</Link>
              <Link href="/leaves" className="btn">View Leaves</Link>
              <Link href="/timetable" className="btn">View Timetable</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
