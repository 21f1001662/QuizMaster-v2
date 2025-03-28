<template>
  <div class="card">
    <div class="card-body">
      <h1 class="card-title mb-4">Upcoming Quizzes</h1>
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Quiz Name</th>
              <th>Subject</th>
              <th>Chapter</th>
              <th>Date & Time</th>
              <th>Duration</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Mathematics Final Exam</td>
              <td>Mathematics</td>
              <td>Calculus</td>
              <td>2024-04-15 10:00 AM</td>
              <td>60 minutes</td>
              <td>
                <button class="btn btn-primary btn-sm">Start Quiz</button>
              </td>
            </tr>
            <tr>
              <td>Physics Mid Term</td>
              <td>Physics</td>
              <td>Mechanics</td>
              <td>2024-04-20 02:00 PM</td>
              <td>45 minutes</td>
              <td>
                <button class="btn btn-primary btn-sm">Start Quiz</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>