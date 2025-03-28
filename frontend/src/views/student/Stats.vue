<template>
  <div class="card">
    <div class="card-body">
      <h1 class="card-title mb-4">Statistics</h1>
      <div class="row">
        <div class="col-md-4 mb-4">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5 class="card-title">Total Quizzes Taken</h5>
              <h2 class="card-text">12</h2>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5 class="card-title">Average Score</h5>
              <h2 class="card-text">87%</h2>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <h5 class="card-title">Upcoming Quizzes</h5>
              <h2 class="card-text">3</h2>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Subject-wise Performance</h5>
              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Average Score</th>
                      <th>Quizzes Taken</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Mathematics</td>
                      <td>90%</td>
                      <td>4</td>
                    </tr>
                    <tr>
                      <td>Physics</td>
                      <td>85%</td>
                      <td>3</td>
                    </tr>
                    <tr>
                      <td>Chemistry</td>
                      <td>88%</td>
                      <td>3</td>
                    </tr>
                    <tr>
                      <td>Biology</td>
                      <td>92%</td>
                      <td>2</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Recent Performance</h5>
              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Quiz</th>
                      <th>Date</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Chemistry Quiz 1</td>
                      <td>2024-03-15</td>
                      <td>85%</td>
                    </tr>
                    <tr>
                      <td>Biology Quiz 2</td>
                      <td>2024-03-10</td>
                      <td>92%</td>
                    </tr>
                    <tr>
                      <td>Mathematics Quiz 3</td>
                      <td>2024-03-05</td>
                      <td>88%</td>
                    </tr>
                    <tr>
                      <td>Physics Quiz 2</td>
                      <td>2024-02-28</td>
                      <td>82%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>