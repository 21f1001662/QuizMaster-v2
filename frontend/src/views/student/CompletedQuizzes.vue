<template>
  <div class="card">
    <div class="card-body">
      <h1 class="card-title mb-4">Completed Quizzes</h1>
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Quiz Name</th>
              <th>Subject</th>
              <th>Chapter</th>
              <th>Date Taken</th>
              <th>Score</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Chemistry Quiz 1</td>
              <td>Chemistry</td>
              <td>Atomic Structure</td>
              <td>2024-03-15 11:00 AM</td>
              <td>85%</td>
              <td>
                <button class="btn btn-info btn-sm">View Results</button>
              </td>
            </tr>
            <tr>
              <td>Biology Quiz 2</td>
              <td>Biology</td>
              <td>Cell Biology</td>
              <td>2024-03-10 09:00 AM</td>
              <td>92%</td>
              <td>
                <button class="btn btn-info btn-sm">View Results</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>