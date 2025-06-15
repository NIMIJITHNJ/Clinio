function updateStatus(id, status) {
  fetch("/admins/ajax/update-status/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({ id: id, status: status })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const row = document.getElementById(`appt-${id}`);
      const statusCell = row.querySelector(".status-cell");
      statusCell.innerHTML = `
        <span class="px-2 py-1 rounded text-sm font-semibold
          ${status === 'Approved' ? 'bg-green-100 text-green-800' :
            status === 'Cancelled' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}">
          ${status}
        </span>`;
      row.querySelector(".action-cell").innerHTML = '';
    } else {
      alert("Error: " + data.error);
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const chartElement = document.getElementById('appointmentsPieChart');
  if (!chartElement) return;

  const labels = JSON.parse(chartElement.dataset.labels);
  const values = JSON.parse(chartElement.dataset.values);
  
  new Chart(chartElement, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        label: 'Appointments',
        data: values,
        backgroundColor: [
          '#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#6366F1', '#3B82F6', '#06B6D4'
        ],
        borderWidth: 1,
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true,
        layout: {
          padding: {
            top: 10,
            bottom: 10,
            left: 10,
            right: 10
          }
        },
      plugins: {
        legend: {
          position: 'bottom'
        },
        title: {
          display: true,
          text: 'Appointments Trend (Past 7 Days)'
        }
      },
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const chartElement = document.getElementById('doctorChart');
  if (!chartElement) return;

  const labels = JSON.parse(chartElement.dataset.labels);
  const datasets = JSON.parse(chartElement.dataset.datasets);

  new Chart(chartElement, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: true, text: 'Doctor Availability by Date' }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
});

function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function pollAppointmentUpdates() {
  fetch(recentAppointmentsUrl)
    .then(response => response.json())
    .then(data => {
      console.log("Polled:", data);  // ✅ Check if data is correct

      data.appointments.forEach(appt => {
        const row = document.getElementById(`appt-${appt.id}`);
        if (!row) return;

        const statusCell = row.querySelector(".status-cell");
        const actionCell = row.querySelector(".action-cell");

        // Use regex to strip <span> contents and get plain text
        const currentStatus = statusCell ? statusCell.textContent.trim().toLowerCase() : "";
        const newStatus = appt.status.toLowerCase();

        // Only update if different
        if (currentStatus !== newStatus && statusCell) {
          statusCell.innerHTML = `
            <span class="bg-green-100 text-green-800 text-sm font-semibold px-2 py-1 rounded">
              ${appt.status}
            </span>`;
          if (actionCell) {
            actionCell.innerHTML = '<span class="text-gray-500">-</span>';
          }
        }
      });
    })
    .catch(err => console.error("Polling failed", err));
}

document.addEventListener("DOMContentLoaded", () => {
  setInterval(pollAppointmentUpdates, 10000);
});

