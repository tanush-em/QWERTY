import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'

export default function Timetable() {
  const [timetable, setTimetable] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedDay, setSelectedDay] = useState('Monday')

  useEffect(() => {
    fetchTimetable()
  }, [])

  const fetchTimetable = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/timetable')
      setTimetable(response.data)
    } catch (err) {
      setError('Failed to fetch timetable data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'lecture':
        return '#3498db'
      case 'lab':
        return '#e74c3c'
      case 'break':
        return '#95a5a6'
      default:
        return '#2c3e50'
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'lecture':
        return '📚'
      case 'lab':
        return '🔬'
      case 'break':
        return '☕'
      default:
        return '📝'
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Timetable...</h2>
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

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
  const selectedDayData = timetable.find(day => day.dayOfWeek === selectedDay)

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
          <h1>Class Timetable</h1>
          <p>View the weekly class schedule for CSE-AIML students.</p>
          
          {/* Day Selector */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h3>Select Day</h3>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {days.map(day => (
                <button
                  key={day}
                  onClick={() => setSelectedDay(day)}
                  className={`btn ${selectedDay === day ? 'btn-primary' : 'btn-secondary'}`}
                  style={{
                    backgroundColor: selectedDay === day ? '#3498db' : '#95a5a6',
                    color: 'white',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {day}
                </button>
              ))}
            </div>
          </div>

          {/* Timetable for Selected Day */}
          {selectedDayData && (
            <div className="card">
              <h2>{selectedDayData.dayOfWeek} Schedule</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Period</th>
                      <th>Time</th>
                      <th>Type</th>
                      <th>Course</th>
                      <th>Room</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedDayData.slots.map((slot, index) => (
                      <tr key={index}>
                        <td>{slot.period}</td>
                        <td>{slot.startTime} - {slot.endTime}</td>
                        <td>
                          <span style={{ 
                            color: getTypeColor(slot.type),
                            fontWeight: 'bold'
                          }}>
                            {getTypeIcon(slot.type)} {slot.type.toUpperCase()}
                          </span>
                        </td>
                        <td>{slot.courseCode || '-'}</td>
                        <td>{slot.room}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Weekly Overview */}
          <div className="card">
            <h2>Weekly Overview</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Total Periods</th>
                    <th>Lectures</th>
                    <th>Labs</th>
                    <th>Breaks</th>
                  </tr>
                </thead>
                <tbody>
                  {timetable.map((day, index) => {
                    const lectures = day.slots.filter(slot => slot.type === 'lecture').length
                    const labs = day.slots.filter(slot => slot.type === 'lab').length
                    const breaks = day.slots.filter(slot => slot.type === 'break').length
                    
                    return (
                      <tr key={index}>
                        <td>{day.dayOfWeek}</td>
                        <td>{day.slots.length}</td>
                        <td>{lectures}</td>
                        <td>{labs}</td>
                        <td>{breaks}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {timetable.length === 0 && (
            <div className="card">
              <p>No timetable data found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
